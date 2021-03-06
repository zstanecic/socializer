# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class general(wx.Panel, widgetUtils.BaseDialog):
	def __init__(self, panel):
		super(general, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		lbl1 = wx.StaticText(self, wx.NewId(), _("Number of items to load for newsfeed and wall buffers (maximun 100)"))
		self.wall_buffer_count = wx.SpinCtrl(self, wx.NewId())
		self.wall_buffer_count.SetRange(1, 100)
		box1 = wx.BoxSizer(wx.HORIZONTAL)
		box1.Add(lbl1, 0, wx.ALL, 5)
		box1.Add(self.wall_buffer_count, 0, wx.ALL, 5)
		sizer.Add(box1, 0, wx.ALL, 5)
		lbl3 = wx.StaticText(self, wx.NewId(), _("Number of items to load in video buffers (maximun 200)"))
		self.video_buffers_count = wx.SpinCtrl(self, wx.NewId())
		self.video_buffers_count.SetRange(1, 200)
		box3 = wx.BoxSizer(wx.HORIZONTAL)
		box3.Add(lbl3, 0, wx.ALL, 5)
		box3.Add(self.video_buffers_count, 0, wx.ALL, 5)
		sizer.Add(box3, 0, wx.ALL, 5)
		self.load_images = wx.CheckBox(self, wx.NewId(), _("Load images in posts"))
		sizer.Add(self.load_images, 0, wx.ALL, 5)
		lbl4 = wx.StaticText(self, wx.NewId(), _("Update channel"))
		self.update_channel = wx.ComboBox(self, wx.NewId(), choices=[_("Stable"), _("Alpha")], value=_("Native"), style=wx.CB_READONLY)
		box4 = wx.BoxSizer(wx.HORIZONTAL)
		box4.Add(lbl4, 0, wx.ALL, 5)
		box4.Add(self.update_channel, 0, wx.ALL, 5)
		sizer.Add(box4, 0, wx.ALL, 5)
		self.SetSizer(sizer)

class chat(wx.Panel, widgetUtils.BaseDialog):
	def __init__(self, panel):
		super(chat, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.notify_online = wx.CheckBox(self, wx.NewId(), _("Show notifications when users are online"))
		sizer.Add(self.notify_online, 0, wx.ALL, 5)
		self.notify_offline = wx.CheckBox(self, wx.NewId(), _("Show notifications when users are offline"))
		sizer.Add(self.notify_offline, 0, wx.ALL, 5)
		self.open_unread_conversations = wx.CheckBox(self, wx.NewId(), _("Open unread conversations at startup"))
		sizer.Add(self.open_unread_conversations, 0, wx.ALL, 5)
		self.automove_to_conversations = wx.CheckBox(self, wx.NewId(), _("Move focus to new conversations"))
		sizer.Add(self.automove_to_conversations, 0, wx.ALL, 5)
		lbl = wx.StaticText(self, wx.NewId(), _("Notification type"))
		self.notifications = wx.ComboBox(self, wx.NewId(), choices=[_("Native"), _("Custom"),], value=_("Native"), style=wx.CB_READONLY)
		nbox = wx.BoxSizer(wx.HORIZONTAL)
		nbox.Add(lbl, 0, wx.ALL, 5)
		nbox.Add(self.notifications, 0, wx.ALL, 5)
		sizer.Add(nbox, 0, wx.ALL, 5)
		self.SetSizer(sizer)

class loadAtStartup(wx.Panel, widgetUtils.BaseDialog):
	def __init__(self, panel):
		super(loadAtStartup, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.audio_albums = wx.CheckBox(self, wx.NewId(), _("Create buffers for audio albums at startup"))
		sizer.Add(self.audio_albums, 0, wx.ALL, 5)
		self.video_albums = wx.CheckBox(self, wx.NewId(), _("Create buffers for video albums at startup"))
		sizer.Add(self.video_albums, 0, wx.ALL, 5)
		self.communities = wx.CheckBox(self, wx.NewId(), _("Create buffers for communities and public pages at startup"))
		sizer.Add(self.communities, 0, wx.ALL, 5)
		self.SetSizer(sizer)

class configurationDialog(widgetUtils.BaseDialog):

	def __init__(self, title):
		super(configurationDialog, self).__init__(None, -1, title=title)
		self.panel = wx.Panel(self)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.notebook = wx.Notebook(self.panel)

	def create_general(self):
		self.general = general(self.notebook)
		self.notebook.AddPage(self.general, _("General"))
		self.general.SetFocus()

	def create_chat(self):
		self.chat = chat(self.notebook)
		self.notebook.AddPage(self.chat, _("Chat settings"))

	def create_startup_options(self):
		self.startup = loadAtStartup(self.notebook)
		self.notebook.AddPage(self.startup, _("Optional buffers"))

	def realize(self):
		self.sizer.Add(self.notebook, 0, wx.ALL, 5)
		ok_cancel_box = wx.BoxSizer(wx.HORIZONTAL)
		ok = wx.Button(self.panel, wx.ID_OK, _("Save"))
		ok.SetDefault()
		cancel = wx.Button(self.panel, wx.ID_CANCEL, _("Close"))
		self.SetEscapeId(cancel.GetId())
		ok_cancel_box.Add(ok, 0, wx.ALL, 5)
		ok_cancel_box.Add(cancel, 0, wx.ALL, 5)
		self.sizer.Add(ok_cancel_box, 0, wx.ALL, 5)
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())

	def get_value(self, panel, key):
		p = getattr(self, panel)
		return getattr(p, key).GetValue()

	def set_value(self, panel, key, value):
		p = getattr(self, panel)
		control = getattr(p, key)
		getattr(control, "SetValue")(value)

	def alpha_channel(self):
		return wx.MessageDialog(self, _("The alpha channel contains bleeding edge changes introduced to Socializer. A new alpha update is generated every time there are new changes in the project. Take into account that updates are generated automatically and may fail at any time due to errors in the build process. Use alpha channels when you are sure you want to try the latest changes and contribute with reports to fix bugs. Never use alpha channel updates for everyday use. Do you want to continue?"), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()

	def weekly_channel(self):
		return wx.MessageDialog(self, _("The weekly channel generates an update automatically every week by building the source code present in the project. This version is used to test features added to the next stable version. Do you want to continue?"), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()