import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.sidebar_visible = True
        self.open_tabs = {}  # Track file paths for each tab
        self.untitled_count = 0
        self.setup_window()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_main_container()
        self.create_file_explorer()
        self.create_notebook()
        
    def setup_window(self):
        """Initialize the main window"""
        # Set window title
        self.root.title("Code Editor")
        
        # Set window size
        self.root.geometry("1200x700")
        
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
    
    def create_file_explorer(self):
        """Create the file explorer sidebar"""
        # Title label
        title_frame = tk.Frame(self.left_pane, bg="#252526")
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(title_frame, text="EXPLORER", 
                              bg="#252526", fg="#cccccc", font=("Arial", 9, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Create Treeview for file structure
        tree_frame = tk.Frame(self.left_pane, bg="#252526")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview widget
        self.file_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Configure Treeview style
        style = ttk.Style()
        style.configure("Treeview", background="#252526", 
                       foreground="#cccccc", fieldbackground="#252526")
        
        # Bind events
        self.file_tree.bind("<<TreeviewOpen>>", self.on_folder_expand)
        self.file_tree.bind("<Double-1>", self.on_file_double_click)
        
        # Populate with current directory
        self.populate_tree()
    
    def populate_tree(self, parent="", path=None):
        """Populate the tree with files and folders"""
        if path is None:
            path = os.getcwd()
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            # Add root
            node = self.file_tree.insert("", "end", text=path, values=[path], open=True)
            parent = node
        
        try:
            items = os.listdir(path)
            # Sort: directories first, then files
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    # Add folder with dummy child to make it expandable
                    node = self.file_tree.insert(parent, "end", text=f"📁 {item}", 
                                                 values=[item_path])
                    self.file_tree.insert(node, "end", text="dummy")  # Dummy child
                else:
                    # Add file
                    self.file_tree.insert(parent, "end", text=f"📄 {item}", 
                                         values=[item_path])
        except PermissionError:
            pass
    
    def on_folder_expand(self, event):
        """Handle folder expansion"""
        item = self.file_tree.focus()
        children = self.file_tree.get_children(item)
        
        # If only has dummy child, populate it
        if len(children) == 1 and self.file_tree.item(children[0])["text"] == "dummy":
            self.file_tree.delete(children[0])
            path = self.file_tree.item(item)["values"][0]
            self.populate_tree(item, path)
    
    def on_file_double_click(self, event):
        """Handle file double-click to open"""
        item = self.file_tree.focus()
        if item:
            values = self.file_tree.item(item)["values"]
            if values:
                path = values[0]
                if os.path.isfile(path):
                    # Open file in editor
                    self.open_file(path)
    
    def create_notebook(self):
        """Create the tabbed notebook for editor"""
        self.notebook = ttk.Notebook(self.right_pane)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab close event (middle-click or button)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)
    
    def create_editor_tab(self, title="Untitled", content="", file_path=None):
        """Create a new editor tab with text widget and line numbers"""
        # Create frame for this tab
        tab_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        
        # Create frame for line numbers and text widget
        editor_frame = tk.Frame(tab_frame, bg="#1e1e1e")
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers widget
        line_numbers = tk.Text(editor_frame, width=4, padx=5, pady=5,
                               bg="#1e1e1e", fg="#858585", 
                               font=("Consolas", 11), state='disabled',
                               takefocus=0, bd=0, highlightthickness=0)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create text widget with scrollbars
        text_frame = tk.Frame(editor_frame, bg="#1e1e1e")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(text_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Text widget
        text_widget = tk.Text(text_frame, wrap=tk.NONE,
                             undo=True, maxundo=-1,
                             bg="#1e1e1e", fg="#d4d4d4",
                             insertbackground="white",
                             font=("Consolas", 11),
                             yscrollcommand=v_scrollbar.set,
                             xscrollcommand=h_scrollbar.set,
                             selectbackground="#264f78",
                             bd=0, padx=5, pady=5)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.on_scroll(text_widget, line_numbers))
        h_scrollbar.config(command=text_widget.xview)
        
        # Configure syntax highlighting tags
        self.configure_syntax_tags(text_widget)
        
        # Insert content
        text_widget.insert("1.0", content)
        
        # Bind events for line numbers and syntax highlighting
        text_widget.bind("<<Modified>>", lambda e: self.on_text_modified(text_widget, line_numbers))
        text_widget.bind("<KeyRelease>", lambda e: self.apply_syntax_highlighting(text_widget))
        
        # Add tab to notebook
        self.notebook.add(tab_frame, text=title)
        self.notebook.select(tab_frame)
        
        # Store tab info
        tab_id = str(tab_frame)
        self.open_tabs[tab_id] = {
            'text_widget': text_widget,
            'line_numbers': line_numbers,
            'file_path': file_path,
            'title': title,
            'modified': False
        }
        
        # Update line numbers initially
        self.update_line_numbers(text_widget, line_numbers)
        self.apply_syntax_highlighting(text_widget)
        
        return tab_frame
    
    def on_scroll(self, text_widget, line_numbers):
        """Synchronize scrolling between text widget and line numbers"""
        def scroll(*args):
            text_widget.yview(*args)
            line_numbers.yview(*args)
        return scroll
    
    def on_text_modified(self, text_widget, line_numbers):
        """Handle text modifications"""
        if text_widget.edit_modified():
            self.update_line_numbers(text_widget, line_numbers)
            self.mark_tab_modified(text_widget)
            text_widget.edit_modified(False)
    
    def update_line_numbers(self, text_widget, line_numbers):
        """Update line numbers display"""
        line_numbers.config(state='normal')
        line_numbers.delete("1.0", tk.END)
        
        # Get number of lines
        line_count = int(text_widget.index('end-1c').split('.')[0])
        
        # Generate line numbers
        line_nums = "\n".join(str(i) for i in range(1, line_count + 1))
        line_numbers.insert("1.0", line_nums)
        
        line_numbers.config(state='disabled')
    
    def configure_syntax_tags(self, text_widget):
        """Configure syntax highlighting tags"""
        text_widget.tag_configure("keyword", foreground="#569cd6")
        text_widget.tag_configure("string", foreground="#ce9178")
        text_widget.tag_configure("comment", foreground="#6a9955")
        text_widget.tag_configure("number", foreground="#b5cea8")
        text_widget.tag_configure("function", foreground="#dcdcaa")
    
    def apply_syntax_highlighting(self, text_widget):
        """Apply syntax highlighting for Python"""
        # Remove existing tags
        for tag in ["keyword", "string", "comment", "number", "function"]:
            text_widget.tag_remove(tag, "1.0", tk.END)
        
        content = text_widget.get("1.0", tk.END)
        
        # Highlight comments
        for match in re.finditer(r'#.*$', content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            text_widget.tag_add("comment", start, end)
        
        # Highlight strings (single and double quotes)
        for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            text_widget.tag_add("string", start, end)
        
        # Highlight keywords
        keywords = r'\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|finally|with|lambda|yield|pass|break|continue|and|or|not|in|is|None|True|False)\b'
        for match in re.finditer(keywords, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            text_widget.tag_add("keyword", start, end)
        
        # Highlight numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            text_widget.tag_add("number", start, end)
        
        # Highlight function definitions
        for match in re.finditer(r'\bdef\s+(\w+)', content):
            start = f"1.0+{match.start(1)}c"
            end = f"1.0+{match.end(1)}c"
            text_widget.tag_add("function", start, end)
    
    def mark_tab_modified(self, text_widget):
        """Mark tab as modified"""
        for tab_id, tab_info in self.open_tabs.items():
            if tab_info['text_widget'] == text_widget and not tab_info['modified']:
                tab_info['modified'] = True
                # Find tab index
                for i in range(self.notebook.index('end')):
                    if str(self.notebook.nametowidget(self.notebook.tabs()[i])) == tab_id:
                        current_title = self.notebook.tab(i, 'text')
                        if not current_title.startswith('• '):
                            self.notebook.tab(i, text='• ' + current_title)
                        break
    
    def on_tab_right_click(self, event):
        """Handle right-click on tab to close"""
        try:
            clicked_tab = self.notebook.index(f"@{event.x},{event.y}")
            self.close_tab(clicked_tab)
        except:
            pass
    
    def close_tab(self, tab_index):
        """Close a tab"""
        if self.notebook.index('end') > 0:
            tab_id = str(self.notebook.nametowidget(self.notebook.tabs()[tab_index]))
            if tab_id in self.open_tabs:
                # Check if modified
                if self.open_tabs[tab_id]['modified']:
                    response = messagebox.askyesnocancel(
                        "Unsaved Changes",
                        f"Save changes to {self.open_tabs[tab_id]['title']}?"
                    )
                    if response is True:  # Yes
                        self.save_current_tab()
                    elif response is None:  # Cancel
                        return
                
                del self.open_tabs[tab_id]
            
            self.notebook.forget(tab_index)
    
    def get_current_tab_info(self):
        """Get info for currently selected tab"""
        try:
            current_tab = self.notebook.select()
            if current_tab:
                tab_id = str(self.notebook.nametowidget(current_tab))
                return self.open_tabs.get(tab_id)
        except:
            pass
        return None
    
    def save_current_tab(self):
        """Save the current tab"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            text_widget = tab_info['text_widget']
            file_path = tab_info['file_path']
            
            if file_path:
                # Save to existing path
                try:
                    content = text_widget.get("1.0", "end-1c")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    tab_info['modified'] = False
                    # Remove modified indicator
                    for i in range(self.notebook.index('end')):
                        if str(self.notebook.nametowidget(self.notebook.tabs()[i])) == str(self.notebook.select()):
                            title = self.notebook.tab(i, 'text').replace('• ', '')
                            self.notebook.tab(i, text=title)
                            break
                    messagebox.showinfo("Success", "File saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            else:
                # New file, prompt for location
                self.save_as_current_tab()
    
    def save_as_current_tab(self):
        """Save current tab with new filename"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            
            if file_path:
                try:
                    text_widget = tab_info['text_widget']
                    content = text_widget.get("1.0", "end-1c")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Update tab info
                    tab_info['file_path'] = file_path
                    tab_info['title'] = os.path.basename(file_path)
                    tab_info['modified'] = False
                    
                    # Update tab title
                    for i in range(self.notebook.index('end')):
                        if str(self.notebook.nametowidget(self.notebook.tabs()[i])) == str(self.notebook.select()):
                            self.notebook.tab(i, text=tab_info['title'])
                            break
                    
                    messagebox.showinfo("Success", "File saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def open_file(self, file_path):
        """Open a file in a new tab"""
        # Check if file is already open
        for tab_info in self.open_tabs.values():
            if tab_info['file_path'] == file_path:
                # Switch to existing tab
                for i, tab in enumerate(self.notebook.tabs()):
                    if str(self.notebook.nametowidget(tab)) in self.open_tabs:
                        tab_id = str(self.notebook.nametowidget(tab))
                        if self.open_tabs[tab_id]['file_path'] == file_path:
                            self.notebook.select(i)
                            return
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create new tab
            title = os.path.basename(file_path)
            self.create_editor_tab(title=title, content=content, file_path=file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    # File menu functions
    def file_new(self):
        """Create a new untitled file"""
        self.untitled_count += 1
        title = f"Untitled-{self.untitled_count}"
        self.create_editor_tab(title=title)
    
    def file_open(self):
        """Open an existing file"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.open_file(file_path)
    
    def file_save(self):
        """Save the current file"""
        self.save_current_tab()
    
    def file_save_as(self):
        """Save the current file with a new name"""
        self.save_as_current_tab()
    
    def file_exit(self):
        self.root.quit()
    
    # Edit menu functions
    def edit_cut(self):
        """Cut selected text"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            tab_info['text_widget'].event_generate("<<Cut>>")
    
    def edit_copy(self):
        """Copy selected text"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            tab_info['text_widget'].event_generate("<<Copy>>")
    
    def edit_paste(self):
        """Paste text"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            tab_info['text_widget'].event_generate("<<Paste>>")
    
    def edit_undo(self):
        """Undo last action"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            try:
                tab_info['text_widget'].edit_undo()
            except:
                pass
    
    def edit_redo(self):
        """Redo last undone action"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            try:
                tab_info['text_widget'].edit_redo()
            except:
                pass
    
    # View menu functions
    def view_toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_visible:
            self.paned_window.forget(self.left_pane)
            self.sidebar_visible = False
        else:
            self.paned_window.add(self.left_pane, before=self.right_pane, minsize=200)
            self.sidebar_visible = True
    
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
