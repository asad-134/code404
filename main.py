import tkinter as tk
from tkinter import ttk

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_menu_bar()
        
    def setup_window(self):
        """Initialize the main window"""
        # Set window title
        self.root.title("Code Editor")
        
        # Set window size
        self.root.geometry("1200x800")
        
        # Set minimum dimensions
        self.root.minsize(800, 600)
        
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.file_new)
        file_menu.add_command(label="Open", command=self.file_open)
        file_menu.add_command(label="Save", command=self.file_save)
        file_menu.add_command(label="Save As", command=self.file_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.file_exit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.edit_cut)
        edit_menu.add_command(label="Copy", command=self.edit_copy)
        edit_menu.add_command(label="Paste", command=self.edit_paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.edit_undo)
        edit_menu.add_command(label="Redo", command=self.edit_redo)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Sidebar", command=self.view_toggle_sidebar)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.view_zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.view_zoom_out)
    
    # File menu placeholder functions
    def file_new(self):
        pass
    
    def file_open(self):
        pass
    
    def file_save(self):
        pass
    
    def file_save_as(self):
        pass
    
    def file_exit(self):
        self.root.quit()
    
    # Edit menu placeholder functions
    def edit_cut(self):
        pass
    
    def edit_copy(self):
        pass
    
    def edit_paste(self):
        pass
    
    def edit_undo(self):
        pass
    
    def edit_redo(self):
        pass
    
    # View menu placeholder functions
    def view_toggle_sidebar(self):
        pass
    
    def view_zoom_in(self):
        pass
    
    def view_zoom_out(self):
        pass

        

def main():
    root = tk.Tk()
    app = CodeEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
