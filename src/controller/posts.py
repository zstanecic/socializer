# -*- coding: utf-8 -*-
import os
import arrow
import messages
import languageHandler
import widgetUtils
import output
import wx
import webbrowser
import utils
from sessionmanager import session # We'll use some functions from there
from pubsub import pub
from wxUI.dialogs import postDialogs, urlList
from extra import SpellChecker, translator
from mysc.thread_utils import call_threaded
from wxUI import menus

def get_user(id, profiles):
	""" Returns an user name and last name  based in the id receibed."""
	for i in profiles:
		if i["id"] == id:
			return u"{0} {1}".format(i["first_name"], i["last_name"])
	return _(u"Unknown username")

def add_attachment(attachment):
	msg = u""
	tpe = ""
	if attachment["type"] == "link":
		msg = u"{0}: {1}".format(attachment["link"]["title"], attachment["link"]["url"])
		tpe = _(u"Link")
	elif attachment["type"] == "photo":
		tpe = _(u"Photo")
		msg = attachment["photo"]["text"]
		if msg == "":
			msg = "photo with no description available"
	elif attachment["type"] == "video":
		msg = u"{0}".format(attachment["video"]["title"],)
		tpe = _(u"Video")
	return [tpe, msg]

def get_message(status):
	message = ""
	message = utils.clean_text(status["text"])
	if status.has_key("attachments"):
		print status["attachments"]
#		message = message+session.add_attachment(status["attachment"])
	return message

class postController(object):
	def __init__(self, session, postObject):
		super(postController, self).__init__()
		self.session = session
		self.post = postObject
		# Posts from newsfeed contains this source_id instead from_id in walls. Also it uses post_id and walls use just id.
		if self.post.has_key("source_id"):
			self.user_identifier = "source_id"
			self.post_identifier = "post_id"
		else:
			self.user_identifier = "from_id"
			self.post_identifier = "id"
		self.dialog = postDialogs.post()
#		self.dialog.comments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.show_comment)
		widgetUtils.connect_event(self.dialog.like, widgetUtils.BUTTON_PRESSED, self.post_like)
		widgetUtils.connect_event(self.dialog.comment, widgetUtils.BUTTON_PRESSED, self.add_comment)
		widgetUtils.connect_event(self.dialog.tools, widgetUtils.BUTTON_PRESSED, self.show_tools_menu)
		widgetUtils.connect_event(self.dialog.repost, widgetUtils.BUTTON_PRESSED, self.post_repost)
		self.dialog.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu, self.dialog.comments.list)
		self.dialog.Bind(wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key, self.dialog.comments.list)
		call_threaded(self.load_all_components)
		print self.post.keys()
		self.attachments = []

	def get_comments(self):
		user = self.post[self.user_identifier]
		id = self.post[self.post_identifier]
		self.comments = self.session.vk.client.wall.getComments(owner_id=user, post_id=id, need_likes=1, count=100, extended=1, preview_length=0)
		comments_ = []
		for i in self.comments["items"]:
			from_ = get_user(i["from_id"], self.comments["profiles"])
			if len(i["text"]) > 140:
				text = i["text"][:141]
			else:
				text = i["text"]
			original_date = arrow.get(i["date"])
			created_at = original_date.humanize(locale=languageHandler.getLanguage())
			likes = str(i["likes"]["count"])
			comments_.append((from_, text, created_at, likes))
		self.dialog.insert_comments(comments_)

	def get_post_information(self):
		from_ = self.session.get_user_name(self.post[self.user_identifier])
		if self.post.has_key("copy_history"):
			title = _(u"repost from {0}").format(from_,)
		else:
			title = _(u"Post from {0}").format(from_,)
		self.dialog.set_title(title)
		message = u""
		message = get_message(self.post)
		self.get_attachments(self.post)
		if self.post.has_key("copy_history"):
			nm = u"\n"
			for i in self.post["copy_history"]:
				nm += u"{0}: {1}\n\n".format(self.session.get_user_name(i["from_id"]),  get_message(i))
				self.get_attachments(i)
			message += nm
		self.dialog.set_post(message)

	def get_attachments(self, post):
		attachments = []
		if post.has_key("attachments"):
			for i in post["attachments"]:
				attachments.append(add_attachment(i))
		if len(attachments) > 0:
			self.attachments.extend(attachments)
		if len(self.attachments) > 0:
			self.dialog.attachments.list.Enable(True)
			self.dialog.insert_attachments(self.attachments)

	def load_all_components(self):
		self.get_post_information()
		self.get_likes()
		self.get_reposts()
		self.get_comments()
		if self.post["comments"]["can_post"] == 0:
			self.dialog.disable("add_comment")
		if self.post["likes"]["can_like"] == 0 and self.post["likes"]["user_likes"] == 0:
			self.dialog.disable("like")
		elif self.post["likes"]["user_likes"] == 1:
			self.dialog.set("like", _(u"&Dislike"))
		if self.post["likes"]["can_publish"] == 0:
			self.dialog.disable("repost")

	def post_like(self, *args, **kwargs):
		if self.post.has_key("owner_id") == False:
			user = int(self.post[self.user_identifier])
		else:
			user = int(self.post["owner_id"])
		id = int(self.post[self.post_identifier])
		if self.post.has_key("type"):
			type_ = self.post["type"]
		else:
			type_ = "post"
		if self.dialog.get("like") == _(u"&Dislike"):
			l = self.session.vk.client.likes.delete(owner_id=user, item_id=id, type=type_)
			output.speak(_(u"You don't like this"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 2
			self.get_likes()
			self.dialog.set("like", _(u"&Like"))
		else:
			l = self.session.vk.client.likes.add(owner_id=user, item_id=id, type=type_)
			output.speak(_(u"You liked this"))
			self.dialog.set("like", _(u"&Dislike"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 1
			self.get_likes()

	def post_repost(self, *args, **kwargs):
		object_id = "wall{0}_{1}".format(self.post[self.user_identifier], self.post[self.post_identifier])
		p = messages.post(title=_(u"Repost"), caption=_(u"Add your comment here"), text="")
		if p.message.get_response() == widgetUtils.OK:
			msg = p.message.get_text().encode("utf-8")
			self.session.vk.client.wall.repost(object=object_id, message=msg)

	def get_likes(self):
		self.dialog.set_likes(self.post["likes"]["count"])

	def get_reposts(self):
		self.dialog.set_shares(self.post["reposts"]["count"])

	def add_comment(self, *args, **kwargs):
		comment = messages.comment(title=_(u"Add a comment"), caption="", text="")
		if comment.message.get_response() == widgetUtils.OK:
			msg = comment.message.get_text().encode("utf-8")
			try:
				user = self.post[self.user_identifier]
				id = self.post[self.post_identifier]
				self.session.vk.client.wall.addComment(owner_id=user, post_id=id, text=msg)
				output.speak(_(u"You've posted a comment"))
				if self.comments["count"] < 100:
					self.clear_comments_list()
					self.get_comments()
			except Exception as msg:
				print msg

	def clear_comments_list(self):
		self.dialog.comments.clear()

	def show_comment(self, *args, **kwargs):
		c = comment(self.session, self.comments["data"][self.dialog.comments.get_selected()])
		c.dialog.get_response()

	def show_menu(self, *args, **kwargs):
		if self.dialog.comments.get_count() == 0: return
		menu = menus.commentMenu()
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.show_comment, menuitem=menu.open)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.comment_like, menuitem=menu.like)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.comment_unlike, menuitem=menu.unlike)
		self.dialog.PopupMenu(menu, self.dialog.comments.list.GetPosition())

	def show_menu_by_key(self, ev):
		if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
			self.show_menu()

	def show_tools_menu(self, *args, **kwargs):
		menu = menus.toolsMenu()
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.open_url, menuitem=menu.url)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.translate, menuitem=menu.translate)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.spellcheck, menuitem=menu.CheckSpelling)
		self.dialog.PopupMenu(menu, self.dialog.tools.GetPosition())

	def comment_like(self, *args, **kwargs):
		comment_id = self.comments["data"][self.dialog.comments.get_selected()]["id"]
		self.session.like(comment_id)
		output.speak(_(u"You do like this comment"))

	def comment_unlike(self, *args, **kwargs):
		comment_id = self.comments["data"][self.dialog.comments.get_selected()]["id"]
		self.session.unlike(comment_id)
		output.speak(_(u"You don't like this comment"))

	def translate(self, *args, **kwargs):
		dlg = translator.gui.translateDialog()
		if dlg.get_response() == widgetUtils.OK:
			text_to_translate = self.dialog.post_view.GetValue().encode("utf-8")
			source = [x[0] for x in translator.translator.available_languages()][dlg.get("source_lang")]
			dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
			msg = translator.translator.translate(text_to_translate, source, dest)
			self.dialog.post_view.ChangeValue(msg)
			output.speak(_(u"Translated"))
		else:
			return

	def spellcheck(self, *args, **kwargs):
		text = self.dialog.post_view.GetValue()
		checker = SpellChecker.spellchecker.spellChecker(text, "")
		if hasattr(checker, "fixed_text"):
			self.dialog.post_view.ChangeValue(checker.fixed_text)

	def open_url(self, *args, **kwargs):
		text = self.dialog.post_view.GetValue()
		urls = find_urls(text)
		url = None
		if len(urls) == 0: return
		if len(urls) == 1:
			url = urls[0]
		elif len(urls) > 1:
			url_list = urlList.urlList()
			url_list.populate_list(urls)
			if url_list.get_response() == widgetUtils.OK:
				url = urls[url_list.get_item()]
		if url != None:
			output.speak(_(u"Opening URL..."), True)
			webbrowser.open_new_tab(url)

class comment(object):
	def __init__(self, session, comment_object):
		super(comment, self).__init__()
		self.session = session
		self.comment = comment_object
		self.dialog = postDialogs.comment()
		from_ = self.comment["from"]["name"]
		message = self.comment["message"]
		original_date = arrow.get(self.comment["created_time"], "YYYY-MM-DTHH:m:sZ", locale="en")
		created_at = original_date.humanize(locale=languageHandler.getLanguage())
		self.dialog.set_post(message)
		self.dialog.set_title(_(u"Comment from {0}").format(from_,))
		widgetUtils.connect_event(self.dialog.like, widgetUtils.BUTTON_PRESSED, self.post_like)
		call_threaded(self.get_likes)

	def get_likes(self):
		self.likes = self.session.fb.client.get_connections(id=self.comment["id"], connection_name="likes", summary=True)
		self.dialog.set_likes(self.likes["summary"]["total_count"])

	def post_like(self, *args, **kwargs):
		lk = self.session.like(self.comment["id"])
		self.get_likes()

class audio(postController):
	def __init__(self, session, postObject):
		self.added_audios = {}
		self.session = session
		self.post = postObject
		self.dialog = postDialogs.audio()
		widgetUtils.connect_event(self.dialog.list, widgetUtils.LISTBOX_CHANGED, self.handle_changes)
		self.load_audios()
		self.fill_information(0)
		widgetUtils.connect_event(self.dialog.download, widgetUtils.BUTTON_PRESSED, self.download)
		widgetUtils.connect_event(self.dialog.play, widgetUtils.BUTTON_PRESSED, self.play)
		widgetUtils.connect_event(self.dialog.add, widgetUtils.BUTTON_PRESSED, self.add_to_library)
		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_from_library)

	def add_to_library(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		args = {}
		args["audio_id"] = post["id"]
		if post.has_key("album_id"):
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		audio = self.session.vk.client.audio.add(**args)
		if audio != None and int(audio) > 21:
			self.added_audios[post["id"]] = audio
			self.dialog.change_state("add", False)
			self.dialog.change_state("remove", True)

	def remove_from_library(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		args = {}
		if self.added_audios.has_key(post["id"]):
			args["audio_id"] = self.added_audios[post["id"]]
			args["owner_id"] = self.session.user_id
		else:
			args["audio_id"] = post["id"]
			args["owner_id"] = post["owner_id"]
		result = self.session.vk.client.audio.delete(**args)
		if int(result) == 1:
			self.dialog.change_state("add", True)
			self.dialog.change_state("remove", False)
			if self.added_audios.has_key(post["id"]):
				self.added_audios.pop(post["id"])

	def fill_information(self, index):
		post = self.post[index]
		if post.has_key("artist"):
			self.dialog.set("artist", post["artist"])
		if post.has_key("title"):
			self.dialog.set("title", post["title"])
		if post.has_key("duration"):
			self.dialog.set("duration", utils.seconds_to_string(post["duration"]))
		self.dialog.set_title(u"{0} - {1}".format(post["title"], post["artist"]))
		call_threaded(self.get_lyrics)
		if  post["owner_id"] == self.session.user_id or self.added_audios.has_key(post["id"]) == True:
			self.dialog.change_state("remove", True)
			self.dialog.change_state("add", False)
		else:
			self.dialog.change_state("add", True)
			self.dialog.change_state("remove", False)

	def get_lyrics(self):
		post = self.post[self.dialog.get_audio()]
		if post.has_key("lyrics_id"):
			l = self.session.vk.client.audio.getLyrics(lyrics_id=int(post["lyrics_id"]))
			self.dialog.set("lyric", l["text"])
		else:
			self.dialog.change_state("lyric", False)

	def download(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		f = u"{0} - {1}.mp3".format(post["title"], post["artist"])
		path = self.dialog.get_destination_path(f)
		if path != None:
			pub.sendMessage("download-file", url=post["url"], filename=path)

	def play(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		pub.sendMessage("play-audio", audio_object=post)

	def load_audios(self):
		for i in self.post:
			s = u"{0} - {1}. {2}".format(i["title"], i["artist"], utils.seconds_to_string(i["duration"]))
			self.dialog.insert_audio(s)
		self.dialog.list.SetSelection(0)
		if len(self.post) == 1:
			self.dialog.list.Enable(False)
			self.dialog.title.SetFocus()

	def handle_changes(self, *args, **kwargs):
		p = self.dialog.get_audio()
		self.fill_information(p)

class friendship(object):

	def __init__(self, session, post):
		self.session = session
		self.post = post
		self.dialog = postDialogs.friendship()
		list_of_friends = self.get_friend_names()
		from_ = self.session.get_user_name(self.post["source_id"])
		title = _(u"{0} added the following friends").format(from_,)
		self.dialog.set_title(title)
		self.set_friends_list(list_of_friends)

	def get_friend_names(self):
		self.friends = self.post["friends"]["items"]
		return [self.session.get_user_name(i["user_id"]) for i in self.friends]

	def set_friends_list(self, friendslist):
		for i in friendslist:
			self.dialog.friends.insert_item(False, *[i])
