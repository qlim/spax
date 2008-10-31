from wax import StyledTextBox, FileDialog, keys
from wxPython import stc
import wx
import os
import string
import re
import md5

FIXED_FONT = ('Monospace', 10)
INDENTATION_RE = re.compile(r'^[ \t]*')

class Editor(StyledTextBox):

    def __init__(self, *args, **kwargs):
        super(Editor, self).__init__(*args, **kwargs)
        self.filename = None
        self.changed = False
        self.setHash('')
	self.SetFont(FIXED_FONT)
    
    def setHash(self, data=None):
        if data is None:
            data = self.GetData()
        self.hash = md5.new(data).hexdigest()
    
    def checkChanged(self):
        hash = md5.new(self.GetText()).hexdigest()
        hasChanged = hash != self.hash
        if hasChanged != self.changed:
            idx = self.Parent.GetSelection()
            name = self.filename and os.path.split(self.filename)[1] or '[noname]'
            if hasChanged:
                name += ' *'
            self.Parent.SetPageText(idx, name)
        self.changed = hasChanged

    def open(self, filename, readonly=False):
        f = open(filename, "rb")
        data = f.read()
        f.close()
        self.ClearAll()
        self.AddText(data)
        self.filename = filename
        self.SetReadOnly(readonly)
        self.setHash(data)
        self.checkChanged()
        self.SendMsg(stc.wxSTC_CMD_DOCUMENTSTART)

    def save(self):
        if self.filename:
            self._save(self.filename)
        else:
            self.saveAs()

    def saveAs(self):
        dlg = FileDialog(self, save=True)
        try:
            result = dlg.ShowModal()
            if result == 'ok':
                filename = dlg.GetPaths()[0]
                self.filename = filename
                self._save(filename)
        finally:
            dlg.Destroy()

    def _save(self, filename):
        data = self.GetText()
        f = open(filename, "wb")
        f.write(data)
        f.close()
        self.setHash(data)
        self.checkChanged()

    ###
    ### indentation

    def _get_indent(self, line):
        """ Get the indentation, as a string, from the given line. """
	return INDENTATION_RE.match(line).group()

    def handle_autoindent(self):
        prevlineno = self.GetCurrentLineNo() - 1
        prevline = self.GetLine(prevlineno)
        indent = self._get_indent(prevline)
        currpos = self.GetCurrentPos()
        self.InsertText(currpos, indent)
        self.GotoPos(currpos + len(indent))
        
    def OnKeyUp(self, event):
        keycode = event.GetKeyCode()
        if keycode == keys.enter:
            self.handle_autoindent()
        elif keycode == keys.pageup and event.ControlDown():
            self.CursorDocumentStart()
        elif keycode == keys.pagedown and event.ControlDown():
            self.CursorDocumentEnd()
        else:
            self.checkChanged()
            event.Skip()

    def GetCurrentLineNo(self):
        return self.LineFromPosition(self.GetCurrentPos())
            
    def UpdateUI(self, event):
        if options.match_braces:
            pos = self.GetCurrentPos()
            char = self.GetCharAt(pos)
            if chr(char) in '([{}])':
                self.BraceHighlight(-1,-1)
                pos2 = self.BraceMatch(pos)
                if pos2 == stc.wxSTC_INVALID_POSITION:
                    self.BraceBadLight(pos)
                else:
                    self.BraceHighlight(pos, pos2)
            else:
                # clear brace match highlighting
                self.BraceHighlight(-1,-1)

