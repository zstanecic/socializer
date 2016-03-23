# -*- coding: utf-8 -*-
import wx
import application

class mainWindow(wx.Frame):
	def makeMenu(self):
		mb = wx.MenuBar()
		buffer = wx.Menu()
		self.update_buffer = buffer.Append(wx.NewId(), _(u"Update current buffer"))
		self.load_previous_items = buffer.Append(wx.NewId(), _(u"Load previous items"))
		self.load_previous_items.Enable(False)
		mb.Append(buffer, _(u"Buffer"))
		help_ = wx.Menu()
		self.about = help_.Append(wx.NewId(), _(u"About {0}").format(application.name,))
		self.check_for_updates = help_.Append(wx.NewId(), _(u"Check for updates"))

		mb.Append(help_, _(u"Help"))
		self.SetMenuBar(mb)

	def __init__(self):
		super(mainWindow, self).__init__(parent=None, id=wx.NewId(), title=application.name)
		self.makeMenu()
		self.panel = wx.Panel(self)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sb = self.CreateStatusBar()
		self.tb = wx.Treebook(self.panel, -1)
		self.sizer.Add(self.tb, 0, wx.ALL, 5)

	def realize(self):
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())

	def change_status(self, status):
		self.sb.SetStatusText(status)

	def connection_error(self):
		wx.MessageDialog(self, _(u"There is a connection error. Check your internet connection and try again later."), _(u"Connection error"), wx.ICON_ERROR).ShowModal()

	def get_buffer_count(self):
		return self.tb.GetPageCount()

	def add_buffer(self, buffer, name):
		self.tb.AddPage(buffer, name)

	def insert_buffer(self, buffer, name, pos):
		self.tb.InsertSubPage(pos, buffer, name)

	def search(self, name_):
		for i in xrange(0, self.tb.GetPageCount()):
			if self.tb.GetPage(i).name == name_: return i

	def get_current_buffer(self):
		return self.tb.GetCurrentPage()

	def get_current_buffer_pos(self):
		return self.tb.GetSelection()

	def get_buffer(self, pos):
		return self.GetPage(pos)

	def change_buffer(self, position):
		self.tb.ChangeSelection(position)

	def get_buffer_text(self):
		return self.tb.GetPageText(self.tb.GetSelection())

	def get_buffer_by_id(self, id):
		return self.nb.FindWindowById(id)

	def advance_selection(self, forward):
		self.tb.AdvanceSelection(forward)

	def about_dialog(self, *args, **kwargs):
		info = wx.AboutDialogInfo()
		info.SetName(application.name)
		info.SetVersion(application.version)
		info.SetDescription(application.description)
		info.SetCopyright(application.copyright)
#  info.SetTranslators(application.translators)
#  info.SetLicence(application.licence)
		info.AddDeveloper(application.author)
		wx.AboutBox(info)

	def about_dialog(self, *args, **kwargs):
		info = wx.AboutDialogInfo()
		info.SetName(application.name)
		info.SetVersion(application.version)
		info.SetDescription(application.description)
		info.SetCopyright(application.copyright)
#		info.SetTranslators(application.translators)
#		info.SetLicence(application.licence)
		info.AddDeveloper(application.author)
		wx.AboutBox(info)
