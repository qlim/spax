from wax import *
from spax.widgets.menus import SpaxMenuBar
from spax.widgets.notebook import SpaxNoteBook
from spax.widgets.findpanel import FindPanel
from spax.widgets.filetreeview import ShowAllFileTreeView
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

    def findNextInCurrentFile(self, pattern, wrap=True, isRegex=False, matchCase=False, backwards=False):
        flags = re.M
        if not matchCase:
            flags |= re.I
        if not isRegex:
            pattern = re.escape(pattern)
        regex = re.compile(pattern, flags)
        editor = self.getEditor()
        text = editor.GetText()
        pos = editor.GetCurrentPos()
        
        if not backwards:
            match = regex.search(text, pos, editor.GetTextLength())
            if wrap and not match:
                match = regex.search(text, 0, pos)
        
        else:
            iter = re.finditer(pattern, text)
            match = None
            try:
                while True:
                    next = iter.next()
                    if match and match.end() < pos and next.end() >= pos:
                        raise StopIteration()
                    match = next
            except StopIteration:
                pass

        if not match:
            return
        editor.SetSelection(match.start(), match.end())
        return match
    
    def replaceNextInCurrentFile(self, find, replace, wrap=True, isRegex=False, matchCase=False, backwards=False):
        match = self.findNextInCurrentFile(find, wrap, isRegex, matchCase, backwards)
        if match:
            editor = self.getEditor()
            if isRegex:
                replace = match.expand(replace)
            editor.Replace(match.start(), match.end(), replace)
            editor.SetSelection(match.start(), match.start() + len(replace))
            editor.checkChanged()
    
    def replaceAllInCurrentFile(self, find, replace, wrap=True, isRegex=False, matchCase=False, backwards=False):
        flags = re.M
        if not matchCase:
            flags |= re.I
        if not isRegex:
            find = re.escape(find)
            replace = re.escape(replace)
        regex = re.compile(find, flags)
        editor = self.getEditor()
        text = editor.GetText()
        text = regex.sub(replace, text)
        editor.SetText(text)
        editor.checkChanged()
    
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
                if save == 'cancel':
                    return save
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

app = Application(MainFrame, title='Spax', direction='vertical')
app.Run()
