import wx

from wax.dialog import Dialog
from wax import Panel, Button, CheckListBox

class PromptSaveDialog(Dialog):
    def __init__(self, parent, choices=None, cancel_button=1):
        title = 'Save files?'
        self.__choices = choices or []
        super(PromptSaveDialog, self).__init__(parent, title, cancel_button=cancel_button)

    def AddButtonPanel(self, cancel_button=1):
        panel = Panel(self, direction='horizontal')
        self.saveAllButton = Button(panel, 'Save selected', event=self.OnClickSaveSelected)
        self.saveAllButton.SetDefault()
        panel.AddComponent(self.saveAllButton, expand=1, border=5)

        self.saveNoneButton = Button(panel, 'Save none', event=self.OnClickSaveNone)
        panel.AddComponent(self.saveNoneButton, expand=1, border=5)

        if cancel_button:
            cancelbutton = Button(panel, "Cancel", event=self.OnClickCancelButton)
            panel.AddComponent(cancelbutton, expand=1, border=5)
        return panel

    def OnClickSaveSelected(self, event=None):
        event.Skip()
        self.EndModal(wx.ID_YES)

    def OnClickSaveNone(self, event=None):
        event.Skip()
        self.EndModal(wx.ID_NO)

    def OnClickCancelButton(self, event=None):
        self.EndModal(wx.ID_CANCEL)

    def ShowModal(self):
        """ Show the dialog modally.  Returns 'yes', 'no' or 'cancel'. """
        r = wx.Dialog.ShowModal(self)
        return {
            wx.ID_YES: "yes",
            wx.ID_NO: "no",
            wx.ID_CANCEL: "cancel",
        }.get(r, "?")

    def Body(self):
        self.listbox = CheckListBox(self)
        for filename, idx in self.__choices:
            i = self.listbox.Append(filename, idx)
            self.listbox.Check(i, True)
        self.AddComponent(self.listbox, expand="both", border=5)

    def getCheckedFiles(self):
        return [self.listbox.GetClientData(i) for i in range(self.listbox.GetCount()) if self.listbox.IsChecked(i)]

    # this doesn't work -- or does it?:
    def OnCharHook(self, event=None):
        if event.GetKeyCode() == keys.esc:
            self.OnClickCancelButton()
            event.Skip()

