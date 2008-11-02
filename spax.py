from wax import *
from spax.widgets.menus import SpaxMenuBar
from spax.widgets.notebook import SpaxNoteBook
from spax.widgets.filetreeview import ShowAllFileTreeView
from spax.utils import regexFromSearchString
from spax import settings

import re
import os
import wx

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
		self.findPanel = FindPanel(self, direction='v', expanded=True)
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

	def findNextInCurrentFile(self, value, wrap=True, isRegex=False, matchCase=False):
		flags = re.M
		if not matchCase:
			flags |= re.I
		if isRegex:
			regex = re.compile(value, flags)
		else:
			regex = regexFromSearchString(value, flags)
		editor = self.getEditor()
		text = editor.GetText()
		pos = editor.GetCurrentPos()

		match = regex.search(text, pos, editor.GetTextLength())
		if wrap and not match:
			match = regex.search(text, 0, pos)
		if not match:
			return
		editor.SetSelection(match.start(), match.end())
		return match
	
	def replaceNextInCurrentFile(self, find, replace, wrap=True, isRegex=False, matchCase=False):
		match = self.findNextInCurrentFile(find, wrap, isRegex, matchCase)
		if match:
			editor = self.getEditor()
			editor.Replace(match.start(), match.end(), replace)
			editor.SetSelection(match.start(), match.start() + len(replace))
	
	def newFile(self, event=None):
		self.notebook.newFile()

	def open(self, event=None):
		self.openFile()

	def openFile(self, filename=None):
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
	def __init__(self, *args, **kwargs):
		self._expanded = kwargs.pop('expanded', False)
		super(FindPanel, self).__init__(*args, **kwargs)

	def Body(self):
		self.topPanel = Panel(self, direction='h')
		self.bottomPanel = Panel(self, direction='h')
		
		self.replacePanel = Panel(self.topPanel, direction='h')
		self.replaceLabel = Label(self.replacePanel, 'Replace with:')
		self.replaceTextBox = TextBox(self.replacePanel, size=(-1,25))
		self.replaceButton = Button(self.replacePanel, 'Find/Replace', size=(60, 25), event=self.onClickReplace)
		self.replacePanel.AddComponent(self.replaceLabel, border=5)
		self.replacePanel.AddComponent(self.replaceTextBox, border=5, expand='h')
		self.replacePanel.AddComponent(self.replaceButton, border=5)
		self.replacePanel.Pack()
		self.replacePanel.Show(self._expanded)

		self.findTextBox = TextBox(self.topPanel, size=(-1,25))
		self.findButton = Button(self.topPanel, 'Find', size=(60,25), event=self.onClickFind)
		self.isRegexCheckBox1 = CheckBox(self.topPanel, 'Regular expression')
		self.isRegexCheckBox1.Hide()
		self.topPanel.AddComponent(self.findTextBox, border=5, expand='h')
		self.topPanel.AddComponent(self.findButton, border=5)
		self.topPanel.AddComponent(self.isRegexCheckBox1, border=5)
		self.topPanel.AddComponent(self.replacePanel, expand='h')
		self.moreButton = Button(self.topPanel, self._expanded and '(less)' or '(more)', size=(60,25), event=self.onClickMore)
		self.moreButton.Hide()
		self.topPanel.AddComponent(self.moreButton, border=5)
		self.topPanel.Pack()

		self.isRegexCheckBox2 = CheckBox(self.bottomPanel, 'Regular expression')
		self.matchCaseCheckBox = CheckBox(self.bottomPanel, 'Match case')
		#self.backwardsCheckBox = CheckBox(self.bottomPanel, 'Backwards')
		self.wrapCheckBox = CheckBox(self.bottomPanel, 'Wrap search')
		self.wrapCheckBox.SetValue(True)
		self.bottomPanel.AddComponent(self.isRegexCheckBox2, expand='both')
		self.bottomPanel.AddComponent(self.matchCaseCheckBox, expand='both')
		#self.bottomPanel.AddComponent(self.backwardsCheckBox, expand='both')
		self.bottomPanel.AddComponent(self.wrapCheckBox, expand='both')
		self.bottomPanel.Pack()
		self.bottomPanel.Show(self._expanded)

		self.AddComponent(self.topPanel, expand='h')
		self.AddComponent(self.bottomPanel, expand='h')
		self.Pack()

	def expandPanel(self, expand=True):
		if self._expanded == expand:
			return
		self.moreButton.SetLabel(expand and '(less)' or '(more)')
		old, new = expand and (self.isRegexCheckBox1, self.isRegexCheckBox2) or (self.isRegexCheckBox2, self.isRegexCheckBox1)
		new.SetValue(old.IsChecked())
		old.Hide()
		new.Show()

		self.replacePanel.Show(expand)
		self.bottomPanel.Show(expand)
		self.Layout()
		self._expanded = expand

	def isRegex(self):
		return (self._expanded and self.isRegexCheckBox2 or self.isRegexCheckBox1).IsChecked()
	
	def OnKeyUp(self, event=None):
		if event.KeyCode == keys.esc:
			event.Skip()
			self.Parent.closeFind()
	
	def findNextInCurrentFile(self):
		return self.Parent.findNextInCurrentFile(
			self.findTextBox.GetValue(), 
			isRegex=self.isRegex(), 
			wrap=self.wrapCheckBox.GetValue(), 
			matchCase=self.matchCaseCheckBox.GetValue()
		)
	
	def replaceNextInCurrentFile(self):
		return self.Parent.replaceNextInCurrentFile(
			self.findTextBox.GetValue(),
			self.replaceTextBox.GetValue(),
			isRegex=self.isRegex(), 
			wrap=self.wrapCheckBox.GetValue(), 
			matchCase=self.matchCaseCheckBox.GetValue()
		)

	def onClickFind(self, event=None):
		self.findNextInCurrentFile()

	def onClickReplace(self, event=None):
		self.replaceNextInCurrentFile()

	def onClickMore(self, event=None):
		self.expandPanel(not self._expanded)

app = Application(MainFrame, title='Spax', direction='vertical')
app.Run()
