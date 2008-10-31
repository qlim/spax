
import os
import string
import sys
import wx
from wax.treeview import TreeView
from wax.imagelist import ImageList

class ShowAllFileTreeView(TreeView):
    def __init__(self, parent, rootdir="/"):
        TreeView.__init__(self, parent)
        self.rootdir = rootdir

        imagelist = ImageList(16, 16)
        imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16,16)), 'folder')
        imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16,16)), 'folder_open')
        imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16,16)), 'file')
        self.SetImageList(imagelist)
        self.MakeRoot()

    def SetImages(self, node, isdir):
        if isdir:
            self.SetItemImage(node, self._imagelist['folder'], expanded=0)
            self.SetItemImage(node, self._imagelist['folder_open'], expanded=1)
        else:
            self.SetItemImage(node, self._imagelist['file'])

    def MakeRoot(self):
        """ Add the toplevel nodes to the tree.  For Unix, this is simple:
            get the root directory, and look at the subdirectories there.
            For Windows, however, we have to get the available drive letters. """
        self.Clear()
        self.root = self.AddRoot(self.rootdir)
        self.SetImages(self.root, True)

        # get a list of tuples (short, long)
        if sys.platform == 'win32':
            a = self._win32_get_drive_letters()
            children = [(d, d, True) for d in a]
        else:
            children = self.GetChildren(self.rootdir)

        self.AddChildren(self.root, children)
        self.Expand(self.root)

    def _win32_get_drive_letters(self):
        drives = []
        try:
            # check if win32all is available
            import win32api
        except ImportError:
            # if not, use os.path.exists to determine if drives exist
            # however, this may bring up an error dialog if there is no disk
            # in A:\
            for letter in string.uppercase:
                drive = letter + ":\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            drives = win32api.GetLogicalDriveStrings()
            drives = filter(None, string.splitfields(drives, "\000"))

        return drives

    def AddChildren(self, node, children):
        for short, long, isdir in children:
            child = self.AppendItem(node, short)
            self.SetPyData(child, long)
            self.SetImages(child, isdir)

    def GetChildren(self, path):
        files = os.listdir(path)
        files = [(f, os.path.join(path, f), os.path.isdir(os.path.join(path, f))) for f in files]
        return sorted(files, key=lambda x:(-x[2], x[0]))

    def OnItemActivated(self, event):
        print dir(event), event.GetEventObject()

    def OnSelectionChanged(self, event):
        node = event.GetItem()
        if not self.HasChildren(node):
            path = self.GetPyData(node)
            children = self.GetChildren(path)
            self.AddChildren(node, children)
            self.Expand(node)
            self.Refresh()

