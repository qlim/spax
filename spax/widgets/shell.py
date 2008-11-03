import wax
import os
import wx
from wx.py.shell import Shell
from wax.waxobject import WaxObject

class SpaxShell(Shell, WaxObject):

    def __init__(self, parent, *args, **kwargs):
        id = wx.NewId()
        loc = kwargs.get('locals', {})
        loc['shell'] = self
        kwargs['locals'] = loc

        super(SpaxShell, self).__init__(parent, id, *args, **kwargs)

        # override the main frame accelerator
        aTable = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('A'), wx.ID_ANY),
        ])
        self.SetAcceleratorTable(aTable)

    def doHome(self):
        home = self.promptPosEnd
        if self.GetCurrentPos() > home:
            self.SetCurrentPos(home)
            self.SetAnchor(home)
            self.EnsureCaretVisible()

    def doKill(self):
        self.SetSelection(self.GetCurrentPos(), self.GetTextLength())
        self.ReplaceSelection('')
        self.more = False

    def doEnd(self):
        end = self.GetTextLength()
        self.SetCurrentPos(end)
        self.SetAnchor(end)
        self.EnsureCaretVisible()

    def OnKeyDown(self, event):
        """Key down event handler."""

        key = event.GetKeyCode()
        # If the auto-complete window is up let it do its thing.
        if self.AutoCompActive():
            event.Skip()
            return

        controlDown = event.ControlDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        currpos = self.GetCurrentPos()
        endpos = self.GetTextLength()
        selecting = self.GetSelectionStart() != self.GetSelectionEnd()

        isK = lambda k, l: k == ord(l)

        if controlDown and isK(key, 'A'):
            self.doHome()
        elif controlDown and isK(key, 'K'):
            self.doKill()
        elif controlDown and isK(key, 'E'):
            self.doEnd()
        # Insert the previous command from the history buffer.
        elif (key == wx.WXK_UP) and self.CanEdit():
            self.OnHistoryInsert(step=+1)

        # Insert the next command from the history buffer.
        elif (key == wx.WXK_DOWN) and self.CanEdit():
            self.OnHistoryInsert(step=-1)
        else:
            super(SpaxShell, self).OnKeyDown(event)


