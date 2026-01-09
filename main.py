import tkinter as tk
from tkinter import ttk

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_main_container()
        
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
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = tk.Frame(self.root, bg="#2d2d2d", height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # New file button
        btn_new = tk.Button(toolbar, text="New", command=self.file_new, 
                           bg="#3d3d3d", fg="white", relief=tk.FLAT, padx=10)
        btn_new.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Open file button
        btn_open = tk.Button(toolbar, text="Open", command=self.file_open,
                            bg="#3d3d3d", fg="white", relief=tk.FLAT, padx=10)
        btn_open.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Save button
        btn_save = tk.Button(toolbar, text="Save", command=self.file_save,
                            bg="#3d3d3d", fg="white", relief=tk.FLAT, padx=10)
        btn_save.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Run button
        btn_run = tk.Button(toolbar, text="Run", command=self.run_code,
                           bg="#3d3d3d", fg="white", relief=tk.FLAT, padx=10)
        btn_run.pack(side=tk.LEFT, padx=2, pady=5)
    
    def create_main_container(self):
        """Create the main container with resizable panes"""
        # Create PanedWindow for resizable layout
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, 
                                           sashwidth=5, bg="#2d2d2d")
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left pane for file explorer
        self.left_pane = tk.Frame(self.paned_window, bg="#252526", width=250)
        self.paned_window.add(self.left_pane, minsize=200)
        
        # Right pane for editor area
        self.right_pane = tk.Frame(self.paned_window, bg="#1e1e1e")
        self.paned_window.add(self.right_pane, minsize=400)
    
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

        
    # Run button placeholder function
    def run_code(self):
        pass

def main():
    root = tk.Tk()
    app = CodeEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
