
from wax import *
import os
from spax.widgets.editor import Editor
import wx

class SpaxNoteBook(NoteBook):
    def __init__(self, *args, **kwargs):
        super(SpaxNoteBook, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMiddleClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDoubleClick)
        filedrop = FileDropTarget(self, self.OnDropFiles)
        self.SetDropTarget(filedrop)

    def GetPageIndex(self, page):
        for i in range(self.GetPageCount()):
            if self.GetPage(i) == page:
                return i

    def AddPage(self, win, *args, **kwargs):
        super(SpaxNoteBook, self).AddPage(win, *args, **kwargs)
        win.SetFocus()

    def openFile(self, filename):
        for i in range(self.GetPageCount()):
            editor = self.GetPage(i)
            if editor.filename == filename:
                self.SetSelection(i)
                return
        old_id = self.GetSelection()
        ed = Editor(self)
        ed.open(filename)
        path, shortname = os.path.split(filename)
        self.AddPage(ed, shortname, 1)
        oldpage = self.GetPage(old_id)
        if not (oldpage.filename or oldpage.changed):
            self.closeFile(old_id)

    def closeFile(self, idx):
        editor = self.GetPage(idx)
        save = 'no'
        if editor.changed:
            save = self.Parent.Parent.promptToSave(editor)
        if save == 'cancel':
            return
        self.DeletePage(idx)
        if self.GetPageCount() == 0:
            self.newFile()

    def newFile(self):
        ed = Editor(self)
        self.AddPage(ed, "[noname]", 1)

    def get_current_page(self):
        idx = self.GetSelection()
        if idx > -1:
            return self.GetPage(idx)
        else:
            raise ValueError, "No current page"

    def next_page(self):
        """ Move to the next page. """
        idx = self.GetSelection()
        if idx > -1:
            idx = (idx + 1) % self.GetPageCount()
            self.SetSelection(idx)
            self.GetCurrentPage().SetFocus()

    def previous_page(self):
        """ Move to the previous page. """
        idx = self.GetSelection()
        if idx > -1:
            idx = (idx - 1) % self.GetPageCount()
            self.SetSelection(idx)
            self.GetCurrentPage().SetFocus()

    ###
    ### helper functions
    
    def get_editors(self):
        """ Get a list of all Editor instances. """
        editors = []
        for i in range(self.GetPageCount()):
            win = self.GetPage(i)
            if isinstance(win, Editor):
                editors.append(win)
        return editors

    def OnMiddleClick(self, event=None):
        mousePos = event.GetPosition()
        pageIdx, other = self.HitTest(mousePos)
	if pageIdx >= 0:
            self.closeFile(pageIdx)
    
    def OnLeftDoubleClick(self, event=None):
        mousePos = event.GetPosition()
        pageIdx, other = self.HitTest(mousePos)
	if pageIdx < 0:
            self.newFile()

    def OnDropFiles(self, x, y, filenames):
        print filenames, "dropped"
        for filename in filenames:
            self.open_file(filename)
            
