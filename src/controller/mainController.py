# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import range
import time
import os
import webbrowser
import logging
import wx
import widgetUtils
import output
import presenters
import interactors
import views
from vk_api.exceptions import LoginRequired, VkApiError
from requests.exceptions import ConnectionError
from pubsub import pub
from mysc.repeating_timer import RepeatingTimer
from mysc.thread_utils import call_threaded
from mysc import localization
from sessionmanager import session, utils, renderers
from wxUI import (mainWindow, commonMessages)
from wxUI.dialogs import search as searchDialogs
from wxUI.dialogs import timeline
from update import updater
from issueReporter import issueReporter
from . import buffers
from presenters import player
from presenters import longpollthread
from . import selector

log = logging.getLogger("controller.main")

class Controller(object):

	def search(self, tab_name):
		for i in range(0, len(self.buffers)):
			if self.buffers[i].name == tab_name:
				return self.buffers[i]
		return False

	def get_current_buffer(self):
		""" Get the current bufferObject"""
		buffer = self.window.get_current_buffer()
		if hasattr(buffer, "name"):
			buffer = self.search(buffer.name)
			return buffer

	def __init__(self):
		super(Controller, self).__init__()
		log.debug("Starting main controller...")
		self.buffers = []
		player.setup()
		self.window = mainWindow.mainWindow()
		log.debug("Main window created")
		self.window.change_status(_("Ready"))
		self.session = session.sessions[list(session.sessions.keys())[0]]
		self.window.Show()
		self.connect_events()
		self.create_controls()
		call_threaded(updater.do_update, update_type=self.session.settings["general"]["update_channel"])

	def create_buffer(self, buffer_type="baseBuffer", buffer_title="", parent_tab="posts", loadable=False, get_items=False, kwargs={}):
		if not hasattr(buffers, buffer_type):
			raise AttributeError("Specified buffer type does not exist.")
		buffer = getattr(buffers, buffer_type)(**kwargs)
		if loadable:
			buffer.can_get_items = False
		self.buffers.append(buffer)
		self.window.insert_buffer(buffer.tab, buffer_title, self.window.search(parent_tab))
		if get_items:
			call_threaded(buffer.get_items)

	def create_empty_buffer(self, buffer_type="empty", buffer_title="", parent_tab=None, kwargs={}):
		if not hasattr(buffers, buffer_type):
			raise AttributeError("Specified buffer type does not exist.")
		buffer = getattr(buffers, buffer_type)(**kwargs)
		self.buffers.append(buffer)
		if parent_tab == None:
			self.window.add_buffer(buffer.tab, buffer_title)
		else:
			self.window.insert_buffer(buffer.tab, buffer_title, self.window.search(parent_tab))

	def create_controls(self):
		log.debug("Creating controls for the window...")
		pub.sendMessage("create_empty_buffer", buffer_title=_("Posts"), kwargs=dict(parent=self.window.tb, name="posts"))
		pub.sendMessage("create_buffer", buffer_type="baseBuffer", buffer_title=_("Home"), parent_tab="posts", kwargs=dict(parent=self.window.tb, name="home_timeline", session=self.session, composefunc="render_newsfeed_item", endpoint="newsfeed", count=self.session.settings["buffers"]["count_for_wall_buffers"]))
		pub.sendMessage("create_buffer", buffer_type="feedBuffer", buffer_title=_("My wall"), parent_tab="posts", kwargs=dict(parent=self.window.tb, name="me_feed", composefunc="render_status", session=self.session, endpoint="get", parent_endpoint="wall", extended=1, count=self.session.settings["buffers"]["count_for_wall_buffers"]))
		pub.sendMessage("create_empty_buffer", buffer_title=_("Music"), kwargs=dict(parent=self.window.tb, name="audios"))
		pub.sendMessage("create_buffer", buffer_type="audioBuffer", buffer_title=_("My audios"), parent_tab="audios", kwargs=dict(parent=self.window.tb, name="me_audio", composefunc="render_audio", session=self.session, endpoint="get", parent_endpoint="audio"))
		if self.session.settings["vk"]["use_alternative_tokens"] == False:
			pub.sendMessage("create_buffer", buffer_type="audioBuffer", buffer_title=_("Populars"), parent_tab="audios", kwargs=dict(parent=self.window.tb, name="popular_audio", composefunc="render_audio", session=self.session, endpoint="getPopular", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"]))
			pub.sendMessage("create_buffer", buffer_type="audioBuffer", buffer_title=_("Recommendations"), parent_tab="audios", kwargs=dict(parent=self.window.tb, name="recommended_audio", composefunc="render_audio", session=self.session, endpoint="getRecommendations", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"]))
		pub.sendMessage("create_empty_buffer", buffer_type="empty", buffer_title=_("Albums"), parent_tab="audios", kwargs=dict(parent=self.window.tb, name="albums"))
		pub.sendMessage("create_empty_buffer", buffer_title=_("Video"), kwargs=dict(parent=self.window.tb, name="videos"))
		pub.sendMessage("create_buffer", buffer_type="videoBuffer", buffer_title=_("My videos"), parent_tab="videos", kwargs=dict(parent=self.window.tb, name="me_video", composefunc="render_video", session=self.session, endpoint="get", parent_endpoint="video", count=self.session.settings["buffers"]["count_for_video_buffers"]))
		pub.sendMessage("create_empty_buffer", buffer_title=_("Albums"), parent_tab="videos", kwargs=dict(parent=self.window.tb, name="video_albums"))
		pub.sendMessage("create_empty_buffer", buffer_title=_("People"), kwargs=dict(parent=self.window.tb, name="people"))
		pub.sendMessage("create_buffer", buffer_type="peopleBuffer", buffer_title=_("Friends"), parent_tab="people", kwargs=dict(parent=self.window.tb, name="friends_", composefunc="render_person", session=self.session, endpoint="get", parent_endpoint="friends", count=5000, fields="uid, first_name, last_name, last_seen"))
		pub.sendMessage("create_empty_buffer", buffer_title=_("Friendship requests"), parent_tab="people", kwargs=dict(parent=self.window.tb, name="requests"))
		pub.sendMessage("create_buffer", buffer_type="requestsBuffer", buffer_title=_("Pending requests"), parent_tab="requests", kwargs=dict(parent=self.window.tb, name="friend_requests", composefunc="render_person", session=self.session, count=1000))
		pub.sendMessage("create_buffer", buffer_type="requestsBuffer", buffer_title=_("I follow"), parent_tab="requests", kwargs=dict(parent=self.window.tb, name="friend_requests_sent", composefunc="render_person", session=self.session, count=1000, out=1))
		pub.sendMessage("create_empty_buffer", buffer_title=_("Communities"), kwargs=dict(parent=self.window.tb, name="communities"))
		pub.sendMessage("create_empty_buffer", buffer_title=_("Chats"), kwargs=dict(parent=self.window.tb, name="chats"))
		pub.sendMessage("create_empty_buffer", buffer_title=_("Timelines"), kwargs=dict(parent=self.window.tb, name="timelines"))
		self.window.realize()
		self.repeatedUpdate = RepeatingTimer(120, self.update_all_buffers)
		self.repeatedUpdate.start()
		self.readMarker = RepeatingTimer(60, self.mark_as_read)
		self.readMarker.start()

	def connect_events(self):
		log.debug("Connecting events to responses...")
		pub.subscribe(self.in_post, "posted")
		pub.subscribe(self.download, "download-file")
		pub.subscribe(self.play_audio, "play-audio")
		pub.subscribe(self.play_audios, "play-audios")
		pub.subscribe(self.view_post, "open-post")
		pub.subscribe(self.update_status_bar, "update-status-bar")
		pub.subscribe(self.chat_from_id, "new-chat")
		pub.subscribe(self.authorisation_failed, "authorisation-failed")
		pub.subscribe(self.user_profile, "user-profile")
		pub.subscribe(self.user_online, "user-online")
		pub.subscribe(self.user_offline, "user-offline")
		pub.subscribe(self.notify, "notify")
		pub.subscribe(self.handle_longpoll_read_timeout, "longpoll-read-timeout")
		pub.subscribe(self.create_buffer, "create_buffer")
		pub.subscribe(self.create_empty_buffer, "create_empty_buffer")
		pub.subscribe(self.user_typing, "user-typing")
		widgetUtils.connect_event(self.window, widgetUtils.CLOSE_EVENT, self.exit)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.update_buffer, menuitem=self.window.update_buffer)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.check_for_updates, menuitem=self.window.check_for_updates)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.window.about_dialog, menuitem=self.window.about)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.search_audios, menuitem=self.window.search_audios)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.search_videos, menuitem=self.window.search_videos)
		widgetUtils.connect_event(self.window, widgetUtils.MENU,self.remove_buffer, menuitem=self.window.remove_buffer_)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.get_more_items, menuitem=self.window.load_previous_items)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.changelog, menuitem=self.window.changelog)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.configuration, menuitem=self.window.settings_dialog)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.new_timeline, menuitem=self.window.timeline)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.create_audio_album, menuitem=self.window.audio_album)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.delete_audio_album, menuitem=self.window.delete_audio_album)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.create_video_album, menuitem=self.window.video_album)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.delete_video_album, menuitem=self.window.delete_video_album)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.check_documentation, menuitem=self.window.documentation)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_pause, menuitem=self.window.player_play)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_next, menuitem=self.window.player_next)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_previous, menuitem=self.window.player_previous)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_all, menuitem=self.window.player_play_all)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_stop, menuitem=self.window.player_stop)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_volume_down, menuitem=self.window.player_volume_down)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_volume_up, menuitem=self.window.player_volume_up)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_mute, menuitem=self.window.player_mute)
		pub.subscribe(self.get_chat, "order-sent-message")
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.view_my_profile, menuitem=self.window.view_profile)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.view_my_profile_in_browser, menuitem=self.window.open_in_browser)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.set_status, menuitem=self.window.set_status)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.on_report_error, menuitem=self.window.report)

	def disconnect_events(self):
		log.debug("Disconnecting some events...")
		pub.unsubscribe(self.in_post, "posted")
		pub.unsubscribe(self.download, "download-file")
		pub.unsubscribe(self.play_audio, "play-audio")
		pub.unsubscribe(self.authorisation_failed, "authorisation-failed")
		pub.unsubscribe(self.play_audios, "play-audios")
		pub.unsubscribe(self.view_post, "open-post")
		pub.unsubscribe(self.update_status_bar, "update-status-bar")
		pub.unsubscribe(self.user_online, "user-online")
		pub.unsubscribe(self.user_offline, "user-offline")
		pub.unsubscribe(self.notify, "notify")

	def authorisation_failed(self):
		commonMessages.bad_authorisation()

	def login(self):
		self.window.change_status(_("Logging in VK"))
		self.session.login()
		self.window.change_status(_("Ready"))
		for i in self.buffers:
			if hasattr(i, "get_items"):
				# Translators: {0} will be replaced with the name of a buffer.
				self.window.change_status(_("Loading items for {0}").format(i.name,))
				i.get_items()
		self.window.change_status(_("Ready"))
		self.create_unread_messages()
		self.status_setter = RepeatingTimer(280, self.set_online)
		self.status_setter.start()
		self.set_online(notify=True)
		self.get_audio_albums(self.session.user_id)
		self.get_video_albums(self.session.user_id)
		self.get_communities(self.session.user_id)
		self.create_longpoll_thread()

	def create_longpoll_thread(self, notify=False):
		try:
			self.longpoll = longpollthread.worker(self.session)
			self.longpoll.start()
			if notify:
				self.notify(message=_("Chat server reconnected"))
		except ConnectionError:
			pub.sendMessage("longpoll-read-timeout")

	def in_post(self, buffer):
		buffer = self.search(buffer)
		buffer.get_items()
		buffer = self.search("home_timeline")
		buffer.get_items()

	def update_all_buffers(self):
		log.debug("Updating buffers...")
		self.get_audio_albums(self.session.user_id, create_buffers=False)
		self.get_video_albums(self.session.user_id, create_buffers=False)
		for i in self.buffers:
			if hasattr(i, "get_items"):
				i.get_items()
				log.debug("Updated %s" % (i.name))

	def download(self, url, filename):
		log.debug("downloading %s URL to %s filename" % (url, filename,))
		call_threaded(utils.download_file, url, filename, self.window)

	def play_audio(self, audio_object):
		# Restricted audios does not include an URL paramether.
		# Restriction can be due to licensed content to unauthorized countries.
		if "url" in audio_object and audio_object["url"] =="":
			self.notify(message=_("This file could not be played because it is not allowed in your country"))
			return
		call_threaded(player.player.play, audio_object)

	def play_audios(self, audios):
		player.player.play_all(audios, shuffle=self.window.player_shuffle.IsChecked())

	def view_post(self, post_object, controller_):
		p = getattr(presenters, controller_+"Presenter")(session=self.session, postObject=post_object, interactor=getattr(interactors, controller_+"Interactor")(), view=getattr(views, controller_)())

	def exit(self, *args, **kwargs):
		log.debug("Receibed an exit signal. closing...")
		self.set_offline()
		self.disconnect_events()
		self.window.Destroy()
		wx.GetApp().ExitMainLoop()

	def update_buffer(self, *args, **kwargs):
		b = self.get_current_buffer()
		b.get_items()

	def get_more_items(self, *args, **kwargs):
		b = self.get_current_buffer()
		b.get_more_items()

	def check_for_updates(self, *args, **kwargs):
		update = updater.do_update(update_type=self.session.settings["general"]["update_channel"])
		if update == False:
			commonMessages.no_update_available()

	def search_audios(self, *args, **kwargs):
		dlg = searchDialogs.searchAudioDialog()
		if dlg.get_response() == widgetUtils.OK:
			q = dlg.get("term")
			newbuff = buffers.audioBuffer(parent=self.window.tb, name="{0}_audiosearch".format(q,), session=self.session, composefunc="render_audio", parent_endpoint="audio", endpoint="search", q=q)
			self.buffers.append(newbuff)
			call_threaded(newbuff.get_items)
			# Translators: {0} will be replaced with the search term.
			self.window.insert_buffer(newbuff.tab, _("Search for {0}").format(q,), self.window.search("audios"))

	def search_videos(self, *args, **kwargs):
		dlg = searchDialogs.searchVideoDialog()
		if dlg.get_response() == widgetUtils.OK:
			params = {}
			params["q"] = dlg.get("term").encode("utf-8")
			params["count"] = 200
			hd = dlg.get_checkable("hd")
			if hd != 0:
				params["hd"] = 1
			params["adult"] = dlg.get_checkable("safe_search")
			params["sort"] = dlg.get_sort_order()
			params["filters"] = "youtube, vimeo, short, long"
			newbuff = buffers.videoBuffer(parent=self.window.tb, name="{0}_videosearch".format(params["q"],), session=self.session, composefunc="render_video", parent_endpoint="video", endpoint="search", **params)
			self.buffers.append(newbuff)
			call_threaded(newbuff.get_items)
			# Translators: {0} will be replaced with the search term.
			self.window.insert_buffer(newbuff.tab, _("Search for {0}").format(params["q"],), self.window.search("videos"))

	def update_status_bar(self, status):
		self.window.change_status(status)

	def remove_buffer(self, event, mandatory=False, *args, **kwargs):
		buffer = self.get_current_buffer()
		buff = self.window.search(buffer.name)
		answer = buffer.remove_buffer(mandatory)
		if answer == False:
			return
		self.window.remove_buffer(buff)
		self.buffers.remove(buffer)
		del buffer

	def changelog(self, *args, **kwargs):
		os.chdir("documentation")
		webbrowser.open("changelog.html")
		os.chdir("../")

	def configuration(self, *args, **kwargs):
		""" Opens the global settings dialogue."""
		presenter = presenters.configurationPresenter(session=self.session, view=views.configurationDialog(title=_("Preferences")), interactor=interactors.configurationInteractor())

	def new_timeline(self, *args, **kwargs):
		b = self.get_current_buffer()
		# If executing this method from an empty buffer we should get the newsfeed buffer.
		if not hasattr(b, "get_users"):
			b = self.search("home_timeline")
		# Get a list of (id, user) objects.
		d = []
		for i in self.session.db["users"]:
			d.append((i, self.session.get_user(i)["user1_gen"]))
		# Do the same for communities.
		for i in self.session.db["groups"]:
			d.append((-i, self.session.get_user(-i)["user1_nom"]))
		a = timeline.timelineDialog([i[1] for i in d])
		if a.get_response() == widgetUtils.OK:
			user = a.get_user()
			buffertype = a.get_buffer_type()
			user_id = ""
			for i in d:
				if i[1] == user:
					user_id = i[0]
			if user_id == "":
				user_data = self.session.vk.client.utils.resolveScreenName(screen_name=user)
				if type(user_data) == list:
					commonMessages.no_user_exist()
					return
				user_id = user_data["object_id"]
			if buffertype == "audio":
				buffer = buffers.audioBuffer(parent=self.window.tb, name="{0}_audio".format(user_id,), composefunc="render_audio", session=self.session, create_tab=False, endpoint="get", parent_endpoint="audio", owner_id=user_id)
				user = self.session.get_user(user_id, key="user1")
				name_ = _("{user1_nom}'s audios").format(**user)
			elif buffertype == "wall":
				buffer = buffers.feedBuffer(parent=self.window.tb, name="{0}_feed".format(user_id,), composefunc="render_status", session=self.session, create_tab=False, endpoint="get", parent_endpoint="wall", extended=1, count=self.session.settings["buffers"]["count_for_wall_buffers"],  owner_id=user_id)
				user = self.session.get_user(user_id, key="user1")
				name_ = _("{user1_nom}'s posts").format(**user)
			elif buffertype == "friends":
				buffer = buffers.peopleBuffer(parent=self.window.tb, name="friends_{0}".format(user_id,), composefunc="render_person", session=self.session, create_tab=False, endpoint="get", parent_endpoint="friends", count=5000, fields="uid, first_name, last_name, last_seen", user_id=user_id)
				user = self.session.get_user(user_id, key="user1")
				name_ = _("{user1_nom}'s friends").format(**user)
			wx.CallAfter(self.complete_buffer_creation, buffer=buffer, name_=name_, position=self.window.search("timelines"))

	def complete_buffer_creation(self, buffer, name_, position):
		answer = buffer.get_items()
		if answer is not True:
			commonMessages.show_error_code(answer)
			return
		self.buffers.append(buffer)
		self.window.insert_buffer(buffer.tab, name_, position)

	def search_chat_buffer(self, user_id):
		for i in self.buffers:
			if "_messages" in i.name:
				if "peer_id" in i.kwargs and i.kwargs["peer_id"] == user_id: return i
		return None

	def chat_from_id(self, user_id, setfocus=True, unread=False):
		b = self.search_chat_buffer(user_id)
		if b != None:
			pos = self.window.search(b.name)
			if setfocus:
				self.window.change_buffer(pos)
				return b.tab.text.SetFocus()
			return
		# Get name based in the ID.
		# for users.
		if user_id > 0 and user_id < 2000000000:
			user = self.session.get_user(user_id, key="user1")
			name = _("Chat with {user1_nom}").format(**user)
		elif user_id > 2000000000:
			chat = self.session.vk.client.messages.getChat(chat_id=user_id-2000000000)
			name = _("Chat in {chat_name}").format(chat_name=chat["title"],)
		wx.CallAfter(pub.sendMessage, "create_buffer", buffer_type="chatBuffer", buffer_title=name, parent_tab="chats", get_items=True, kwargs=dict(parent=self.window.tb, name="{0}_messages".format(user_id,), composefunc="render_message", session=self.session, count=200,  peer_id=user_id, rev=0, extended=True, fields="id, user_id, date, read_state, out, body, attachments, deleted"))
#		if setfocus:
#			pos = self.window.search(buffer.name)
#			self.window.change_buffer(pos)
#		call_threaded(buffer.get_items, unread=unread)
#		if setfocus: buffer.tab.text.SetFocus()
#		return True

	def user_online(self, event):
		if self.session.settings["chat"]["notify_online"] == False:
			return
		user_name = self.session.get_user(event.user_id)
		msg = _("{user1_nom} is online.").format(**user_name)
		sound = "friend_online.ogg"
		self.notify(msg, sound, self.session.settings["chat"]["notifications"])

	def user_offline(self, event):
		if self.session.settings["chat"]["notify_offline"] == False:
			return
		user_name = self.session.get_user(event.user_id)
		msg = _("{user1_nom} is offline.").format(**user_name)
		sound = "friend_offline.ogg"
		self.notify(msg, sound, self.session.settings["chat"]["notifications"])

	def user_typing(self, obj):
		buffer = self.search_chat_buffer(obj.user_id)
		if buffer != None and buffer == self.get_current_buffer():
			user = self.session.get_user(obj.user_id)
			output.speak(_("{user1_nom} is typing...").format(**user))

	def get_chat(self, obj=None):
		""" Searches or creates a chat buffer with the id of the user that is sending or receiving a message.
			obj vk_api.longpoll.EventType: an event wich defines some data from the vk's long poll server."""
		message = {}
		uid = obj.peer_id
		buffer = self.search_chat_buffer(uid)
		if obj.from_me:
			message.update(out=0)
		# If there is no buffer, we must create one in a wxThread so it will not crash.
		if buffer == None:
			wx.CallAfter(self.chat_from_id, uid, setfocus=self.session.settings["chat"]["automove_to_conversations"], unread=True)
			self.session.soundplayer.play("conversation_opened.ogg")
			return
		# If the chat already exists, let's create a dictionary wich will contains data of the received message.
		message.update(id=obj.message_id, user_id=uid, date=obj.timestamp, body=obj.text, attachments=obj.attachments)
		# if attachments is true, let's request for the full message with attachments formatted in a better way.
		# Todo: code improvements. We shouldn't need to request the same message again just for these attachments.
		if len(message["attachments"]) != 0:
			message_ids = message["id"]
			results = self.session.vk.client.messages.getById(message_ids=message_ids)
			message = results["items"][0]
			message.update(read_state=0)
		if obj.from_me:
			message["from_id"] = self.session.user_id
		else:
			message["from_id"] = obj.user_id
		data = [message]
		# Let's add this to the buffer.
		# ToDo: Clean this code and test how is the database working with this set to True.
		num = self.session.order_buffer(buffer.name, data, True)
		buffer.insert(self.session.db[buffer.name]["items"][-1], False)
		self.session.soundplayer.play("message_received.ogg")
		# Check if we have to read the message aloud
		if buffer == self.get_current_buffer():
			rendered_message = renderers.render_message(message, self.session)
			output.speak(rendered_message[0])

	def set_online(self, notify=False):
		try:
			r = self.session.vk.client.account.setOnline()
		except:
			log.error("Error in setting online for the current user")
		if notify:
			self.window.notify("Socializer", "online now!")

	def set_offline(self):
		try:
			r = self.session.vk.client.account.setOffline()
		except:
			log.error("Error in setting offline status for the current user")

	def create_unread_messages(self):
		if self.session.settings["chat"]["open_unread_conversations"] == False:
			return
		try:
			log.debug("Getting possible unread messages.")
			msgs = self.session.vk.client.messages.getDialogs(count=200, unread=True)
		except VkApiError as ex:
			if ex.code == 6:
				log.exception("Something went wrong when getting messages. Waiting a second to retry")
		for i in msgs["items"]:
			call_threaded(self.chat_from_id, i["message"]["user_id"], setfocus=False, unread=True)

	def mark_as_read(self):
		for i in self.buffers:
			if hasattr(i, "reads") and len(i.reads) != 0:
				response = self.session.vk.client.messages.markAsRead(peer_id=i.kwargs["peer_id"])
				i.clear_reads()
				i.reads = []
				time.sleep(1)

	def get_audio_albums(self, user_id=None, create_buffers=True):
		if self.session.settings["load_at_startup"]["audio_albums"] == False:
			return
		log.debug("Create audio albums...")
		if self.session.settings["vk"]["use_alternative_tokens"]:
			albums = self.session.vk.client_audio.get_albums(owner_id=user_id)
		else:
			albums = self.session.vk.client.audio.getPlaylists(owner_id=user_id)
			albums = albums["items"]
		self.session.audio_albums = albums
		if create_buffers:
			for i in albums:
				wx.CallAfter(pub.sendMessage, "create_buffer", buffer_type="audioAlbum", buffer_title=_("Album: {0}").format(i["title"],), parent_tab="albums", loadable=True, kwargs=dict(parent=self.window.tb, name="{0}_audio_album".format(i["id"],), composefunc="render_audio", session=self.session, endpoint="get", parent_endpoint="audio", owner_id=user_id, album_id=i["id"]))
				time.sleep(0.6)

	def get_video_albums(self, user_id=None, create_buffers=True):
		if self.session.settings["load_at_startup"]["video_albums"] == False:
			return
		log.debug("Create video  albums...")
		albums = self.session.vk.client.video.getAlbums(owner_id=user_id)
		self.session.video_albums = albums["items"]
		if create_buffers:
			for i in albums["items"]:
				wx.CallAfter(pub.sendMessage, "create_buffer", buffer_type="videoAlbum", buffer_title=_("Album: {0}").format(i["title"],), parent_tab="video_albums", loadable=True, kwargs=dict(parent=self.window.tb, name="{0}_video_album".format(i["id"],), composefunc="render_video", session=self.session, endpoint="get", parent_endpoint="video", count=self.session.settings["buffers"]["count_for_video_buffers"], user_id=user_id, album_id=i["id"]))
				time.sleep(0.15)

	def get_communities(self, user_id=None, create_buffers=True):
		if self.session.settings["vk"]["invited_to_group"] == False:
			socializer_group = self.session.vk.client.groups.getById(group_ids="175825000")[0]
			if socializer_group["is_member"] ==False:
				d = commonMessages.join_group()
				self.session.settings["vk"]["invited_to_group"] = True
				self.session.settings.write()
				if d == widgetUtils.YES:
					result = self.session.vk.client.groups.join(group_id=socializer_group["id"])
					if result == 1:
						commonMessages.group_joined()
					else:
						log.error("Invalid result when joining the Socializer's group: %d" % (result))
		if self.session.settings["load_at_startup"]["communities"] == False:
			return
		log.debug("Create community buffers...")
		groups= self.session.vk.client.groups.get(user_id=user_id, extended=1, fields="city, country, place, description, wiki_page, members_count, counters, start_date, finish_date, can_post, can_see_all_posts, activity, status, contacts, links, fixed_post, verified, site, can_create_topic", count=1000)
		self.session.groups=groups["items"]
		# Let's feed the local database cache with new groups coming from here.
		data= dict(profiles=[], groups=groups["items"])
		self.session.process_usernames(data)
		if create_buffers:
			for i in groups["items"]:
				wx.CallAfter(pub.sendMessage, "create_buffer", buffer_type="communityBuffer", buffer_title=i["name"], parent_tab="communities", loadable=True, kwargs=dict(parent=self.window.tb, name="{0}_community".format(i["id"],), composefunc="render_status", session=self.session, endpoint="get", parent_endpoint="wall", count=self.session.settings["buffers"]["count_for_wall_buffers"], owner_id=-1*i["id"]))
				time.sleep(0.15)

	def create_audio_album(self, *args, **kwargs):
		d = creation.audio_album()
		if d.get_response() == widgetUtils.OK and d.get("title") != "":
			response = self.session.vk.client.audio.addAlbum(title=d.get("title"))
			if ("album_id" in response) == False: return
			album_id = response["album_id"]
			buffer = buffers.audioAlbum(parent=self.window.tb, name="{0}_audio_album".format(album_id,), composefunc="render_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"], user_id=self.session.user_id, album_id=album_id)
			buffer.can_get_items = False
			# Translators: {0} will be replaced with an audio album's title.
			name_ = _("Album: {0}").format(d.get("title"),)
			self.buffers.append(buffer)
			self.window.insert_buffer(buffer.tab, name_, self.window.search("albums"))
			buffer.get_items()
			self.session.audio_albums = self.session.vk.client.audio.getAlbums(owner_id=self.session.user_id)["items"]

	def delete_audio_album(self, *args, **kwargs):
		if len(self.session.audio_albums) == 0:
			return commonMessages.no_audio_albums()
		answer = selector.album(_("Select the album you want to delete"), self.session)
		if answer.item == None:
			return
		response = commonMessages.delete_audio_album()
		if response != widgetUtils.YES: return
		removal = self.session.vk.client.audio.deleteAlbum(album_id=answer.item)
		buffer = self.search("{0}_audio_album".format(answer.item,))
		buff = self.window.search(buffer.name)
		self.window.remove_buffer(buff)
		self.buffers.remove(buffer)
		del buffer
		self.session.audio_albums = self.session.vk.client.audio.getAlbums(owner_id=self.session.user_id)["items"]

	def create_video_album(self, *args, **kwargs):
		d = creation.audio_album()
		if d.get_response() == widgetUtils.OK and d.get("title") != "":
			response = self.session.vk.client.video.addAlbum(title=d.get("title"))
			if ("album_id" in response) == False: return
			album_id = response["album_id"]
			buffer = buffers.videoAlbum(parent=self.window.tb, name="{0}_video_album".format(album_id,), composefunc="render_video", session=self.session, endpoint="get", parent_endpoint="video", count=self.session.settings["buffers"]["count_for_video_buffers"], user_id=self.session.user_id, album_id=album_id)
			buffer.can_get_items = False
			# Translators: {0} will be replaced with a video  album's title.
			name_ = _("Album: {0}").format(d.get("title"),)
			self.buffers.append(buffer)
			self.window.insert_buffer(buffer.tab, name_, self.window.search("video_albums"))
			buffer.get_items()
			self.session.video_albums = self.session.vk.client.video.getAlbums(owner_id=self.session.user_id)["items"]

	def delete_video_album(self, *args, **kwargs):
		if len(self.session.video_albums) == 0:
			return commonMessages.no_video_albums()
		answer = selector.album(_("Select the album you want to delete"), self.session, "video_albums")
		if answer.item == None:
			return
		response = commonMessages.delete_audio_album()
		if response != widgetUtils.YES: return
		removal = self.session.vk.client.video.deleteAlbum(album_id=answer.item)
		buffer = self.search("{0}_video_album".format(answer.item,))
		buff = self.window.search(buffer.name)
		self.window.remove_buffer(buff)
		self.buffers.remove(buffer)
		del buffer
		self.session.video_albums = self.session.vk.client.video.getAlbums(owner_id=self.session.user_id)["items"]

	def check_documentation(self, *args, **kwargs):
		lang = localization.get("documentation")
		os.chdir("documentation/%s" % (lang,))
		webbrowser.open("manual.html")
		os.chdir("../../")

	def menu_play_pause(self, *args, **kwargs):
		if player.player.check_is_playing() != False:
			return player.player.pause()
		b = self.get_current_buffer()
		if hasattr(b, "play_next"):
			b.play_audio()
		else:
			b = self.search("me_audio")
			b.play_audio()

	def menu_play_next(self, *args, **kwargs):
		b = self.get_current_buffer()
		if hasattr(b, "play_next"):
			b.play_next()
		else:
			self.search("me_audio").play_next()

	def menu_play_previous(self, *args, **kwargs):
		b = self.get_current_buffer()
		if hasattr(b, "play_previous"):
			b.play_previous()
		else:
			self.search("me_audio").play_previous()

	def menu_play_all(self, *args, **kwargs):
		b = self.get_current_buffer()
		if hasattr(b, "play_all"):
			b.play_all()
		else:
			self.search("me_audio").play_all()

	def menu_stop(self, *args, **kwargs):
		player.player.stop()

	def menu_volume_down(self, *args, **kwargs):
		player.player.volume = player.player.volume-5

	def menu_volume_up(self, *args, **kwargs):
		player.player.volume = player.player.volume+5

	def menu_mute(self, *args, **kwargs):
		player.player.volume = 0

	def user_profile(self, person):
		p = presenters.userProfilePresenter(session=self.session, user_id=person, view=views.userProfileDialog(), interactor=interactors.userProfileInteractor())

	def view_my_profile(self, *args, **kwargs):
		self.user_profile(self.session.user_id)

	def view_my_profile_in_browser(self, *args, **kwargs):
		webbrowser.open_new_tab("https://vk.com/id{id}".format(id=self.session.user_id,))

	def notify(self, message="", sound="", type="native"):
		if type == "native":
			wx.CallAfter(self.window.notify, _("Socializer"), message)
		else:
			if sound != "":
				self.session.soundplayer.play(sound)
			if message != "":
				output.speak(message)

	def handle_longpoll_read_timeout(self):
		if hasattr(self, "longpoll"):
			self.notify(message=_("Chat disconnected. Trying to connect in 60 seconds"))
		time.sleep(60)
		if hasattr(self, "longpoll"):
			del self.longpoll
		self.create_longpoll_thread(notify=True)

	def set_status(self, *args, **kwargs):
		dlg = wx.TextEntryDialog(self.window, _("Write your status message"), _("Set status"))
		if dlg.ShowModal() == widgetUtils.OK:
			result = dlg.GetValue()
			info = self.session.vk.client.account.saveProfileInfo(status=result)
			commonMessages.updated_status()
		dlg.Destroy()

	def on_report_error(self, *args, **kwargs):
		r = issueReporter.reportBug()