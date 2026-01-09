import tkinter as tk
from tkinter import ttk

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
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

def main():
    root = tk.Tk()
    app = CodeEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
