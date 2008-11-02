from wax import *

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
        self.replaceButton = Button(self.replacePanel, 'Replace', size=(60, 25), event=self.onClickReplace)
        self.replaceAllButton = Button(self.replacePanel, 'Replace all', size=(80, 25), event=self.onClickReplaceAll)
        self.replacePanel.AddComponent(self.replaceLabel, border=2)
        self.replacePanel.AddComponent(self.replaceTextBox, border=2, expand='h')
        self.replacePanel.AddComponent(self.replaceButton, border=2)
        self.replacePanel.AddComponent(self.replaceAllButton, border=2)
        self.replacePanel.Pack()
        self.replacePanel.Show(self._expanded)

        self.findTextBox = TextBox(self.topPanel, size=(-1,25))
        self.findButton = Button(self.topPanel, 'Find', size=(60,25), event=self.onClickFind)
        self.isRegexCheckBox1 = CheckBox(self.topPanel, 'Regular expression')
        self.isRegexCheckBox1.Hide()
        self.topPanel.AddComponent(self.findTextBox, border=2, expand='h')
        self.topPanel.AddComponent(self.findButton, border=2)
        self.topPanel.AddComponent(self.isRegexCheckBox1, border=2)
        self.topPanel.AddComponent(self.replacePanel, expand='h')
        self.moreButton = Button(self.topPanel, self._expanded and '(less)' or '(more)', size=(60,25), event=self.onClickMore)
        self.moreButton.Hide()
        self.topPanel.AddComponent(self.moreButton, border=5)
        self.topPanel.Pack()

        self.isRegexCheckBox2 = CheckBox(self.bottomPanel, 'Regular expression')
        self.matchCaseCheckBox = CheckBox(self.bottomPanel, 'Match case')
        self.backwardsCheckBox = CheckBox(self.bottomPanel, 'Backwards')
        self.wrapCheckBox = CheckBox(self.bottomPanel, 'Wrap search')
        self.wrapCheckBox.SetValue(True)
        self.bottomPanel.AddComponent(self.isRegexCheckBox2, expand='both')
        self.bottomPanel.AddComponent(self.matchCaseCheckBox, expand='both')
        self.bottomPanel.AddComponent(self.backwardsCheckBox, expand='both')
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
    
    def _getFindArgs(self):
        return {
            'isRegex': self.isRegex(),
            'wrap': self.wrapCheckBox.GetValue(),
            'matchCase': self.matchCaseCheckBox.GetValue(),
            'backwards': self.backwardsCheckBox.GetValue()
        }

    def onClickFind(self, event=None):
        return self.Parent.findNextInCurrentFile(
            self.findTextBox.GetValue(),
            **self._getFindArgs()
        )

    def onClickReplace(self, event=None):
        return self.Parent.replaceNextInCurrentFile(
            self.findTextBox.GetValue(),
            self.replaceTextBox.GetValue(),
            **self._getFindArgs()
        )

    def onClickReplaceAll(self, event=None):
        return self.Parent.replaceAllInCurrentFile(
            self.findTextBox.GetValue(),
            self.replaceTextBox.GetValue(),
            **self._getFindArgs()
        )

    def onClickMore(self, event=None):
        self.expandPanel(not self._expanded)
