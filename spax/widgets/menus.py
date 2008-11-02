from wax import MenuBar, Menu

class SpaxMenuBar(MenuBar):
	def __init__(self, parent, *args, **kwargs):
		super(SpaxMenuBar, self).__init__(*args, **kwargs)
		self.Append(FileMenu(parent), '&File')
		self.Append(EditMenu(parent), '&Edit')

class FileMenu(Menu):
	def __init__(self, *args, **kwargs):
		super(FileMenu, self).__init__(*args, **kwargs)
		self.Append('&New file', self.parent.newFile, 'Create a new file', hotkey='Ctrl-N')
		self.Append("&Open", self.parent.open, "Open a file", hotkey='Ctrl-O')
		self.Append("&Close", self.parent.closeFile, "Close a file", hotkey='Ctrl-F4')
		self.Append("&Save", self.parent.saveFile, "Save file", hotkey='Ctrl-S')
		self.Append("Save &As", self.parent.saveFileAs, "Save file under a different name")
		self.Append('E&xit', self.parent.exit, 'Exit spax', hotkey='Alt-F4')

class EditMenu(Menu):
	def __init__(self, *args, **kwargs):
		super(EditMenu, self).__init__(*args, **kwargs)
		
		self.Append('&Undo', self.onUndo, hotkey='Ctrl-Z')
		self.Append('&Redo', self.onRedo, hotkey='Ctrl-Y')
		self.Append('&Copy', self.onCopy, hotkey='Ctrl-C')
		self.Append('C&ut', self.onCut, hotkey='Ctrl-X')
		self.Append('&Paste', self.onPaste, hotkey='Ctrl-V')
		self.Append('&Select All', self.onSelectAll, hotkey='Ctrl-A')
		self.Append('&Find/replace', self.onFind, hotkey='Ctrl-F')
		
	def onUndo(self, event=None):
		self.parent.getEditor().Undo()
	
	def onRedo(self, event=None):
		self.parent.getEditor().Redo()
	
	def onCopy(self, event=None):
		self.parent.getEditor().Copy()
	
	def onCut(self, event=None):
		self.parent.getEditor().Cut()
	
	def onPaste(self, event=None):
		self.parent.getEditor().Paste()
	
	def onSelectAll(self, event=None):
		self.parent.getEditor().SelectAll()

	def onFind(self, event=None):
		self.parent.focusFind()
	
