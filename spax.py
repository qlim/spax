from wax import *
from spax.widgets.menus import SpaxMenuBar
from spax.widgets.notebook import SpaxNoteBook
from spax.widgets.filetreeview import ShowAllFileTreeView
from spax import settings

class MainFrame(Frame):
	def Body(self):
		self.SetMenuBar(SpaxMenuBar(self))
		self.splitter = Splitter(self)
		self.treeview = ShowAllFileTreeView(self.splitter, exclude=settings.TREEVIEW_HIDE_FILES)
		self.notebook = SpaxNoteBook(self.splitter)
		self.splitter.Split(self.treeview, self.notebook, direction='v', sashposition=200, minsize=100)
		self.AddComponent(self.splitter, expand='both')
		self.Pack()
		self.Size = (800, 600)
		self.newFile()

	def getEditor(self):
		return self.notebook.get_current_page()
	
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

	def saveFile(self, event=None):
		editor = self.notebook.get_current_page()
		editor.save()
	
	def saveFileAs(self, event=None):
		editor = self.notebook.get_current_page()
		editor.saveAs()
	
	def exit(self, event=None):
		self.Close()

app = Application(MainFrame, title='Spax', direction='vertical')
app.Run()
