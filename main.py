import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import re
import json
import subprocess
import threading
import sys
from utils.ai_service import AIService

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.sidebar_visible = True
        self.open_tabs = {}  # Track file paths for each tab
        self.untitled_count = 0
        self.find_dialog = None
        
        # AI features
        self.ai_service = None
        self.ai_suggestion = ""
        self.ai_suggestion_widget = None
        self.ai_suggestion_start_pos = None  # Track ghost text start position
        self.ai_suggestion_end_pos = None    # Track ghost text end position
        self.suggestion_timer = None
        self.suggestion_delay = 1500  # ms delay before showing suggestion
        self.is_accepting_suggestion = False
        self.ai_explanation_panel = None
        self.ai_panel_visible = False
        self.chat_history = []  # Store chat conversation history
        
        # Define themes
        self.themes = {
            'dark': {
                'bg': '#1e1e1e',
                'fg': '#d4d4d4',
                'sidebar_bg': '#252526',
                'toolbar_bg': '#2d2d2d',
                'button_bg': '#3d3d3d',
                'status_bg': '#007acc',
                'line_num_bg': '#1e1e1e',
                'line_num_fg': '#858585',
                'select_bg': '#264f78',
                'insert_bg': 'white',
                'keyword': '#569cd6',
                'string': '#ce9178',
                'comment': '#6a9955',
                'number': '#b5cea8',
                'function': '#dcdcaa'
            },
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'sidebar_bg': '#f3f3f3',
                'toolbar_bg': '#e0e0e0',
                'button_bg': '#d0d0d0',
                'status_bg': '#0078d4',
                'line_num_bg': '#f0f0f0',
                'line_num_fg': '#6e6e6e',
                'select_bg': '#add6ff',
                'insert_bg': 'black',
                'keyword': '#0000ff',
                'string': '#a31515',
                'comment': '#008000',
                'number': '#098658',
                'function': '#795e26'
            }
        }
        
        # Load settings
        self.load_settings()
        
        self.setup_window()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_main_container()
        self.create_file_explorer()
        self.create_notebook()
        self.create_status_bar()
        self.setup_keybindings()
        self.initialize_ai_service()
        
    def load_settings(self):
        """Load settings from config file"""
        self.config_file = os.path.join(os.path.dirname(__file__), 'editor_config.json')
        default_settings = {
            'theme': 'dark',
            'font_family': 'Consolas',
            'font_size': 11,
            'tab_width': 4,
            'auto_save_interval': 0,  # 0 = disabled
            'ai_enabled': True,
            'ai_auto_suggest': True,
            'ai_suggestion_delay': 1500
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.settings = json.load(f)
                # Ensure all default keys exist
                for key, value in default_settings.items():
                    if key not in self.settings:
                        self.settings[key] = value
            else:
                self.settings = default_settings
        except:
            self.settings = default_settings
        
        self.current_theme = self.settings.get('theme', 'dark')
    
    def save_settings(self):
        """Save settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
        
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
        edit_menu.add_command(label="Cut", command=self.edit_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.edit_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.edit_paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.show_find_dialog, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.show_replace_dialog, accelerator="Ctrl+H")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Sidebar", command=self.view_toggle_sidebar)
        view_menu.add_command(label="Toggle Terminal", command=self.view_toggle_terminal)
        view_menu.add_separator()
        view_menu.add_command(label="Dark Theme", command=lambda: self.apply_theme('dark'))
        view_menu.add_command(label="Light Theme", command=lambda: self.apply_theme('light'))
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.view_zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.view_zoom_out)
        view_menu.add_separator()
        view_menu.add_command(label="Settings", command=self.show_settings_dialog)
        view_menu.add_separator()
        view_menu.add_command(label="Run Code", command=self.run_code, accelerator="F5")
        
        # AI menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="AI", menu=ai_menu)
        ai_menu.add_command(label="Code Completion", command=self.trigger_ai_completion, accelerator="Ctrl+Space")
        ai_menu.add_command(label="Explain Code", command=self.explain_selected_code, accelerator="Ctrl+Shift+I")
        ai_menu.add_separator()
        ai_menu.add_command(label="Generate Code from Comment", command=self.generate_code_from_comment, accelerator="Ctrl+Shift+G")
        ai_menu.add_command(label="Refactor Code", command=self.refactor_selected_code, accelerator="Ctrl+Shift+R")
        ai_menu.add_command(label="Fix Code Errors", command=self.fix_selected_code, accelerator="Ctrl+Shift+F")
        ai_menu.add_separator()
        ai_menu.add_command(label="Scan File for Bugs", command=self.scan_file_for_bugs, accelerator="Ctrl+Shift+B")
        ai_menu.add_command(label="AI Chat", command=self.show_ai_chat, accelerator="Ctrl+Shift+C")
        ai_menu.add_separator()
        ai_menu.add_command(label="Generate Documentation", command=self.generate_documentation)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_toolbar(self):
        """Create the toolbar"""
        theme = self.themes[self.current_theme]
        self.toolbar = tk.Frame(self.root, bg=theme['toolbar_bg'], height=40)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # New file button
        self.btn_new = tk.Button(self.toolbar, text="New", command=self.file_new, 
                           bg=theme['button_bg'], fg=theme['fg'], relief=tk.FLAT, padx=10)
        self.btn_new.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Open file button
        self.btn_open = tk.Button(self.toolbar, text="Open", command=self.file_open,
                            bg=theme['button_bg'], fg=theme['fg'], relief=tk.FLAT, padx=10)
        self.btn_open.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Save button
        self.btn_save = tk.Button(self.toolbar, text="Save", command=self.file_save,
                            bg=theme['button_bg'], fg=theme['fg'], relief=tk.FLAT, padx=10)
        self.btn_save.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Run button
        self.btn_run = tk.Button(self.toolbar, text="Run", command=self.run_code,
                           bg=theme['button_bg'], fg=theme['fg'], relief=tk.FLAT, padx=10)
        self.btn_run.pack(side=tk.LEFT, padx=2, pady=5)
    
    def create_main_container(self):
        """Create the main container with resizable panes"""
        # Create PanedWindow for resizable layout
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, 
                                           sashwidth=5, bg="#2d2d2d")
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left pane for file explorer
        self.left_pane = tk.Frame(self.paned_window, bg="#252526", width=250)
        self.paned_window.add(self.left_pane, minsize=200)
        
        # Right pane - split into editor and terminal
        self.right_pane = tk.Frame(self.paned_window, bg="#1e1e1e")
        self.paned_window.add(self.right_pane, minsize=400)
        
        # Create horizontal paned window for editor/terminal and AI panel
        self.main_right_pane = tk.PanedWindow(self.right_pane, orient=tk.HORIZONTAL,
                                              sashwidth=5, bg="#2d2d2d")
        self.main_right_pane.pack(fill=tk.BOTH, expand=True)
        
        # Left side: editor and terminal
        self.editor_terminal_container = tk.Frame(self.main_right_pane, bg="#1e1e1e")
        self.main_right_pane.add(self.editor_terminal_container, minsize=400)
        
        # Create vertical paned window for editor and terminal
        self.editor_terminal_pane = tk.PanedWindow(self.editor_terminal_container, orient=tk.VERTICAL,
                                                    sashwidth=5, bg="#2d2d2d")
        self.editor_terminal_pane.pack(fill=tk.BOTH, expand=True)
        
        # Editor container
        self.editor_container = tk.Frame(self.editor_terminal_pane, bg="#1e1e1e")
        self.editor_terminal_pane.add(self.editor_container, minsize=300)
        
        # Terminal container
        self.terminal_container = tk.Frame(self.editor_terminal_pane, bg="#1e1e1e", height=200)
        self.editor_terminal_pane.add(self.terminal_container, minsize=100)
        
        # Create terminal widget
        self.create_terminal()
    
    def create_terminal(self):
        """Create the integrated terminal"""
        theme = self.themes[self.current_theme]
        
        # Terminal title bar
        terminal_title = tk.Frame(self.terminal_container, bg=theme['toolbar_bg'], height=25)
        terminal_title.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(terminal_title, text="TERMINAL", bg=theme['toolbar_bg'], 
                fg=theme['fg'], font=("Arial", 9, "bold"), padx=10).pack(side=tk.LEFT)
        
        # Clear button
        clear_btn = tk.Button(terminal_title, text="Clear", command=self.clear_terminal,
                             bg=theme['button_bg'], fg=theme['fg'], relief=tk.FLAT, padx=8)
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Terminal text widget
        terminal_frame = tk.Frame(self.terminal_container, bg=theme['bg'])
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(terminal_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.terminal_output = tk.Text(terminal_frame, 
                                        bg="#000000", fg="#00ff00",
                                        font=("Consolas", 10),
                                        yscrollcommand=scrollbar.set,
                                        state='disabled',
                                        wrap=tk.WORD)
        self.terminal_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.terminal_output.yview)
    
    def clear_terminal(self):
        """Clear terminal output"""
        self.terminal_output.config(state='normal')
        self.terminal_output.delete("1.0", tk.END)
        self.terminal_output.config(state='disabled')
    
    def append_terminal_output(self, text, color="#00ff00"):
        """Append text to terminal output"""
        self.terminal_output.config(state='normal')
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state='disabled')
    
    def create_file_explorer(self):
        """Create the file explorer sidebar"""
        # Title label
        title_frame = tk.Frame(self.left_pane, bg="#1e1e1e")
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(title_frame, text="EXPLORER", 
                              bg="#1e1e1e", fg="#cccccc", font=("Arial", 9, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Create Treeview for file structure
        tree_frame = tk.Frame(self.left_pane, bg="#1e1e1e")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Configure Treeview style BEFORE creating the widget
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better customization
        style.configure("Treeview", 
                       background="#1e1e1e", 
                       foreground="#cccccc", 
                       fieldbackground="#1e1e1e",
                       borderwidth=0, 
                       relief="flat")
        style.map("Treeview", background=[("selected", "#094771")])
        
        # Treeview widget
        self.file_tree = ttk.Treeview(tree_frame, yscrollcommand=lambda *args: scrollbar.set(*args))
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(tree_frame, bg="#2d2d2d", troughcolor="#1e1e1e", 
                                activebackground="#3e3e3e", highlightthickness=0, 
                                bd=0, relief=tk.FLAT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar.config(command=self.file_tree.yview)
        
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
    
    def show_file_context_menu(self, event):
        """Show context menu on right-click in file explorer"""
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            values = self.file_tree.item(item)["values"]
            
            if not values:
                return
            
            path = values[0]
            is_dir = os.path.isdir(path)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            
            if is_dir:
                context_menu.add_command(label="New File", 
                                        command=lambda: self.create_new_file_in_folder(path))
                context_menu.add_command(label="New Folder", 
                                        command=lambda: self.create_new_folder_in_folder(path))
                context_menu.add_separator()
            
            context_menu.add_command(label="Rename", 
                                    command=lambda: self.rename_file_or_folder(item, path))
            context_menu.add_command(label="Delete", 
                                    command=lambda: self.delete_file_or_folder(item, path))
            context_menu.add_separator()
            context_menu.add_command(label="Refresh", command=self.refresh_tree)
            
            context_menu.tk_popup(event.x_root, event.y_root)
    
    def create_new_file_in_folder(self, folder_path):
        """Create a new file in the specified folder"""
        file_name = tk.simpledialog.askstring("New File", "Enter file name:")
        if file_name:
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.refresh_tree()
                self.open_file(file_path)
                messagebox.showinfo("Success", f"File created: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file: {str(e)}")
    
    def create_new_folder_in_folder(self, parent_path):
        """Create a new folder in the specified folder"""
        folder_name = tk.simpledialog.askstring("New Folder", "Enter folder name:")
        if folder_name:
            folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.refresh_tree()
                messagebox.showinfo("Success", f"Folder created: {folder_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {str(e)}")
    
    def rename_file_or_folder(self, item, old_path):
        """Rename a file or folder"""
        old_name = os.path.basename(old_path)
        new_name = tk.simpledialog.askstring("Rename", f"Rename '{old_name}' to:", 
                                              initialvalue=old_name)
        if new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh_tree()
                
                # Update open tabs if file was renamed
                for tab_info in self.open_tabs.values():
                    if tab_info['file_path'] == old_path:
                        tab_info['file_path'] = new_path
                        tab_info['title'] = new_name
                
                messagebox.showinfo("Success", f"Renamed to: {new_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename: {str(e)}")
    
    def delete_file_or_folder(self, item, path):
        """Delete a file or folder"""
        name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        
        response = messagebox.askyesno("Delete", 
                                       f"Are you sure you want to delete '{name}'?")
        if response:
            try:
                if is_dir:
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                
                self.refresh_tree()
                
                # Close tabs for deleted files
                tabs_to_close = []
                for tab_id, tab_info in self.open_tabs.items():
                    if tab_info['file_path'] == path:
                        tabs_to_close.append(tab_id)
                
                for tab_id in tabs_to_close:
                    for i, tab in enumerate(self.notebook.tabs()):
                        if str(self.notebook.nametowidget(tab)) == tab_id:
                            self.close_tab(i)
                            break
                
                messagebox.showinfo("Success", f"Deleted: {name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def refresh_tree(self):
        """Refresh the file tree"""
        self.populate_tree()
    
    def create_notebook(self):
        """Create the tabbed notebook for editor"""
        self.notebook = ttk.Notebook(self.editor_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab close events
        self.notebook.bind("<Button-3>", self.on_tab_right_click)
        self.notebook.bind("<Button-2>", self.on_tab_middle_click)  # Middle-click to close
    
    def on_tab_middle_click(self, event):
        """Handle middle-click on tab to close"""
        try:
            clicked_tab = self.notebook.index(f"@{event.x},{event.y}")
            self.close_tab(clicked_tab)
        except:
            pass
    
    def create_editor_tab(self, title="Untitled", content="", file_path=None):
        """Create a new editor tab with text widget and line numbers"""
        theme = self.themes[self.current_theme]
        font = (self.settings['font_family'], self.settings['font_size'])
        
        # Create frame for this tab
        tab_frame = tk.Frame(self.notebook, bg=theme['bg'])
        
        # Create frame for line numbers and text widget
        editor_frame = tk.Frame(tab_frame, bg=theme['bg'])
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers widget
        line_numbers = tk.Text(editor_frame, width=4, padx=5, pady=5,
                               bg=theme['line_num_bg'], fg=theme['line_num_fg'], 
                               font=font, state='disabled',
                               takefocus=0, bd=0, highlightthickness=0)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create text widget with scrollbars
        text_frame = tk.Frame(editor_frame, bg=theme['bg'])
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
                             bg=theme['bg'], fg=theme['fg'],
                             insertbackground=theme['insert_bg'],
                             font=font,
                             yscrollcommand=v_scrollbar.set,
                             xscrollcommand=h_scrollbar.set,
                             selectbackground=theme['select_bg'],
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
        
        # Bind cursor movement events for status bar
        text_widget.bind("<KeyRelease>", lambda e: self.update_status_bar(text_widget), add='+')
        text_widget.bind("<ButtonRelease-1>", lambda e: self.update_status_bar(text_widget))
        
        # AI code completion bindings
        text_widget.bind("<KeyRelease>", lambda e: self.on_key_release_for_ai(e, text_widget), add='+')
        text_widget.bind("<Tab>", lambda e: self.accept_ai_suggestion(text_widget))
        text_widget.bind("<Escape>", lambda e: self.reject_ai_suggestion(text_widget))
        
        # Clear ghost text on any interaction
        text_widget.bind("<Button-1>", lambda e: self.on_mouse_click(e, text_widget))
        text_widget.bind("<ButtonRelease-1>", lambda e: None)  # Prevent double trigger
        text_widget.bind("<FocusOut>", lambda e: self.clear_ai_suggestion(text_widget), add='+')
        text_widget.bind("<KeyPress>", lambda e: self.on_key_press_clear_ghost(e, text_widget))
        
        # Right-click context menu for AI features
        text_widget.bind("<Button-3>", lambda e: self.show_editor_context_menu(e, text_widget))
        
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
        theme = self.themes[self.current_theme]
        text_widget.tag_configure("keyword", foreground=theme['keyword'])
        text_widget.tag_configure("string", foreground=theme['string'])
        text_widget.tag_configure("comment", foreground=theme['comment'])
        text_widget.tag_configure("number", foreground=theme['number'])
        text_widget.tag_configure("function", foreground=theme['function'])
    
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
            
            # Clear any ghost text before saving
            self.clear_ai_suggestion(text_widget)
            
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
    
    def view_toggle_terminal(self):
        """Toggle terminal visibility"""
        try:
            if self.terminal_container.winfo_ismapped():
                self.editor_terminal_pane.forget(self.terminal_container)
            else:
                self.editor_terminal_pane.add(self.terminal_container, minsize=100)
        except:
            pass
    
    def view_zoom_in(self):
        pass
    
    def view_zoom_out(self):
        pass
    
    def setup_keybindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-n>", lambda e: self.file_new())
        self.root.bind("<Control-o>", lambda e: self.file_open())
        self.root.bind("<Control-s>", lambda e: self.file_save())
        self.root.bind("<Control-Shift-S>", lambda e: self.file_save_as())
        self.root.bind("<Control-w>", lambda e: self.close_current_tab())
        
        self.root.bind("<Control-z>", lambda e: self.edit_undo())
        self.root.bind("<Control-y>", lambda e: self.edit_redo())
        self.root.bind("<Control-Shift-Z>", lambda e: self.edit_redo())
        
        self.root.bind("<Control-x>", lambda e: self.edit_cut())
        self.root.bind("<Control-c>", lambda e: self.edit_copy())
        self.root.bind("<Control-v>", lambda e: self.edit_paste())
        
        self.root.bind("<F5>", lambda e: self.run_code())
        
        self.root.bind("<Control-f>", lambda e: self.show_find_dialog())
        self.root.bind("<Control-h>", lambda e: self.show_replace_dialog())
        
        # AI shortcuts
        self.root.bind("<Control-space>", lambda e: self.trigger_ai_completion())
        self.root.bind("<Control-Shift-I>", lambda e: self.explain_selected_code())
        self.root.bind("<Control-Shift-G>", lambda e: self.generate_code_from_comment())
        self.root.bind("<Control-Shift-R>", lambda e: self.refactor_selected_code())
        self.root.bind("<Control-Shift-F>", lambda e: self.fix_selected_code())
        self.root.bind("<Control-Shift-B>", lambda e: self.scan_file_for_bugs())
        self.root.bind("<Control-Shift-C>", lambda e: self.show_ai_chat())
        
        # Tab switching
        self.root.bind("<Control-Tab>", lambda e: self.next_tab())
        self.root.bind("<Control-Shift-Tab>", lambda e: self.prev_tab())
    
    def close_current_tab(self):
        """Close the currently selected tab"""
        try:
            current = self.notebook.index(self.notebook.select())
            self.close_tab(current)
        except:
            pass
    
    def next_tab(self):
        """Switch to next tab"""
        try:
            current = self.notebook.index(self.notebook.select())
            total = self.notebook.index('end')
            if total > 0:
                next_tab = (current + 1) % total
                self.notebook.select(next_tab)
        except:
            pass
    
    def prev_tab(self):
        """Switch to previous tab"""
        try:
            current = self.notebook.index(self.notebook.select())
            total = self.notebook.index('end')
            if total > 0:
                prev_tab = (current - 1) % total
                self.notebook.select(prev_tab)
        except:
            pass
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        theme = self.themes[self.current_theme]
        self.status_bar = tk.Frame(self.root, bg=theme['status_bg'], height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Left section: File path/status messages
        self.status_left = tk.Label(self.status_bar, text="Ready", 
                                     bg=theme['status_bg'], fg="white", anchor=tk.W, padx=10)
        self.status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Center section: File type
        self.status_center = tk.Label(self.status_bar, text="Python", 
                                       bg=theme['status_bg'], fg="white", padx=10)
        self.status_center.pack(side=tk.LEFT)
        
        # Right section: Line and column numbers
        self.status_right = tk.Label(self.status_bar, text="Ln 1, Col 1", 
                                      bg=theme['status_bg'], fg="white", anchor=tk.E, padx=10)
        self.status_right.pack(side=tk.RIGHT)
    
    def update_status_bar(self, text_widget):
        """Update status bar with current cursor position"""
        try:
            # Get cursor position
            cursor_pos = text_widget.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.status_right.config(text=f"Ln {line}, Col {int(col) + 1}")
            
            # Update file path if available
            tab_info = self.get_current_tab_info()
            if tab_info:
                file_path = tab_info.get('file_path', 'Untitled')
                if file_path:
                    self.status_left.config(text=file_path)
                else:
                    self.status_left.config(text=tab_info['title'])
        except:
            pass
    
    def show_find_dialog(self):
        """Show find dialog"""
        if self.find_dialog and self.find_dialog.winfo_exists():
            self.find_dialog.lift()
            return
        
        tab_info = self.get_current_tab_info()
        if not tab_info:
            return
        
        self.find_dialog = tk.Toplevel(self.root)
        self.find_dialog.title("Find")
        self.find_dialog.geometry("400x150")
        self.find_dialog.resizable(False, False)
        
        # Find entry
        tk.Label(self.find_dialog, text="Find:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        find_entry = tk.Entry(self.find_dialog, width=30)
        find_entry.grid(row=0, column=1, padx=10, pady=10)
        find_entry.focus()
        
        # Case sensitive checkbox
        case_var = tk.BooleanVar()
        case_check = tk.Checkbutton(self.find_dialog, text="Case sensitive", variable=case_var)
        case_check.grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(self.find_dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        def find_next():
            text_widget = tab_info['text_widget']
            search_text = find_entry.get()
            if not search_text:
                return
            
            # Remove previous highlights
            text_widget.tag_remove("search", "1.0", tk.END)
            
            # Get current cursor position
            start_pos = text_widget.index(tk.INSERT)
            
            # Search for text
            nocase = 0 if case_var.get() else 1
            pos = text_widget.search(search_text, start_pos, tk.END, nocase=nocase)
            
            if pos:
                # Highlight found text
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add("search", pos, end_pos)
                text_widget.tag_config("search", background="yellow", foreground="black")
                text_widget.mark_set(tk.INSERT, end_pos)
                text_widget.see(pos)
            else:
                # Try from beginning
                pos = text_widget.search(search_text, "1.0", tk.END, nocase=nocase)
                if pos:
                    end_pos = f"{pos}+{len(search_text)}c"
                    text_widget.tag_add("search", pos, end_pos)
                    text_widget.tag_config("search", background="yellow", foreground="black")
                    text_widget.mark_set(tk.INSERT, end_pos)
                    text_widget.see(pos)
                else:
                    messagebox.showinfo("Find", "No matches found")
        
        def find_prev():
            text_widget = tab_info['text_widget']
            search_text = find_entry.get()
            if not search_text:
                return
            
            # Remove previous highlights
            text_widget.tag_remove("search", "1.0", tk.END)
            
            # Get current cursor position
            start_pos = text_widget.index(tk.INSERT)
            
            # Search backwards
            nocase = 0 if case_var.get() else 1
            pos = text_widget.search(search_text, start_pos, "1.0", backwards=True, nocase=nocase)
            
            if pos:
                # Highlight found text
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add("search", pos, end_pos)
                text_widget.tag_config("search", background="yellow", foreground="black")
                text_widget.mark_set(tk.INSERT, pos)
                text_widget.see(pos)
            else:
                messagebox.showinfo("Find", "No matches found")
        
        tk.Button(btn_frame, text="Find Next", command=find_next, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Find Previous", command=find_prev, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=self.find_dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to find next
        find_entry.bind("<Return>", lambda e: find_next())
    
    def show_replace_dialog(self):
        """Show find and replace dialog"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            return
        
        replace_dialog = tk.Toplevel(self.root)
        replace_dialog.title("Find and Replace")
        replace_dialog.geometry("400x200")
        replace_dialog.resizable(False, False)
        
        # Find entry
        tk.Label(replace_dialog, text="Find:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        find_entry = tk.Entry(replace_dialog, width=30)
        find_entry.grid(row=0, column=1, padx=10, pady=10)
        find_entry.focus()
        
        # Replace entry
        tk.Label(replace_dialog, text="Replace:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        replace_entry = tk.Entry(replace_dialog, width=30)
        replace_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Case sensitive checkbox
        case_var = tk.BooleanVar()
        case_check = tk.Checkbutton(replace_dialog, text="Case sensitive", variable=case_var)
        case_check.grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(replace_dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        def find_next():
            text_widget = tab_info['text_widget']
            search_text = find_entry.get()
            if not search_text:
                return
            
            # Remove previous highlights
            text_widget.tag_remove("search", "1.0", tk.END)
            
            # Get current cursor position
            start_pos = text_widget.index(tk.INSERT)
            
            # Search for text
            nocase = 0 if case_var.get() else 1
            pos = text_widget.search(search_text, start_pos, tk.END, nocase=nocase)
            
            if pos:
                # Highlight found text
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add("search", pos, end_pos)
                text_widget.tag_config("search", background="yellow", foreground="black")
                text_widget.mark_set(tk.INSERT, end_pos)
                text_widget.see(pos)
                return True
            else:
                # Try from beginning
                pos = text_widget.search(search_text, "1.0", tk.END, nocase=nocase)
                if pos:
                    end_pos = f"{pos}+{len(search_text)}c"
                    text_widget.tag_add("search", pos, end_pos)
                    text_widget.tag_config("search", background="yellow", foreground="black")
                    text_widget.mark_set(tk.INSERT, end_pos)
                    text_widget.see(pos)
                    return True
                else:
                    messagebox.showinfo("Find", "No matches found")
                    return False
        
        def replace():
            text_widget = tab_info['text_widget']
            search_text = find_entry.get()
            replace_text = replace_entry.get()
            
            # Check if current selection matches search text
            try:
                sel_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                if sel_text == search_text or (not case_var.get() and sel_text.lower() == search_text.lower()):
                    text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    text_widget.insert(tk.INSERT, replace_text)
            except:
                pass
            
            # Find next occurrence
            find_next()
        
        def replace_all():
            text_widget = tab_info['text_widget']
            search_text = find_entry.get()
            replace_text = replace_entry.get()
            
            if not search_text:
                return
            
            count = 0
            nocase = 0 if case_var.get() else 1
            pos = "1.0"
            
            while True:
                pos = text_widget.search(search_text, pos, tk.END, nocase=nocase)
                if not pos:
                    break
                
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.delete(pos, end_pos)
                text_widget.insert(pos, replace_text)
                count += 1
                pos = f"{pos}+{len(replace_text)}c"
            
            messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s)")
            replace_dialog.destroy()
        
        tk.Button(btn_frame, text="Find Next", command=find_next, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Replace", command=replace, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Replace All", command=replace_all, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=replace_dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to find next
        find_entry.bind("<Return>", lambda e: find_next())
    
    def apply_theme(self, theme_name):
        """Apply a theme to the editor"""
        if theme_name not in self.themes:
            return
        
        self.current_theme = theme_name
        self.settings['theme'] = theme_name
        self.save_settings()
        
        theme = self.themes[theme_name]
        
        # Update toolbar
        self.toolbar.config(bg=theme['toolbar_bg'])
        for widget in [self.btn_new, self.btn_open, self.btn_save, self.btn_run]:
            widget.config(bg=theme['button_bg'], fg=theme['fg'])
        
        # Update paned window
        self.paned_window.config(bg=theme['toolbar_bg'])
        self.left_pane.config(bg=theme['sidebar_bg'])
        self.right_pane.config(bg=theme['bg'])
        
        # Update status bar
        self.status_bar.config(bg=theme['status_bg'])
        self.status_left.config(bg=theme['status_bg'], fg='white')
        self.status_center.config(bg=theme['status_bg'], fg='white')
        self.status_right.config(bg=theme['status_bg'], fg='white')
        
        # Update all open tabs
        for tab_info in self.open_tabs.values():
            text_widget = tab_info['text_widget']
            line_numbers = tab_info['line_numbers']
            
            # Update text widget
            text_widget.config(
                bg=theme['bg'],
                fg=theme['fg'],
                insertbackground=theme['insert_bg'],
                selectbackground=theme['select_bg']
            )
            
            # Update line numbers
            line_numbers.config(
                bg=theme['line_num_bg'],
                fg=theme['line_num_fg']
            )
            
            # Reconfigure syntax tags
            self.configure_syntax_tags(text_widget)
            
            # Reapply syntax highlighting
            self.apply_syntax_highlighting(text_widget)
        
        messagebox.showinfo("Theme Changed", f"{theme_name.capitalize()} theme applied!")
    
    def show_settings_dialog(self):
        """Show settings/preferences dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        
        # Main frame
        main_frame = tk.Frame(settings_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Font family
        tk.Label(main_frame, text="Font Family:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=10)
        font_var = tk.StringVar(value=self.settings['font_family'])
        font_options = ['Consolas', 'Courier New', 'Monaco', 'Lucida Console', 'DejaVu Sans Mono']
        font_dropdown = ttk.Combobox(main_frame, textvariable=font_var, values=font_options, state='readonly', width=30)
        font_dropdown.grid(row=0, column=1, pady=10, padx=10)
        
        # Font size
        tk.Label(main_frame, text="Font Size:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=10)
        size_var = tk.IntVar(value=self.settings['font_size'])
        size_spinbox = tk.Spinbox(main_frame, from_=8, to=24, textvariable=size_var, width=30)
        size_spinbox.grid(row=1, column=1, pady=10, padx=10)
        
        # Tab width
        tk.Label(main_frame, text="Tab Width (spaces):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=10)
        tab_var = tk.IntVar(value=self.settings['tab_width'])
        tab_spinbox = tk.Spinbox(main_frame, from_=2, to=8, textvariable=tab_var, width=30)
        tab_spinbox.grid(row=2, column=1, pady=10, padx=10)
        
        # Theme
        tk.Label(main_frame, text="Theme:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=10)
        theme_var = tk.StringVar(value=self.settings['theme'])
        theme_dropdown = ttk.Combobox(main_frame, textvariable=theme_var, values=['dark', 'light'], state='readonly', width=30)
        theme_dropdown.grid(row=3, column=1, pady=10, padx=10)
        
        # Auto-save interval
        tk.Label(main_frame, text="Auto-save Interval (sec):", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=10)
        tk.Label(main_frame, text="(0 = disabled)", font=("Arial", 8)).grid(row=5, column=0, sticky=tk.W)
        autosave_var = tk.IntVar(value=self.settings['auto_save_interval'])
        autosave_spinbox = tk.Spinbox(main_frame, from_=0, to=600, textvariable=autosave_var, width=30, increment=30)
        autosave_spinbox.grid(row=4, column=1, pady=10, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def save_settings():
            # Update settings
            self.settings['font_family'] = font_var.get()
            self.settings['font_size'] = size_var.get()
            self.settings['tab_width'] = tab_var.get()
            self.settings['theme'] = theme_var.get()
            self.settings['auto_save_interval'] = autosave_var.get()
            
            # Save to file
            self.save_settings()
            
            # Apply theme if changed
            if self.current_theme != theme_var.get():
                self.apply_theme(theme_var.get())
            
            # Update font in all open tabs
            for tab_info in self.open_tabs.values():
                text_widget = tab_info['text_widget']
                line_numbers = tab_info['line_numbers']
                font = (self.settings['font_family'], self.settings['font_size'])
                text_widget.config(font=font)
                line_numbers.config(font=font)
            
            messagebox.showinfo("Settings", "Settings saved successfully!")
            settings_window.destroy()
        
        def reset_defaults():
            font_var.set('Consolas')
            size_var.set(11)
            tab_var.set(4)
            theme_var.set('dark')
            autosave_var.set(0)
        
        tk.Button(btn_frame, text="Save", command=save_settings, width=12, bg="#0078d4", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reset Defaults", command=reset_defaults, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=settings_window.destroy, width=12).pack(side=tk.LEFT, padx=5)

        
    # Run code function
    def run_code(self):
        """Run the current Python file"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            messagebox.showwarning("No File", "No file is currently open to run.")
            return
        
        # Clear any ghost text first
        text_widget = tab_info.get('text_widget')
        if text_widget:
            self.clear_ai_suggestion(text_widget)
        
        file_path = tab_info.get('file_path')
        
        # If file is not saved, prompt to save
        if not file_path or tab_info.get('modified', False):
            response = messagebox.askyesno("Save File", 
                                          "File must be saved before running. Save now?")
            if response:
                self.file_save()
                # Update file_path after save
                tab_info = self.get_current_tab_info()
                file_path = tab_info.get('file_path')
                if not file_path:
                    return
            else:
                return
        
        # Check if it's a Python file
        if not file_path.endswith('.py'):
            messagebox.showwarning("Not a Python File", 
                                  "Only Python (.py) files can be run.")
            return
        
        # Clear terminal
        self.clear_terminal()
        
        # Add run command to terminal
        self.append_terminal_output(f"Running: {file_path}\n")
        self.append_terminal_output("=" * 60 + "\n")
        
        # Run in a separate thread to avoid blocking UI
        thread = threading.Thread(target=self.execute_python_file, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def execute_python_file(self, file_path):
        """Execute a Python file and capture output"""
        try:
            # Get the directory of the file
            file_dir = os.path.dirname(file_path)
            
            # Run the Python file
            process = subprocess.Popen(
                [sys.executable, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=file_dir,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            def read_output(pipe, prefix=""):
                for line in iter(pipe.readline, ''):
                    if line:
                        self.root.after(0, self.append_terminal_output, prefix + line)
            
            # Read stdout and stderr
            stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "[ERROR] "))
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process to complete
            process.wait()
            stdout_thread.join()
            stderr_thread.join()
            
            # Show completion message
            self.root.after(0, self.append_terminal_output, 
                          f"\n{'=' * 60}\n")
            self.root.after(0, self.append_terminal_output, 
                          f"Process finished with exit code {process.returncode}\n")
            
        except Exception as e:
            self.root.after(0, self.append_terminal_output, 
                          f"\n[ERROR] Failed to run file: {str(e)}\n")
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Keyboard Shortcuts")
        help_window.geometry("500x600")
        help_window.resizable(False, False)
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                       font=("Arial", 10), bg="#f0f0f0", padx=10, pady=10)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)
        
        shortcuts = """KEYBOARD SHORTCUTS

FILE OPERATIONS
Ctrl+N         New File
Ctrl+O         Open File
Ctrl+S         Save File
Ctrl+Shift+S   Save As
Ctrl+W         Close Tab

EDITING
Ctrl+Z         Undo
Ctrl+Y         Redo
Ctrl+Shift+Z   Redo
Ctrl+X         Cut
Ctrl+C         Copy
Ctrl+V         Paste

SEARCH
Ctrl+F         Find
Ctrl+H         Find and Replace

NAVIGATION
Ctrl+Tab       Next Tab
Ctrl+Shift+Tab Previous Tab

VIEW
(Menu) Toggle Sidebar
(Menu) Zoom In
(Menu) Zoom Out

FILE EXPLORER
Double-click   Open File
Right-click    Context Menu
  - New File
  - New Folder
  - Rename
  - Delete
  - Refresh

TAB CLOSING
Right-click    Close Tab
Middle-click   Close Tab
Ctrl+W         Close Current Tab
"""
        
        text.insert("1.0", shortcuts)
        text.config(state='disabled')
        
        # Close button
        tk.Button(help_window, text="Close", command=help_window.destroy,
                 width=10).pack(pady=10)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About Code Editor",
                           "Code Editor v1.0\n\n"
                           "A VS Code-inspired text editor built with Tkinter\n\n"
                           "Features:\n"
                           "• Syntax highlighting for Python\n"
                           "• File explorer with context menu\n"
                           "• Find and replace\n"
                           "• Line numbers\n"
                           "• Multiple tabs\n"
                           "• Status bar\n"
                           "• AI-powered code completion and explanation\n")
    
    # ============================================================================
    # AI SERVICE METHODS (Step 2 & 3)
    # ============================================================================
    
    def initialize_ai_service(self):
        """Initialize the AI service with configuration"""
        try:
            self.ai_service = AIService()
            if self.ai_service.is_available():
                model_info = self.ai_service.get_model_info()
                self.append_terminal_output(f"\n✓ AI Service initialized: {model_info['model']}\n", "#00ff00")
                self.update_status_left(f"AI: {model_info['model'].split('/')[-1]}")
            else:
                self.append_terminal_output("\n⚠ AI Service not available. Check .env configuration.\n", "#ffaa00")
        except Exception as e:
            self.append_terminal_output(f"\n✗ AI initialization failed: {str(e)}\n", "#ff0000")
            self.ai_service = None
    
    def update_status_left(self, message):
        """Update left side of status bar"""
        self.status_left.config(text=message)
    
    def on_mouse_click(self, event, text_widget):
        """Handle mouse click to clear ghost text"""
        # Clear ghost text immediately on click
        if self.ai_suggestion and self.ai_suggestion_widget == text_widget:
            self.clear_ai_suggestion(text_widget)
    
    def on_key_press_clear_ghost(self, event, text_widget):
        """Clear ghost text on any key press (except special keys)"""
        # Don't clear for modifier keys only
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return
        
        # For Tab and Escape, let their specific handlers deal with it
        if event.keysym in ['Tab', 'Escape']:
            return
        
        # Clear ghost text before any other input
        if self.ai_suggestion and self.ai_suggestion_widget == text_widget:
            # Check if we're not accepting the suggestion
            if not self.is_accepting_suggestion:
                self.clear_ai_suggestion(text_widget)
    
    # ============================================================================
    # STEP 4: CODE COMPLETION (Copilot-style)
    # ============================================================================
    
    def on_key_release_for_ai(self, event, text_widget):
        """Handle key release for AI suggestions"""
        # Ignore special keys and when accepting suggestions
        if self.is_accepting_suggestion:
            return
        
        ignored_keys = ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 
                       'Alt_L', 'Alt_R', 'Up', 'Down', 'Left', 'Right',
                       'Home', 'End', 'Page_Up', 'Page_Down', 'Escape', 'Tab']
        
        if event.keysym in ignored_keys:
            self.clear_ai_suggestion(text_widget)
            return
        
        # Check if AI is enabled
        if not self.ai_service or not self.ai_service.is_available():
            return
        
        if not self.settings.get('ai_auto_suggest', True):
            return
        
        # Clear existing suggestion
        self.clear_ai_suggestion(text_widget)
        
        # Cancel previous timer
        if self.suggestion_timer:
            self.root.after_cancel(self.suggestion_timer)
        
        # Set new timer for suggestion
        delay = self.settings.get('ai_suggestion_delay', 1500)
        self.suggestion_timer = self.root.after(delay, 
                                               lambda: self.request_ai_suggestion(text_widget))
    
    def request_ai_suggestion(self, text_widget):
        """Request AI code completion suggestion"""
        try:
            # Clear any existing ghost text first
            self.clear_ai_suggestion(text_widget)
            
            # Get cursor position
            cursor_pos = text_widget.index(tk.INSERT)
            
            # Get code before and after cursor
            code_before = text_widget.get("1.0", cursor_pos)
            code_after = text_widget.get(cursor_pos, tk.END)
            
            # Get current line
            line_start = text_widget.index(f"{cursor_pos} linestart")
            line_end = text_widget.index(f"{cursor_pos} lineend")
            current_line = text_widget.get(line_start, line_end)
            
            # Don't suggest if line is empty or just whitespace
            if not current_line.strip():
                return
            
            # Get file info
            tab_info = self.get_current_tab_info()
            file_name = "untitled"
            language = "python"
            
            if tab_info and tab_info['file_path']:
                file_name = os.path.basename(tab_info['file_path'])
                ext = os.path.splitext(file_name)[1]
                if ext == '.py':
                    language = 'python'
                elif ext == '.js':
                    language = 'javascript'
                elif ext == '.html':
                    language = 'html'
            
            # Show loading indicator
            self.update_status_left("AI: Generating suggestion...")
            
            # Request suggestion in background thread
            def generate_suggestion():
                suggestion = self.ai_service.generate_completion_sync(
                    code_before=code_before,
                    code_after=code_after,
                    current_line=current_line,
                    file_name=file_name,
                    language=language
                )
                
                # Update UI in main thread
                self.root.after(0, lambda: self.show_ai_suggestion(text_widget, suggestion))
            
            # Run in background thread
            thread = threading.Thread(target=generate_suggestion, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Error requesting AI suggestion: {e}")
            self.update_status_left("AI: Error")
    
    def show_ai_suggestion(self, text_widget, suggestion):
        """Display AI suggestion as ghost text"""
        try:
            # Double-check we're still in the right widget
            current_tab = self.get_current_tab_info()
            if not current_tab or current_tab['text_widget'] != text_widget:
                return
            
            if not suggestion or suggestion.strip() == "":
                self.update_status_left("AI: No suggestion")
                return
            
            # Clean up suggestion
            suggestion = suggestion.strip()
            
            # Remove markdown code blocks if present
            if suggestion.startswith('```'):
                lines = suggestion.split('\n')
                suggestion = '\n'.join(lines[1:-1]) if len(lines) > 2 else suggestion
            
            # Clear any existing ghost text
            self.clear_ai_suggestion(text_widget)
            
            self.ai_suggestion = suggestion
            self.ai_suggestion_widget = text_widget
            
            # Get cursor position
            cursor_pos = text_widget.index(tk.INSERT)
            self.ai_suggestion_start_pos = cursor_pos
            
            # Create tag for ghost text with refined appearance
            theme = self.themes[self.current_theme]
            font_family = self.settings.get('font_family', 'Consolas')
            font_size = self.settings.get('font_size', 11)
            
            # Use different colors based on theme
            if self.current_theme == 'dark':
                ghost_color = '#505050'  # Lighter gray for dark theme
            else:
                ghost_color = '#999999'  # Medium gray for light theme
            
            text_widget.tag_configure("ai_suggestion", 
                                     foreground=ghost_color,
                                     background=theme['bg'],
                                     font=(font_family, font_size, 'italic'))
            
            # Temporarily disable undo for ghost text insertion
            text_widget.edit_separator()
            
            # Insert ghost text
            text_widget.insert(cursor_pos, suggestion, "ai_suggestion")
            
            # Store end position
            self.ai_suggestion_end_pos = text_widget.index(tk.INSERT)
            
            # Move cursor back to start (this is crucial)
            text_widget.mark_set(tk.INSERT, cursor_pos)
            text_widget.see(cursor_pos)
            
            # Add another separator so ghost text can be undone separately
            text_widget.edit_separator()
            
            self.update_status_left(f"✨ AI: Tab to accept • Esc to reject")
            
        except Exception as e:
            print(f"Error showing AI suggestion: {e}")
            self.update_status_left("AI: Error displaying suggestion")
    
    def accept_ai_suggestion(self, text_widget):
        """Accept the AI suggestion (Tab key)"""
        if not self.ai_suggestion or self.ai_suggestion_widget != text_widget:
            return None  # Let Tab work normally if no suggestion
        
        try:
            self.is_accepting_suggestion = True
            
            # Get the suggestion before clearing
            suggestion = self.ai_suggestion
            start_pos = self.ai_suggestion_start_pos
            
            # Remove the ghost text first
            self.clear_ai_suggestion(text_widget)
            
            # Now insert as real text
            text_widget.insert(start_pos, suggestion)
            
            # Move cursor to end of inserted text
            end_pos = text_widget.index(f"{start_pos} + {len(suggestion)}c")
            text_widget.mark_set(tk.INSERT, end_pos)
            text_widget.see(end_pos)
            
            self.update_status_left("AI: Suggestion accepted")
            
            self.is_accepting_suggestion = False
            
        except Exception as e:
            print(f"Error accepting suggestion: {e}")
            self.is_accepting_suggestion = False
        
        return "break"  # Prevent default Tab behavior
    
    def reject_ai_suggestion(self, text_widget):
        """Reject the AI suggestion (Escape key)"""
        if self.ai_suggestion and self.ai_suggestion_widget == text_widget:
            self.clear_ai_suggestion(text_widget)
            self.update_status_left("AI: Suggestion rejected")
        return "break"
    
    def clear_ai_suggestion(self, text_widget):
        """Clear any displayed AI suggestion"""
        if not self.ai_suggestion or self.ai_suggestion_widget != text_widget:
            return
        
        try:
            # Method 1: Use stored positions if available
            if self.ai_suggestion_start_pos and self.ai_suggestion_end_pos:
                try:
                    start = self.ai_suggestion_start_pos
                    end = self.ai_suggestion_end_pos
                    
                    # Verify the text at this position has the ghost tag
                    tags = text_widget.tag_names(start)
                    if "ai_suggestion" in tags:
                        text_widget.delete(start, end)
                except tk.TclError:
                    pass  # Position no longer valid
            
            # Method 2: Find all text with ai_suggestion tag
            try:
                ranges = text_widget.tag_ranges("ai_suggestion")
                if ranges:
                    # Delete in reverse order to maintain positions
                    for i in range(len(ranges)-1, -1, -2):
                        if i > 0:
                            text_widget.delete(ranges[i-1], ranges[i])
            except tk.TclError:
                pass
            
            # Method 3: Remove the tag entirely
            text_widget.tag_remove("ai_suggestion", "1.0", tk.END)
            
        except Exception as e:
            print(f"Error clearing ghost text: {e}")
        finally:
            # Always clear the tracking variables
            self.ai_suggestion = ""
            self.ai_suggestion_widget = None
            self.ai_suggestion_start_pos = None
            self.ai_suggestion_end_pos = None
    
    def trigger_ai_completion(self):
        """Manually trigger AI completion (Ctrl+Space)"""
        tab_info = self.get_current_tab_info()
        if tab_info:
            text_widget = tab_info['text_widget']
            self.clear_ai_suggestion(text_widget)
            self.request_ai_suggestion(text_widget)
    
    # ============================================================================
    # STEP 5: CODE EXPLANATION
    # ============================================================================
    
    def show_editor_context_menu(self, event, text_widget):
        """Show context menu with AI options on right-click"""
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # Check if text is selected
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            has_selection = len(selected_text) > 0
        except:
            has_selection = False
        
        # Standard options
        context_menu.add_command(label="Cut", command=lambda: self.edit_cut())
        context_menu.add_command(label="Copy", command=lambda: self.edit_copy())
        context_menu.add_command(label="Paste", command=lambda: self.edit_paste())
        context_menu.add_separator()
        
        # AI options
        if self.ai_service and self.ai_service.is_available():
            if has_selection:
                context_menu.add_command(label="✨ Explain Code (Ctrl+Shift+I)", 
                                        command=lambda: self.explain_selected_code())
                context_menu.add_command(label="✨ Generate from Comment (Ctrl+Shift+G)", 
                                        command=lambda: self.generate_code_from_comment())
                context_menu.add_command(label="✨ Refactor Code (Ctrl+Shift+R)", 
                                        command=lambda: self.refactor_selected_code())
                context_menu.add_command(label="✨ Fix Code (Ctrl+Shift+F)", 
                                        command=lambda: self.fix_selected_code())
            else:
                context_menu.add_command(label="✨ AI Suggestion (Ctrl+Space)", 
                                        command=lambda: self.trigger_ai_completion())
                context_menu.add_command(label="✨ Generate from Comment (Ctrl+Shift+G)", 
                                        command=lambda: self.generate_code_from_comment())
        
        context_menu.post(event.x_root, event.y_root)
    
    def explain_selected_code(self):
        """Explain the selected code using AI"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            return
        
        text_widget = tab_info['text_widget']
        
        # Clear any ghost text first
        self.clear_ai_suggestion(text_widget)
        
        # Get selected text
        try:
            selected_code = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            messagebox.showwarning("No Selection", "Please select code to explain.")
            return
        
        if not selected_code.strip():
            messagebox.showwarning("Empty Selection", "Please select some code to explain.")
            return
        
        if not self.ai_service or not self.ai_service.is_available():
            messagebox.showerror("AI Not Available", "AI service is not initialized.")
            return
        
        # Show explanation dialog
        self.show_code_explanation_dialog(selected_code, tab_info)
    
    def show_code_explanation_dialog(self, code, tab_info):
        """Show AI explanation in right panel"""
        theme = self.themes[self.current_theme]
        
        # Create or show AI explanation panel
        if self.ai_explanation_panel is None:
            self.ai_explanation_panel = tk.Frame(self.main_right_pane, bg=theme['bg'], width=400)
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
            
            # Title bar
            title_frame = tk.Frame(self.ai_explanation_panel, bg=theme['toolbar_bg'], height=35)
            title_frame.pack(side=tk.TOP, fill=tk.X)
            
            tk.Label(title_frame, text="✨ AI Assistant", 
                    bg=theme['toolbar_bg'], fg=theme['fg'],
                    font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, pady=5)
            
            # Close button
            close_btn = tk.Button(title_frame, text="✕", 
                                 command=self.hide_ai_panel,
                                 bg=theme['toolbar_bg'], fg=theme['fg'],
                                 relief=tk.FLAT, padx=8, font=("Arial", 12, "bold"))
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            # Main content frame
            self.ai_content_frame = tk.Frame(self.ai_explanation_panel, bg=theme['bg'])
            self.ai_content_frame.pack(fill=tk.BOTH, expand=True)
        
        elif not self.ai_panel_visible:
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
        
        # Clear previous content
        for widget in self.ai_content_frame.winfo_children():
            widget.destroy()
        
        # Code preview section
        code_frame = tk.LabelFrame(self.ai_content_frame, text="Selected Code:", 
                                   bg=theme['bg'], fg=theme['fg'],
                                   font=("Arial", 9, "bold"), padx=5, pady=5)
        code_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=False)
        
        code_scroll_frame = tk.Frame(code_frame, bg=theme['bg'])
        code_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        code_scrollbar = tk.Scrollbar(code_scroll_frame)
        code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        code_text = tk.Text(code_scroll_frame, height=6, wrap=tk.WORD,
                           bg=theme['line_num_bg'], fg=theme['fg'],
                           font=("Consolas", 9), padx=8, pady=5,
                           yscrollcommand=code_scrollbar.set)
        code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_scrollbar.config(command=code_text.yview)
        
        code_text.insert("1.0", code)
        code_text.config(state='disabled')
        
        # Explanation section
        explanation_frame = tk.LabelFrame(self.ai_content_frame, text="Explanation:",
                                         bg=theme['bg'], fg=theme['fg'],
                                         font=("Arial", 9, "bold"), padx=5, pady=5)
        explanation_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        exp_scroll_frame = tk.Frame(explanation_frame, bg=theme['bg'])
        exp_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        exp_scrollbar = tk.Scrollbar(exp_scroll_frame)
        exp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        explanation_text = tk.Text(exp_scroll_frame, wrap=tk.WORD,
                                   bg=theme['bg'], fg=theme['fg'],
                                   font=("Arial", 10), padx=10, pady=10,
                                   yscrollcommand=exp_scrollbar.set)
        explanation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        exp_scrollbar.config(command=explanation_text.yview)
        
        # Show loading message
        explanation_text.insert("1.0", "⏳ Generating explanation...\n\nPlease wait...")
        explanation_text.config(state='disabled')
        
        # Get file info
        file_name = "untitled"
        language = "python"
        if tab_info['file_path']:
            file_name = os.path.basename(tab_info['file_path'])
            ext = os.path.splitext(file_name)[1]
            language = 'python' if ext == '.py' else 'code'
        
        # Generate explanation in background
        def generate_explanation():
            try:
                explanation = self.ai_service.explain_code(
                    code=code,
                    file_name=file_name,
                    language=language
                )
                
                # Update UI in main thread
                def update_ui():
                    explanation_text.config(state='normal')
                    explanation_text.delete("1.0", tk.END)
                    explanation_text.insert("1.0", explanation)
                    explanation_text.config(state='disabled')
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    explanation_text.config(state='normal')
                    explanation_text.delete("1.0", tk.END)
                    explanation_text.insert("1.0", f"❌ Error: {str(e)}")
                    explanation_text.config(state='disabled')
                
                self.root.after(0, show_error)
        
        # Run in background thread
        thread = threading.Thread(target=generate_explanation, daemon=True)
        thread.start()
    
    def hide_ai_panel(self):
        """Hide the AI explanation panel"""
        if self.ai_explanation_panel and self.ai_panel_visible:
            self.main_right_pane.forget(self.ai_explanation_panel)
            self.ai_panel_visible = False
    
    # ============================================================================
    # STEP 6: CODE GENERATION FROM COMMENTS
    # ============================================================================
    
    def generate_code_from_comment(self):
        """Generate code from TODO comment or description"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            return
        
        text_widget = tab_info['text_widget']
        
        # Clear any ghost text first
        self.clear_ai_suggestion(text_widget)
        
        # Try to get selected text first
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            requirement = selected_text.strip()
            selection_start = text_widget.index(tk.SEL_FIRST)
            selection_end = text_widget.index(tk.SEL_LAST)
            has_selection = True
        except:
            # No selection, try to detect TODO comment on current line
            cursor_pos = text_widget.index(tk.INSERT)
            line_start = text_widget.index(f"{cursor_pos} linestart")
            line_end = text_widget.index(f"{cursor_pos} lineend")
            current_line = text_widget.get(line_start, line_end)
            
            # Check if line contains TODO or a comment
            if 'TODO' in current_line.upper() or current_line.strip().startswith('#'):
                requirement = current_line.strip().lstrip('#').strip()
                selection_start = line_start
                selection_end = line_end
                has_selection = True
            else:
                # Ask user for requirement
                requirement = simpledialog.askstring(
                    "Generate Code",
                    "Enter code requirement or description:",
                    parent=self.root
                )
                if not requirement:
                    return
                cursor_pos = text_widget.index(tk.INSERT)
                selection_start = cursor_pos
                selection_end = cursor_pos
                has_selection = False
        
        if not requirement:
            messagebox.showwarning("No Requirement", "Please provide a code description.")
            return
        
        if not self.ai_service or not self.ai_service.is_available():
            messagebox.showerror("AI Not Available", "AI service is not initialized.")
            return
        
        # Show generation dialog with diff preview
        self.show_code_generation_dialog(requirement, selection_start, selection_end, has_selection, tab_info)
    
    def show_code_generation_dialog(self, requirement, start_pos, end_pos, replace_mode, tab_info):
        """Show dialog with code generation and diff preview"""
        dialog = tk.Toplevel(self.root)
        dialog.title("AI Code Generation")
        dialog.geometry("800x600")
        
        theme = self.themes[self.current_theme]
        dialog.configure(bg=theme['bg'])
        
        # Title bar
        title_frame = tk.Frame(dialog, bg=theme['toolbar_bg'], height=40)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(title_frame, text="⚡ AI Code Generation", 
                bg=theme['toolbar_bg'], fg=theme['fg'],
                font=("Arial", 11, "bold"), padx=10).pack(side=tk.LEFT, pady=8)
        
        # Requirement display
        req_frame = tk.LabelFrame(dialog, text="Requirement:", 
                                  bg=theme['bg'], fg=theme['fg'],
                                  font=("Arial", 9, "bold"))
        req_frame.pack(fill=tk.X, padx=10, pady=5)
        
        req_label = tk.Label(req_frame, text=requirement, 
                            bg=theme['bg'], fg=theme['fg'],
                            font=("Arial", 10), padx=10, pady=5, wraplength=750, justify=tk.LEFT)
        req_label.pack(fill=tk.X)
        
        # Generated code area
        code_frame = tk.LabelFrame(dialog, text="Generated Code:",
                                   bg=theme['bg'], fg=theme['fg'],
                                   font=("Arial", 9, "bold"))
        code_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        code_scroll_frame = tk.Frame(code_frame, bg=theme['bg'])
        code_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        code_scrollbar = tk.Scrollbar(code_scroll_frame)
        code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        generated_code_text = tk.Text(code_scroll_frame, wrap=tk.WORD,
                                      bg=theme['line_num_bg'], fg=theme['fg'],
                                      font=("Consolas", 10), padx=10, pady=10,
                                      yscrollcommand=code_scrollbar.set)
        generated_code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_scrollbar.config(command=generated_code_text.yview)
        
        # Show loading
        generated_code_text.insert("1.0", "⏳ Generating code...\n\nPlease wait...")
        generated_code_text.config(state='disabled')
        
        # Button frame
        button_frame = tk.Frame(dialog, bg=theme['bg'])
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        apply_btn = tk.Button(button_frame, text="✓ Apply to Editor", 
                             state='disabled',
                             bg="#0078d4", fg="white",
                             padx=20, pady=5, font=("Arial", 9, "bold"))
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn = tk.Button(button_frame, text="📋 Copy", 
                            state='disabled',
                            bg=theme['button_bg'], fg=theme['fg'],
                            padx=20, pady=5)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="Close", 
                             command=dialog.destroy,
                             bg=theme['button_bg'], fg=theme['fg'],
                             padx=20, pady=5)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Get context and file info
        cursor_pos = tab_info['text_widget'].index(tk.INSERT)
        context_start = tab_info['text_widget'].index(f"{cursor_pos} - 50 lines")
        context_end = tab_info['text_widget'].index(f"{cursor_pos} + 20 lines")
        context = tab_info['text_widget'].get(context_start, context_end)
        
        file_name = "untitled"
        language = "python"
        if tab_info['file_path']:
            file_name = os.path.basename(tab_info['file_path'])
            ext = os.path.splitext(file_name)[1]
            language = 'python' if ext == '.py' else 'code'
        
        generated_code = [None]  # Use list to store in closure
        
        def apply_code():
            """Apply generated code to editor"""
            if generated_code[0]:
                text_widget = tab_info['text_widget']
                if replace_mode:
                    text_widget.delete(start_pos, end_pos)
                text_widget.insert(start_pos, generated_code[0])
                dialog.destroy()
                messagebox.showinfo("Success", "Code applied to editor!")
        
        def copy_code():
            """Copy generated code to clipboard"""
            if generated_code[0]:
                self.root.clipboard_clear()
                self.root.clipboard_append(generated_code[0])
                messagebox.showinfo("Copied", "Code copied to clipboard!")
        
        apply_btn.config(command=apply_code)
        copy_btn.config(command=copy_code)
        
        # Generate code in background
        def generate():
            try:
                result = self.ai_service.generate_code_from_description(
                    requirement=requirement,
                    context=context,
                    file_name=file_name,
                    language=language
                )
                
                # Clean up result
                if result.startswith('```'):
                    lines = result.split('\n')
                    result = '\n'.join(lines[1:-1]) if len(lines) > 2 else result
                
                generated_code[0] = result
                
                # Update UI
                def update_ui():
                    generated_code_text.config(state='normal')
                    generated_code_text.delete("1.0", tk.END)
                    generated_code_text.insert("1.0", result)
                    generated_code_text.config(state='disabled')
                    apply_btn.config(state='normal')
                    copy_btn.config(state='normal')
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    generated_code_text.config(state='normal')
                    generated_code_text.delete("1.0", tk.END)
                    generated_code_text.insert("1.0", f"❌ Error: {str(e)}")
                    generated_code_text.config(state='disabled')
                
                self.root.after(0, show_error)
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    # ============================================================================
    # STEP 7: CODE REFACTORING SUGGESTIONS
    # ============================================================================
    
    def refactor_selected_code(self):
        """Refactor selected code with AI suggestions"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            return
        
        text_widget = tab_info['text_widget']
        
        # Clear any ghost text first
        self.clear_ai_suggestion(text_widget)
        
        # Get selected text
        try:
            selected_code = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            selection_start = text_widget.index(tk.SEL_FIRST)
            selection_end = text_widget.index(tk.SEL_LAST)
        except:
            # No selection, use entire file
            response = messagebox.askyesno(
                "No Selection",
                "No code selected. Analyze entire file?"
            )
            if not response:
                return
            selected_code = text_widget.get("1.0", tk.END)
            selection_start = "1.0"
            selection_end = tk.END
        
        if not selected_code.strip():
            messagebox.showwarning("Empty Selection", "Please select some code to refactor.")
            return
        
        if not self.ai_service or not self.ai_service.is_available():
            messagebox.showerror("AI Not Available", "AI service is not initialized.")
            return
        
        # Show refactoring in AI panel
        self.show_refactoring_panel(selected_code, selection_start, selection_end, tab_info)
    
    def show_refactoring_panel(self, code, start_pos, end_pos, tab_info):
        """Show refactoring suggestions in AI panel"""
        theme = self.themes[self.current_theme]
        
        # Create or show AI panel
        if self.ai_explanation_panel is None:
            self.ai_explanation_panel = tk.Frame(self.main_right_pane, bg=theme['bg'], width=400)
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
            
            # Title bar
            title_frame = tk.Frame(self.ai_explanation_panel, bg=theme['toolbar_bg'], height=35)
            title_frame.pack(side=tk.TOP, fill=tk.X)
            
            tk.Label(title_frame, text="✨ AI Assistant", 
                    bg=theme['toolbar_bg'], fg=theme['fg'],
                    font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, pady=5)
            
            # Close button
            close_btn = tk.Button(title_frame, text="✕", 
                                 command=self.hide_ai_panel,
                                 bg=theme['toolbar_bg'], fg=theme['fg'],
                                 relief=tk.FLAT, padx=8, font=("Arial", 12, "bold"))
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            # Main content frame
            self.ai_content_frame = tk.Frame(self.ai_explanation_panel, bg=theme['bg'])
            self.ai_content_frame.pack(fill=tk.BOTH, expand=True)
        
        elif not self.ai_panel_visible:
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
        
        # Clear previous content
        for widget in self.ai_content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.ai_content_frame, text="🔧 Code Refactoring",
                        bg=theme['bg'], fg=theme['fg'],
                        font=("Arial", 11, "bold"), pady=10)
        title.pack()
        
        # Analysis section
        analysis_frame = tk.LabelFrame(self.ai_content_frame, text="Analysis & Suggestions:",
                                       bg=theme['bg'], fg=theme['fg'],
                                       font=("Arial", 9, "bold"), padx=5, pady=5)
        analysis_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        analysis_scroll_frame = tk.Frame(analysis_frame, bg=theme['bg'])
        analysis_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        analysis_scrollbar = tk.Scrollbar(analysis_scroll_frame)
        analysis_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        analysis_text = tk.Text(analysis_scroll_frame, wrap=tk.WORD,
                               bg=theme['bg'], fg=theme['fg'],
                               font=("Arial", 10), padx=10, pady=10,
                               yscrollcommand=analysis_scrollbar.set)
        analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        analysis_scrollbar.config(command=analysis_text.yview)
        
        # Show loading
        analysis_text.insert("1.0", "⏳ Analyzing code...\n\nPlease wait...")
        analysis_text.config(state='disabled')
        
        # Get file info
        file_name = "untitled"
        language = "python"
        if tab_info['file_path']:
            file_name = os.path.basename(tab_info['file_path'])
            ext = os.path.splitext(file_name)[1]
            language = 'python' if ext == '.py' else 'code'
        
        # Generate refactoring suggestions
        def generate_suggestions():
            try:
                suggestions = self.ai_service.suggest_refactoring(
                    code=code,
                    file_name=file_name,
                    language=language
                )
                
                # Update UI
                def update_ui():
                    analysis_text.config(state='normal')
                    analysis_text.delete("1.0", tk.END)
                    analysis_text.insert("1.0", suggestions)
                    analysis_text.config(state='disabled')
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    analysis_text.config(state='normal')
                    analysis_text.delete("1.0", tk.END)
                    analysis_text.insert("1.0", f"❌ Error: {str(e)}")
                    analysis_text.config(state='disabled')
                
                self.root.after(0, show_error)
        
        thread = threading.Thread(target=generate_suggestions, daemon=True)
        thread.start()
    
    # ============================================================================
    # STEP 8: BUG DETECTION & FIXES (Enhanced)
    # ============================================================================
    
    def fix_selected_code(self):
        """Fix/debug selected code with AI"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            return
        
        text_widget = tab_info['text_widget']
        
        # Clear any ghost text first
        self.clear_ai_suggestion(text_widget)
        
        # Get selected text
        try:
            selected_code = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            selection_start = text_widget.index(tk.SEL_FIRST)
            selection_end = text_widget.index(tk.SEL_LAST)
        except:
            messagebox.showwarning("No Selection", "Please select code to analyze for bugs.")
            return
        
        if not selected_code.strip():
            messagebox.showwarning("Empty Selection", "Please select some code to fix.")
            return
        
        if not self.ai_service or not self.ai_service.is_available():
            messagebox.showerror("AI Not Available", "AI service is not initialized.")
            return
        
        # Ask for error message if any
        error_msg = simpledialog.askstring(
            "Error Message",
            "Enter error message (if any, or leave blank):",
            parent=self.root
        )
        
        # Show bug fix in AI panel
        self.show_bug_fix_panel(selected_code, error_msg or "", selection_start, selection_end, tab_info)
    
    def scan_file_for_bugs(self):
        """Scan entire file for potential bugs and issues"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            messagebox.showwarning("No File", "No file is currently open.")
            return
        
        if not self.ai_service or not self.ai_service.is_available():
            messagebox.showerror("AI Not Available", "AI service is not initialized.")
            return
        
        text_widget = tab_info['text_widget']
        
        # Clear any ghost text first
        self.clear_ai_suggestion(text_widget)
        
        # Get all code
        all_code = text_widget.get("1.0", tk.END)
        
        if not all_code.strip():
            messagebox.showwarning("Empty File", "The file is empty.")
            return
        
        # Show comprehensive bug scan in AI panel
        self.show_bug_scan_panel(all_code, tab_info)
    
    def show_bug_scan_panel(self, code, tab_info):
        """Show comprehensive bug scan with issue list and line highlighting"""
        theme = self.themes[self.current_theme]
        
        # Create or show AI panel
        if self.ai_explanation_panel is None:
            self.ai_explanation_panel = tk.Frame(self.main_right_pane, bg=theme['bg'], width=400)
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
            
            # Title bar
            title_frame = tk.Frame(self.ai_explanation_panel, bg=theme['toolbar_bg'], height=35)
            title_frame.pack(side=tk.TOP, fill=tk.X)
            
            tk.Label(title_frame, text="✨ AI Assistant", 
                    bg=theme['toolbar_bg'], fg=theme['fg'],
                    font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, pady=5)
            
            close_btn = tk.Button(title_frame, text="✕", 
                                 command=self.hide_ai_panel,
                                 bg=theme['toolbar_bg'], fg=theme['fg'],
                                 relief=tk.FLAT, padx=8, font=("Arial", 12, "bold"))
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            self.ai_content_frame = tk.Frame(self.ai_explanation_panel, bg=theme['bg'])
            self.ai_content_frame.pack(fill=tk.BOTH, expand=True)
        
        elif not self.ai_panel_visible:
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
        
        # Clear previous content
        for widget in self.ai_content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.ai_content_frame, text="🔍 Bug Detection Scan",
                        bg=theme['bg'], fg=theme['fg'],
                        font=("Arial", 11, "bold"), pady=10)
        title.pack()
        
        # Status label
        status_label = tk.Label(self.ai_content_frame, text="Scanning code for issues...",
                               bg=theme['bg'], fg="#ffaa00",
                               font=("Arial", 9, "italic"))
        status_label.pack()
        
        # Bug issues section
        issues_frame = tk.LabelFrame(self.ai_content_frame, text="Issues Found:",
                                     bg=theme['bg'], fg=theme['fg'],
                                     font=("Arial", 9, "bold"), padx=5, pady=5)
        issues_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        issues_scroll_frame = tk.Frame(issues_frame, bg=theme['bg'])
        issues_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        issues_scrollbar = tk.Scrollbar(issues_scroll_frame)
        issues_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        issues_text = tk.Text(issues_scroll_frame, wrap=tk.WORD,
                             bg=theme['bg'], fg=theme['fg'],
                             font=("Consolas", 9), padx=10, pady=10,
                             yscrollcommand=issues_scrollbar.set)
        issues_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        issues_scrollbar.config(command=issues_text.yview)
        
        # Configure tags for issues
        issues_text.tag_configure("error", foreground="#ff4444", font=("Consolas", 9, "bold"))
        issues_text.tag_configure("warning", foreground="#ffaa00", font=("Consolas", 9, "bold"))
        issues_text.tag_configure("info", foreground="#4488ff", font=("Consolas", 9, "bold"))
        issues_text.tag_configure("line", foreground="#888888")
        issues_text.tag_configure("clickable", foreground="#4488ff", underline=True)
        
        # Show loading
        issues_text.insert("1.0", "⏳ Analyzing code...\n\nPlease wait...", "info")
        issues_text.config(state='disabled')
        
        # Clear any existing highlights
        text_widget = tab_info['text_widget']
        text_widget.tag_remove("bug_highlight", "1.0", tk.END)
        text_widget.tag_configure("bug_highlight", background="#ff4444", foreground="#ffffff")
        
        # Get file info
        file_name = "untitled"
        language = "python"
        if tab_info['file_path']:
            file_name = os.path.basename(tab_info['file_path'])
            ext = os.path.splitext(file_name)[1]
            language = 'python' if ext == '.py' else 'code'
        
        # Scan for bugs
        def scan_bugs():
            try:
                # Use detect_and_fix_bugs from AI service
                analysis = self.ai_service.detect_and_fix_bugs(
                    code=code,
                    error_message="",
                    file_name=file_name,
                    language=language
                )
                
                # Parse the analysis to extract issues
                issues = self.parse_bug_analysis(analysis)
                
                # Update UI
                def update_ui():
                    issues_text.config(state='normal')
                    issues_text.delete("1.0", tk.END)
                    
                    if not issues:
                        issues_text.insert("1.0", "✓ No critical issues found!\n\n", "info")
                        issues_text.insert(tk.END, analysis)
                        status_label.config(text="Scan complete - No critical issues", fg="#00ff00")
                    else:
                        status_label.config(text=f"Scan complete - {len(issues)} issue(s) found", fg="#ff4444")
                        
                        for idx, issue in enumerate(issues, 1):
                            # Issue header
                            severity = issue.get('severity', 'warning')
                            if severity == 'error':
                                icon = "❌"
                                tag = "error"
                            elif severity == 'warning':
                                icon = "⚠️"
                                tag = "warning"
                            else:
                                icon = "ℹ️"
                                tag = "info"
                            
                            issues_text.insert(tk.END, f"{icon} Issue {idx}: ", tag)
                            issues_text.insert(tk.END, f"{issue.get('title', 'Unknown')}\n", tag)
                            
                            # Line number (clickable)
                            if 'line' in issue:
                                line_num = issue['line']
                                issues_text.insert(tk.END, f"   Line {line_num}", "line")
                                
                                # Make it clickable
                                start_idx = issues_text.index("end-1c linestart")
                                end_idx = issues_text.index("end-1c lineend")
                                issues_text.tag_add(f"click_{idx}", start_idx, end_idx)
                                issues_text.tag_bind(f"click_{idx}", "<Button-1>", 
                                                    lambda e, l=line_num: self.jump_to_line(l, tab_info))
                                issues_text.tag_configure(f"click_{idx}", foreground="#4488ff", underline=True)
                                issues_text.insert(tk.END, " (click to jump)\n")
                                
                                # Highlight the line in editor
                                text_widget.tag_add("bug_highlight", f"{line_num}.0", f"{line_num}.end")
                            else:
                                issues_text.insert(tk.END, "\n")
                            
                            # Description
                            issues_text.insert(tk.END, f"   {issue.get('description', 'No description')}\n")
                            
                            # Fix suggestion
                            if 'fix' in issue:
                                issues_text.insert(tk.END, f"   💡 Fix: {issue['fix']}\n", "info")
                            
                            issues_text.insert(tk.END, "\n")
                        
                        # Add full analysis at the end
                        issues_text.insert(tk.END, "\n" + "="*50 + "\n")
                        issues_text.insert(tk.END, "Full Analysis:\n\n")
                        issues_text.insert(tk.END, analysis)
                    
                    issues_text.config(state='disabled')
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    issues_text.config(state='normal')
                    issues_text.delete("1.0", tk.END)
                    issues_text.insert("1.0", f"❌ Error during scan: {str(e)}", "error")
                    issues_text.config(state='disabled')
                    status_label.config(text="Scan failed", fg="#ff4444")
                
                self.root.after(0, show_error)
        
        thread = threading.Thread(target=scan_bugs, daemon=True)
        thread.start()
    
    def parse_bug_analysis(self, analysis):
        """Parse AI analysis to extract structured issues"""
        issues = []
        
        # Try to extract issues from the analysis
        # This is a simple parser - can be enhanced based on AI response format
        lines = analysis.split('\n')
        current_issue = None
        
        for line in lines:
            line = line.strip()
            
            # Look for common issue indicators
            if any(keyword in line.lower() for keyword in ['error', 'bug', 'issue', 'problem', 'warning']):
                if current_issue:
                    issues.append(current_issue)
                
                current_issue = {
                    'title': line[:80],
                    'description': '',
                    'severity': 'error' if 'error' in line.lower() else 'warning'
                }
            
            # Look for line numbers
            if current_issue and 'line' in line.lower():
                import re
                line_match = re.search(r'line[:\s]+(\d+)', line, re.IGNORECASE)
                if line_match:
                    current_issue['line'] = int(line_match.group(1))
            
            # Look for fix suggestions
            if current_issue and any(keyword in line.lower() for keyword in ['fix', 'solution', 'suggest']):
                current_issue['fix'] = line
            
            # Add to description
            if current_issue and line and not line.startswith('#'):
                current_issue['description'] += line + ' '
        
        if current_issue:
            issues.append(current_issue)
        
        return issues
    
    def jump_to_line(self, line_number, tab_info):
        """Jump to a specific line in the editor"""
        text_widget = tab_info['text_widget']
        
        # Move cursor to line
        text_widget.mark_set(tk.INSERT, f"{line_number}.0")
        text_widget.see(f"{line_number}.0")
        
        # Highlight the line temporarily
        text_widget.tag_remove("current_line_highlight", "1.0", tk.END)
        text_widget.tag_configure("current_line_highlight", background="#ffff00", foreground="#000000")
        text_widget.tag_add("current_line_highlight", f"{line_number}.0", f"{line_number}.end")
        
        # Remove highlight after 2 seconds
        def remove_highlight():
            text_widget.tag_remove("current_line_highlight", "1.0", tk.END)
        
        self.root.after(2000, remove_highlight)
        
        # Focus the text widget
        text_widget.focus_set()
    
    def show_bug_fix_panel(self, code, error_message, start_pos, end_pos, tab_info):
        """Show bug detection and fixes in AI panel"""
        theme = self.themes[self.current_theme]
        
        # Create or show AI panel
        if self.ai_explanation_panel is None:
            self.ai_explanation_panel = tk.Frame(self.main_right_pane, bg=theme['bg'], width=400)
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
            
            # Title bar
            title_frame = tk.Frame(self.ai_explanation_panel, bg=theme['toolbar_bg'], height=35)
            title_frame.pack(side=tk.TOP, fill=tk.X)
            
            tk.Label(title_frame, text="✨ AI Assistant", 
                    bg=theme['toolbar_bg'], fg=theme['fg'],
                    font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, pady=5)
            
            close_btn = tk.Button(title_frame, text="✕", 
                                 command=self.hide_ai_panel,
                                 bg=theme['toolbar_bg'], fg=theme['fg'],
                                 relief=tk.FLAT, padx=8, font=("Arial", 12, "bold"))
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            self.ai_content_frame = tk.Frame(self.ai_explanation_panel, bg=theme['bg'])
            self.ai_content_frame.pack(fill=tk.BOTH, expand=True)
        
        elif not self.ai_panel_visible:
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
        
        # Clear previous content
        for widget in self.ai_content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.ai_content_frame, text="🐛 Bug Detection & Fixes",
                        bg=theme['bg'], fg=theme['fg'],
                        font=("Arial", 11, "bold"), pady=10)
        title.pack()
        
        # Bug analysis section
        bug_frame = tk.LabelFrame(self.ai_content_frame, text="Analysis & Fixes:",
                                  bg=theme['bg'], fg=theme['fg'],
                                  font=("Arial", 9, "bold"), padx=5, pady=5)
        bug_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        bug_scroll_frame = tk.Frame(bug_frame, bg=theme['bg'])
        bug_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        bug_scrollbar = tk.Scrollbar(bug_scroll_frame)
        bug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        bug_text = tk.Text(bug_scroll_frame, wrap=tk.WORD,
                          bg=theme['bg'], fg=theme['fg'],
                          font=("Arial", 10), padx=10, pady=10,
                          yscrollcommand=bug_scrollbar.set)
        bug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        bug_scrollbar.config(command=bug_text.yview)
        
        # Show loading
        bug_text.insert("1.0", "⏳ Analyzing code for bugs...\n\nPlease wait...")
        bug_text.config(state='disabled')
        
        # Get file info
        file_name = "untitled"
        language = "python"
        if tab_info['file_path']:
            file_name = os.path.basename(tab_info['file_path'])
            ext = os.path.splitext(file_name)[1]
            language = 'python' if ext == '.py' else 'code'
        
        # Detect and fix bugs
        def analyze_bugs():
            try:
                analysis = self.ai_service.detect_and_fix_bugs(
                    code=code,
                    error_message=error_message,
                    file_name=file_name,
                    language=language
                )
                
                # Update UI
                def update_ui():
                    bug_text.config(state='normal')
                    bug_text.delete("1.0", tk.END)
                    bug_text.insert("1.0", analysis)
                    bug_text.config(state='disabled')
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    bug_text.config(state='normal')
                    bug_text.delete("1.0", tk.END)
                    bug_text.insert("1.0", f"❌ Error: {str(e)}")
                    bug_text.config(state='disabled')
                
                self.root.after(0, show_error)
        
        thread = threading.Thread(target=analyze_bugs, daemon=True)
        thread.start()
    
    def generate_documentation(self):
        """Generate documentation for selected code"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            return
        
        text_widget = tab_info['text_widget']
        
        # Clear any ghost text first
        self.clear_ai_suggestion(text_widget)
        
        # Get selected text
        try:
            selected_code = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            messagebox.showwarning("No Selection", "Please select code to document.")
            return
        
        if not selected_code.strip():
            messagebox.showwarning("Empty Selection", "Please select some code.")
            return
        
        if not self.ai_service or not self.ai_service.is_available():
            messagebox.showerror("AI Not Available", "AI service is not initialized.")
            return
        
        messagebox.showinfo("Coming Soon", "Documentation generation will be fully implemented soon!\n\nFor now, use 'Explain Code' to understand your code.")
    
    # ============================================================================
    # STEP 9: AI CHAT INTERFACE
    # ============================================================================
    
    def show_ai_chat(self):
        """Show AI chat interface in right panel"""
        if not self.ai_service or not self.ai_service.is_available():
            messagebox.showerror("AI Not Available", "AI service is not initialized.")
            return
        
        theme = self.themes[self.current_theme]
        
        # Create or show AI panel
        if self.ai_explanation_panel is None:
            self.ai_explanation_panel = tk.Frame(self.main_right_pane, bg=theme['bg'], width=400)
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
            
            # Title bar
            title_frame = tk.Frame(self.ai_explanation_panel, bg=theme['toolbar_bg'], height=35)
            title_frame.pack(side=tk.TOP, fill=tk.X)
            
            tk.Label(title_frame, text="✨ AI Assistant", 
                    bg=theme['toolbar_bg'], fg=theme['fg'],
                    font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, pady=5)
            
            close_btn = tk.Button(title_frame, text="✕", 
                                 command=self.hide_ai_panel,
                                 bg=theme['toolbar_bg'], fg=theme['fg'],
                                 relief=tk.FLAT, padx=8, font=("Arial", 12, "bold"))
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            self.ai_content_frame = tk.Frame(self.ai_explanation_panel, bg=theme['bg'])
            self.ai_content_frame.pack(fill=tk.BOTH, expand=True)
        
        elif not self.ai_panel_visible:
            self.main_right_pane.add(self.ai_explanation_panel, minsize=350)
            self.ai_panel_visible = True
        
        # Clear previous content
        for widget in self.ai_content_frame.winfo_children():
            widget.destroy()
        
        # Create chat interface
        self.create_chat_interface(self.ai_content_frame, theme)
    
    def create_chat_interface(self, parent, theme):
        """Create the chat interface UI"""
        # Title
        title_frame = tk.Frame(parent, bg=theme['bg'])
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(title_frame, text="💬 AI Chat",
                bg=theme['bg'], fg=theme['fg'],
                font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        
        # Clear chat button
        clear_btn = tk.Button(title_frame, text="Clear",
                             command=self.clear_chat,
                             bg=theme['button_bg'], fg=theme['fg'],
                             relief=tk.FLAT, padx=10)
        clear_btn.pack(side=tk.RIGHT)
        
        # Chat history display
        chat_frame = tk.Frame(parent, bg=theme['bg'])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        chat_scroll = tk.Scrollbar(chat_frame)
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_display = tk.Text(chat_frame, wrap=tk.WORD,
                                    bg=theme['bg'], fg=theme['fg'],
                                    font=("Arial", 10), padx=10, pady=10,
                                    yscrollcommand=chat_scroll.set,
                                    state='disabled')
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scroll.config(command=self.chat_display.yview)
        
        # Configure tags for chat messages
        self.chat_display.tag_configure("user", foreground="#4488ff", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground="#00ff88", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("code", background=theme['line_num_bg'], 
                                       font=("Consolas", 9), foreground="#ffaa00")
        self.chat_display.tag_configure("timestamp", foreground="#888888", font=("Arial", 8))
        
        # Restore chat history if exists
        if self.chat_history:
            self.chat_display.config(state='normal')
            for msg in self.chat_history:
                self.display_chat_message(msg['role'], msg['content'], restore=True)
            self.chat_display.config(state='disabled')
        else:
            # Welcome message
            self.chat_display.config(state='normal')
            self.chat_display.insert("1.0", "👋 Welcome to AI Chat!\n\n", "assistant")
            self.chat_display.insert(tk.END, "Ask me anything about your code. You can:\n")
            self.chat_display.insert(tk.END, "• Ask questions about programming concepts\n")
            self.chat_display.insert(tk.END, "• Get help with debugging\n")
            self.chat_display.insert(tk.END, "• Request code reviews\n")
            self.chat_display.insert(tk.END, "• Attach code by selecting it first\n\n")
            self.chat_display.config(state='disabled')
        
        # Input area
        input_frame = tk.Frame(parent, bg=theme['bg'])
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Context indicator
        self.context_label = tk.Label(input_frame, text="", 
                                      bg=theme['bg'], fg="#ffaa00",
                                      font=("Arial", 8))
        self.context_label.pack(fill=tk.X)
        
        # Input box
        input_container = tk.Frame(input_frame, bg=theme['bg'])
        input_container.pack(fill=tk.X, pady=5)
        
        self.chat_input = tk.Text(input_container, height=3, wrap=tk.WORD,
                                  bg=theme['line_num_bg'], fg=theme['fg'],
                                  font=("Arial", 10), padx=5, pady=5)
        self.chat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Button container
        btn_container = tk.Frame(input_container, bg=theme['bg'])
        btn_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Send button
        send_btn = tk.Button(btn_container, text="Send",
                            command=self.send_chat_message,
                            bg="#0078d4", fg="white",
                            font=("Arial", 9, "bold"),
                            padx=15, pady=5)
        send_btn.pack(pady=2)
        
        # Attach code button
        attach_btn = tk.Button(btn_container, text="📎",
                              command=self.attach_code_to_chat,
                              bg=theme['button_bg'], fg=theme['fg'],
                              font=("Arial", 10),
                              padx=10, pady=2)
        attach_btn.pack(pady=2)
        
        # Bind Enter to send (Shift+Enter for new line)
        self.chat_input.bind("<Return>", lambda e: self.send_chat_message() or "break")
        self.chat_input.bind("<Shift-Return>", lambda e: None)  # Allow newline with Shift+Enter
        
        self.chat_input.focus_set()
    
    def attach_code_to_chat(self):
        """Attach selected code to the chat context"""
        tab_info = self.get_current_tab_info()
        if not tab_info:
            self.context_label.config(text="⚠ No file open")
            return
        
        text_widget = tab_info['text_widget']
        
        try:
            selected_code = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_code.strip():
                # Store in chat input as context
                current_text = self.chat_input.get("1.0", tk.END).strip()
                if current_text:
                    self.chat_input.insert("1.0", f"[Code attached]\n```\n{selected_code}\n```\n\n")
                else:
                    self.chat_input.insert("1.0", f"[Code attached]\n```\n{selected_code}\n```\n")
                self.context_label.config(text=f"📎 Code attached ({len(selected_code)} chars)")
            else:
                self.context_label.config(text="⚠ No code selected")
        except:
            # No selection, attach entire file context
            file_content = text_widget.get("1.0", tk.END).strip()
            if len(file_content) > 2000:
                file_content = file_content[:2000] + "\n... (truncated)"
            
            file_name = "untitled"
            if tab_info['file_path']:
                file_name = os.path.basename(tab_info['file_path'])
            
            current_text = self.chat_input.get("1.0", tk.END).strip()
            if current_text:
                self.chat_input.insert("1.0", f"[File: {file_name}]\n```\n{file_content}\n```\n\n")
            else:
                self.chat_input.insert("1.0", f"[File: {file_name}]\n```\n{file_content}\n```\n")
            self.context_label.config(text=f"📎 File attached: {file_name}")
    
    def send_chat_message(self):
        """Send a message in the chat"""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.chat_input.delete("1.0", tk.END)
        self.context_label.config(text="")
        
        # Display user message
        self.display_chat_message("user", message)
        
        # Add to history
        self.chat_history.append({"role": "user", "content": message})
        
        # Show thinking indicator
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.insert(tk.END, "AI: ", "assistant")
        self.chat_display.insert(tk.END, "💭 Thinking...\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
        
        # Get response from AI
        def get_response():
            try:
                # Prepare conversation context
                from .prompt_templates import PromptTemplates
                
                # Get file context if available
                tab_info = self.get_current_tab_info()
                file_context = ""
                if tab_info and tab_info['file_path']:
                    file_name = os.path.basename(tab_info['file_path'])
                    file_context = f"Current file: {file_name}"
                
                # Build conversation history for context
                conversation = "\n".join([
                    f"{msg['role'].capitalize()}: {msg['content']}"
                    for msg in self.chat_history[-5:]  # Last 5 messages for context
                ])
                
                prompt = PromptTemplates.get_chat_prompt()
                messages = prompt.format_messages(
                    conversation=conversation,
                    file_context=file_context,
                    user_message=message
                )
                
                response = self.ai_service.llm.invoke(messages)
                ai_response = response.content
                
                # Update UI
                def update_ui():
                    # Remove thinking indicator
                    self.chat_display.config(state='normal')
                    # Find and remove the thinking message
                    content = self.chat_display.get("1.0", tk.END)
                    if "💭 Thinking..." in content:
                        # Remove the last line with thinking
                        self.chat_display.delete("end-2l", "end-1l")
                    
                    # Display AI response
                    self.display_chat_message("assistant", ai_response)
                    self.chat_display.config(state='disabled')
                    
                    # Add to history
                    self.chat_history.append({"role": "assistant", "content": ai_response})
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    self.chat_display.config(state='normal')
                    # Remove thinking indicator
                    content = self.chat_display.get("1.0", tk.END)
                    if "💭 Thinking..." in content:
                        self.chat_display.delete("end-2l", "end-1l")
                    self.chat_display.insert(tk.END, f"❌ Error: {str(e)}\n")
                    self.chat_display.see(tk.END)
                    self.chat_display.config(state='disabled')
                
                self.root.after(0, show_error)
        
        # Run in background
        thread = threading.Thread(target=get_response, daemon=True)
        thread.start()
    
    def display_chat_message(self, role, content, restore=False):
        """Display a message in the chat"""
        from datetime import datetime
        
        self.chat_display.config(state='normal')
        
        if not restore:
            self.chat_display.insert(tk.END, "\n")
        
        # Message header
        if role == "user":
            self.chat_display.insert(tk.END, "You: ", "user")
        else:
            self.chat_display.insert(tk.END, "AI: ", "assistant")
        
        # Timestamp
        if not restore:
            timestamp = datetime.now().strftime("%H:%M")
            self.chat_display.insert(tk.END, f"({timestamp})\n", "timestamp")
        else:
            self.chat_display.insert(tk.END, "\n")
        
        # Message content with code block formatting
        lines = content.split('\n')
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                self.chat_display.insert(tk.END, line + "\n", "code")
            else:
                self.chat_display.insert(tk.END, line + "\n")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def clear_chat(self):
        """Clear chat history"""
        response = messagebox.askyesno(
            "Clear Chat",
            "Are you sure you want to clear the chat history?"
        )
        
        if response:
            self.chat_history = []
            self.chat_display.config(state='normal')
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.insert("1.0", "Chat cleared. Start a new conversation!\n\n", "assistant")
            self.chat_display.config(state='disabled')

def main():
    root = tk.Tk()
    app = CodeEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()