# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six
import widgetUtils
import wx
from pubsub import pub
from wxUI import menus
from .import base

class displayPostInteractor(base.baseInteractor):

	def set(self, control, value):
		if not hasattr(self.view, control):
			raise AttributeError("The control is not present in the view.")
		getattr(self.view, control).SetValue(value)

	def load_image(self, image):
		image = wx.Image(stream=six.BytesIO(image.content))
		try:
			self.view.image.SetBitmap(wx.Bitmap(image))
		except ValueError:
			return
		self.view.panel.Layout()

	def add_items(self, control, items):
		if not hasattr(self.view, control):
			raise AttributeError("The control is not present in the view.")
		for i in items:
			getattr(self.view, control).insert_item(False, *i)

	def enable_attachments(self):
		self.view.attachments.list.Enable(True)

	def enable_photo_controls(self, navigation):
		self.view.enable_photo_controls(navigation)

	def clean_list(self, list):
		if not hasattr(self.view, list):
			raise AttributeError("The control is not present in the view.")
		getattr(self.view, control).clear()

	def install(self, *args, **kwargs):
		super(displayPostInteractor, self).install(*args, **kwargs)
		self.view.comments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_show_comment)
		self.view.attachments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open_attachment)
		widgetUtils.connect_event(self.view.like, widgetUtils.BUTTON_PRESSED, self.on_like)
		widgetUtils.connect_event(self.view.comment, widgetUtils.BUTTON_PRESSED, self.on_add_comment)
		widgetUtils.connect_event(self.view.tools, widgetUtils.BUTTON_PRESSED, self.on_show_tools_menu)
		if hasattr(self.view, "repost"):
			widgetUtils.connect_event(self.view.repost, widgetUtils.BUTTON_PRESSED, self.on_repost)
			self.view.comments.list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.on_focus)
		if hasattr(self.view, "reply"):
			widgetUtils.connect_event(self.view.reply, widgetUtils.BUTTON_PRESSED, self.on_reply)
#		self.view.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_show_menu, self.view.comments.list)
#		self.view.Bind(wx.EVT_LIST_KEY_DOWN, self.on_show_menu_by_key, self.view.comments.list)
		pub.subscribe(self.set, self.modulename+"_set")
		pub.subscribe(self.load_image, self.modulename+"_load_image")
		pub.subscribe(self.add_items, self.modulename+"_add_items")
		pub.subscribe(self.enable_attachments, self.modulename+"_enable_attachments")
		pub.subscribe(self.enable_photo_controls, self.modulename+"_enable_photo_controls")

	def uninstall(self):
		super(displayPostInteractor, self).uninstall()
		pub.unsubscribe(self.set, self.modulename+"_set")
		pub.unsubscribe(self.load_image, self.modulename+"_load_image")
		pub.unsubscribe(self.add_items, self.modulename+"_add_items")
		pub.unsubscribe(self.enable_attachments, self.modulename+"_enable_attachments")
		pub.unsubscribe(self.enable_photo_controls, self.modulename+"_enable_photo_controls")

	def on_focus(self, *args, **kwargs):
		item = self.view.comments.get_selected()
		if item == -1:
			self.view.reply.Enable(False)
		else:
			self.view.reply.Enable(True)

	def on_like(self, *args, **kwargs):
		self.presenter.post_like()

	def on_repost(self, *args, **kwargs):
		self.presenter.post_repost()

	def on_reply(self, *args, **kwargs):
		if hasattr(self.view, "repost"):
			comment = self.view.comments.get_selected()
			self.presenter.reply(comment)
		else:
			self.presenter.reply()

	def on_add_comment(self, *args, **kwargs):
		self.presenter.add_comment()

	def on_show_tools_menu(self, *args, **kwargs):
		menu = menus.toolsMenu()
		widgetUtils.connect_event(self.view, widgetUtils.MENU, self.on_open_url, menuitem=menu.url)
		widgetUtils.connect_event(self.view, widgetUtils.MENU, self.on_translate, menuitem=menu.translate)
		widgetUtils.connect_event(self.view, widgetUtils.MENU, self.on_spellcheck, menuitem=menu.CheckSpelling)
		self.view.PopupMenu(menu, self.view.tools.GetPosition())

	def on_open_url(self, *args, **kwargs):
		pass

	def on_open_attachment(self, *args, **kwargs):
		attachment = self.view.attachments.get_selected()
		self.presenter.open_attachment(attachment)

	def on_translate(self, *args, **kwargs):
		dlg = translator.gui.translateDialog()
		if dlg.get_response() == widgetUtils.OK:
			text_to_translate = self.view.get("post_view")
			dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
			self.presenter.translate(text_to_translate, dest)
		dlg.Destroy()

	def on_spellcheck(self, event=None):
		text = self.view.get("post_view")
		self.presenter.spellcheck(text)

	def on_show_comment(self, *args, **kwargs):
		comment = self.view.comments.get_selected()
		self.presenter.show_comment(comment)

class displayAudioInteractor(base.baseInteractor):

	def set(self, control, value):
		if not hasattr(self.view, control):
			raise AttributeError("The control is not present in the view.")
		getattr(self.view, control).SetValue(value)

	def add_items(self, control, items):
		if not hasattr(self.view, control):
			raise AttributeError("The control is not present in the view.")
		for i in items:
			getattr(self.view, control).Append(i)
		getattr(self.view, control).SetSelection(0)

	def install(self, *args, **kwargs):
		super(displayAudioInteractor, self).install(*args, **kwargs)
		widgetUtils.connect_event(self.view.list, widgetUtils.LISTBOX_CHANGED, self.on_change)
		widgetUtils.connect_event(self.view.download, widgetUtils.BUTTON_PRESSED, self.on_download)
		widgetUtils.connect_event(self.view.play, widgetUtils.BUTTON_PRESSED, self.on_play)
		widgetUtils.connect_event(self.view.add, widgetUtils.BUTTON_PRESSED, self.on_add_to_library)
		widgetUtils.connect_event(self.view.remove, widgetUtils.BUTTON_PRESSED, self.on_remove_from_library)
		pub.subscribe(self.set, self.modulename+"_set")
		pub.subscribe(self.add_items, self.modulename+"_add_items")

	def uninstall(self):
		super(displayAudioInteractor, self).uninstall()
		pub.unsubscribe(self.set, self.modulename+"_set")
		pub.unsubscribe(self.add_items, self.modulename+"_add_items")

	def on_change(self, *args, **kwargs):
		post = self.view.get_audio()
		self.presenter.handle_changes(post)

	def on_download(self, *args, **kwargs):
		post = self.view.get_audio()
		suggested_filename = self.presenter.get_suggested_filename(post)
		path = self.view.get_destination_path(suggested_filename)
		self.presenter.download(post, path)

	def on_play(self, *args, **kwargs):
		post = self.view.get_audio()
		self.presenter.play(post)

	def on_add_to_library(self, *args, **kwargs):
		post = self.view.get_audio()
		self.presenter.add_to_library(post)

	def on_remove_from_library(self, *args, **kwargs):
		post = self.view.get_audio()
		self.presenter.remove_from_library(post)

class displayFriendshipInteractor(base.baseInteractor):

	def add_items(self, control, items):
		if not hasattr(self.view, control):
			raise AttributeError("The control is not present in the view.")
		for i in items:
			getattr(self.view, control).insert_item(False, *[i])


	def install(self, *args, **kwargs):
		super(displayFriendshipInteractor, self).install(*args, **kwargs)
		pub.subscribe(self.add_items, self.modulename+"_add_items")

	def uninstall(self):
		super(displayFriendshipInteractor, self).uninstall()
		pub.unsubscribe(self.add_items, self.modulename+"_add_items")