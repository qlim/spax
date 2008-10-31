# options.py

from wax import *

class Options:
    def __init__(self, **kwargs):
        self.extend(**kwargs)
    def extend(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
options = Options(
    editor_width = 80,
    editor_height = 25,
    editor_font = ("Courier New", 10),
    system_font = ("Tahoma", 8),
    autoindent = 1,
    use_tabs = 0,
    tabsize = 4,
    show_line_numbers = 1,
    show_whitespace = 0,
    show_indentguides = 0,
    folding = 0,
    shell_with_filling = 0,
    edge = 80,
    filemask = "Python source (*.py)|*.py|"\
               "Text files (*.txt)|*.txt|"\
               "All files (*.*)|*.*",
    match_braces = 1,
)

# file associations
options.file_assoc = {
    '.py': 'python',
}

# default editor colors
options.editor_default_style = "size:8,face:FixedSys,fore:#B0B0C0,back:#000000"
options.editor_linenumber_style = "fore:#000000,back:#C0C0C0,face:Tahoma,size:8"
options.editor_caret_foreground = (0xE0, 0xE0, 0xE0)
options.editor_selection_foreground = (0x00, 0x00, 0x3F)
options.editor_selection_background = (0xC0, 0xC0, 0xC0)
options.edge_color = (0xC0, 0xC0, 0xC0)
options.bad_brace_style = "fore:#FFFFFF,back:#FF0000"
options.matching_brace_style = "fore:#FFFFFF,back:#0000FF"
    
