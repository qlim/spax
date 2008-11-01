from wax import *
from spax.widgets.menus import SpaxMenuBar
from spax.widgets.notebook import SpaxNoteBook
from spax.widgets.filetreeview import ShowAllFileTreeView
from spax.utils import regexFromSearchString
from spax import settings

import re
import os

class MainFrame(Frame):
	def Body(self):
		self.SetMenuBar(SpaxMenuBar(self))
		self.splitter = Splitter(self)
		rootdir = getattr(settings, 'TREEVIEW_ROOT', '/')
		if not (os.path.exists(rootdir) and os.path.isdir(rootdir)):
			rootdir = '/'
		self.treeview = ShowAllFileTreeView(self.splitter, rootdir=rootdir, exclude=settings.TREEVIEW_HIDE_FILES)
		self.notebook = SpaxNoteBook(self.splitter)
		self.splitter.Split(self.treeview, self.notebook, direction='v', sashposition=200, minsize=100)
		self.AddComponent(self.splitter, expand='both')
		self.findPanel = FindPanel(self, size=(-1,28))
		self.AddComponent(self.findPanel, expand='h')
		self.findPanel.Hide()
		self.Pack()
		self.Size = (800, 600)
		self.newFile()

	def getEditor(self):
		return self.notebook.get_current_page()

	def focusFind(self):
		if not self.findPanel.IsShown():
			self.findPanel.Show()
			self.Layout()
		self.findPanel.findTextBox.SetFocus()
	
	def closeFind(self):
		self.findPanel.Hide()
		self.Layout()

	def findNextInCurrentFile(self, value, wrap=True):
		regex = regexFromSearchString(value)
		editor = self.getEditor()
		text = editor.GetText()
		pos = editor.GetCurrentPos()

		match = regex.search(text, pos, editor.GetTextLength())
		if wrap and not match:
			match = regex.search(text, 0, pos)
		if not match:
			return
		editor.SetSelection(match.start(), match.end())
	
	def newFile(self, event=None):
		self.notebook.newFile()

	def openFile(self, filename=None, event=None):
		if not filename:
			try:
				dlg = FileDialog(self, open=True)
				result = dlg.ShowModal()
				if result != 'ok':
					return
				filename = dlg.GetPaths()[0]
			finally:
				dlg.Destroy()
		self.notebook.openFile(filename)
	
	def closeFile(self, event=None):
		idx = self.notebook.GetSelection()
		self.notebook.closeFile(idx)

	def promptToSave(self, editor=None):
		from spax.widgets.dialog import PromptSaveDialog
		choices = []
		if not editor:
			for i in range(self.notebook.GetPageCount()):
				e = self.notebook.GetPage(i)
				if e.changed:
					choices.append((e.filename or '[noname]', i))
		else:
			choices = [(editor.filename or '[noname]', self.notebook.GetPageIndex(editor))]

		if choices:
			dialog = None
			try:
				dialog = PromptSaveDialog(self, choices=choices)
				save = dialog.ShowModal()
				if save == 'yes':
					indexes = dialog.getCheckedFiles()
					for i in indexes:
						editor = self.notebook.GetPage(i)
						if not editor.filename:
							self.notebook.SetSelection(i)
							self.notebook.GetCurrentPage().SetFocus()
						result = editor.save()
						if result == 'cancel':
							return 'cancel'
			finally:
				if dialog:
					dialog.Destroy()
			return 'yes'
		else:
			return 'no'

	def saveFile(self, event=None):
		editor = self.notebook.get_current_page()
		editor.save()
	
	def saveFileAs(self, event=None):
		editor = self.notebook.get_current_page()
		editor.saveAs()

	def OnClose(self, event=None):
		save = self.promptToSave()
		if save != 'cancel':
		        self.Destroy()
	
	def exit(self, event=None):
		self.Close(1)

class FindPanel(Panel):
	def Body(self):
		panel = Panel(self)
		self.findTextBox = TextBox(panel, size=(300,25))
		panel.AddComponent(Label(panel, 'Find:', size=(60,25)), border=5)
		panel.AddComponent(self.findTextBox, border=5)
		self.findButton = Button(panel, 'Find', size=(60,25), event=self.onClickFind)
		panel.AddComponent(self.findButton, border=5)
		self.AddComponent(panel, expand='h')
		panel.Pack()
		#self.moreButton = Button(self, '(more)', size=(60,25), event=self.onClickMore)
		#self.AddComponent(self.moreButton, border=5)
		self.Pack()
	
	def OnKeyUp(self, event=None):
		if event.KeyCode == keys.esc:
			event.Skip()
			self.Parent.closeFind()

	def onClickFind(self, event=None):
		self.Parent.findNextInCurrentFile(self.findTextBox.GetValue())

	def onClickMore(self, event=None):
		pass

app = Application(MainFrame, title='Spax', direction='vertical')
app.Run()
