"""
GUI Module for Python Operating System
Provides graphical user interface instead of terminal
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread
import queue

class OSGUI:
    """Graphical User Interface for the OS"""
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.kernel.gui = self  # Allow kernel to send output to GUI
        self.output_queue = queue.Queue()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Python Operating System v2.0 - GUI Edition (With Persistent Storage)")
        self.root.geometry("1300x750")
        self.root.configure(bg='#2b2b2b')
        
        # Set icon if available (optional)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.create_widgets()
        self.process_output_queue()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Command area
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Output area with scroll
        output_frame = ttk.LabelFrame(left_panel, text="System Output", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=30,
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white',
            font=('Consolas', 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Command input area
        cmd_frame = ttk.LabelFrame(left_panel, text="Command Input", padding=5)
        cmd_frame.pack(fill=tk.X, pady=5)
        
        self.cmd_entry = ttk.Entry(cmd_frame, font=('Consolas', 11))
        self.cmd_entry.pack(fill=tk.X, padx=5, pady=5)
        self.cmd_entry.bind('<Return>', self.execute_command)
        
        cmd_buttons_frame = ttk.Frame(cmd_frame)
        cmd_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(cmd_buttons_frame, text="▶ Execute", command=self.execute_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(cmd_buttons_frame, text="🗑 Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Quick actions and status
        right_panel = ttk.Frame(main_container, width=380)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        right_panel.pack_propagate(False)
        
        # Status frame
        status_frame = ttk.LabelFrame(right_panel, text="System Status", padding=5)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="System Ready", font=('Arial', 11, 'bold'))
        self.status_label.pack(pady=5)
        
        # Process list frame
        process_frame = ttk.LabelFrame(right_panel, text="📊 Running Processes", padding=5)
        process_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        process_scroll = ttk.Scrollbar(process_frame)
        process_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.process_listbox = tk.Listbox(
            process_frame, 
            height=8, 
            bg='#1e1e1e', 
            fg='#d4d4d4',
            yscrollcommand=process_scroll.set,
            font=('Consolas', 9)
        )
        self.process_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        process_scroll.config(command=self.process_listbox.yview)
        
        # File list frame
        file_frame = ttk.LabelFrame(right_panel, text="📁 Files", padding=5)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        file_scroll = ttk.Scrollbar(file_frame)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            file_frame, 
            height=8, 
            bg='#1e1e1e', 
            fg='#d4d4d4',
            yscrollcommand=file_scroll.set,
            font=('Consolas', 9)
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        file_scroll.config(command=self.file_listbox.yview)
        
        # Quick action buttons
        actions_frame = ttk.LabelFrame(right_panel, text="⚡ Quick Actions", padding=5)
        actions_frame.pack(fill=tk.X, pady=5)
        
        button_grid = ttk.Frame(actions_frame)
        button_grid.pack(fill=tk.X, padx=5, pady=5)
        
        quick_buttons = [
            ("📊 System Status", self.cmd_status),
            ("📋 List Processes", self.cmd_ps),
            ("💾 Memory Info", self.cmd_mem),
            ("📁 List Files", self.cmd_ls),
            ("🎮 Run Demo", self.cmd_demo),
            ("💾 Save State", self.cmd_save),
            ("📂 Load State", self.cmd_load),
            ("🧹 Clear Output", self.clear_output),
            ("❌ Exit OS", self.cmd_exit)
        ]
        
        for i, (text, cmd) in enumerate(quick_buttons):
            btn = ttk.Button(button_grid, text=text, command=cmd, width=16)
            btn.grid(row=i, column=0, padx=2, pady=2)
        
        # Create file frame
        create_file_frame = ttk.LabelFrame(right_panel, text="📝 Quick Create File", padding=5)
        create_file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(create_file_frame, text="Filename:").pack(pady=2)
        self.new_filename = ttk.Entry(create_file_frame, width=30)
        self.new_filename.pack(pady=2)
        
        ttk.Label(create_file_frame, text="Content:").pack(pady=2)
        self.new_file_content = tk.Text(create_file_frame, height=4, width=35)
        self.new_file_content.pack(pady=2)
        
        ttk.Button(create_file_frame, text="Create File", command=self.cmd_create_file).pack(pady=5)
        
    def add_output(self, text):
        """Add text to output area"""
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self, event=None):
        """Clear output area"""
        self.output_text.delete(1.0, tk.END)
    
    def execute_command(self, event=None):
        """Execute command from input field"""
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        
        self.add_output(f"\n$ {cmd}")
        self.cmd_entry.delete(0, tk.END)
        
        # Execute in separate thread to prevent GUI freezing
        thread = Thread(target=self._execute, args=(cmd,))
        thread.daemon = True
        thread.start()
    
    def _execute(self, cmd):
        """Execute command in background"""
        parts = cmd.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Redirect stdout to capture print statements
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            if command in self.kernel.commands:
                self.kernel.commands[command](args)
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
        except Exception as e:
            print(f"Error: {e}")
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Send output to GUI
        if output:
            self.add_output(output.rstrip())
    
    def update_status(self):
        """Update system status periodically"""
        try:
            processes = len(self.kernel.process_manager.list_processes())
            mem_info = self.kernel.memory_manager.get_memory_info()
            mem_percent = (mem_info['used'] / mem_info['total'] * 100) if mem_info['total'] > 0 else 0
            
            status_text = f"Processes: {processes} | Memory: {mem_percent:.1f}% ({mem_info['used']}/{mem_info['total']} bytes)"
            self.status_label.config(text=status_text)
            
            # Update process list
            self.process_listbox.delete(0, tk.END)
            for p in self.kernel.process_manager.list_processes():
                mem_info_str = f" [{p.memory_start}-{p.memory_end}]" if p.memory_start else ""
                self.process_listbox.insert(tk.END, f"PID {p.pid:3}: {p.name:12} [{p.state.value}]{mem_info_str}")
            
            # Update file list
            self.file_listbox.delete(0, tk.END)
            for f in self.kernel.file_system.list_files():
                self.file_listbox.insert(tk.END, f"{f['name']:<20} ({f['size']} bytes)")
                
        except Exception as e:
            pass
        
        # Schedule next update
        self.root.after(2000, self.update_status)
    
    def process_output_queue(self):
        """Process queued output"""
        try:
            while True:
                msg = self.output_queue.get_nowait()
                self.add_output(msg)
        except queue.Empty:
            pass
        self.root.after(100, self.process_output_queue)
    
    # Quick command methods
    def cmd_status(self):
        self.kernel.show_status()
    
    def cmd_ps(self):
        self.kernel.list_processes()
    
    def cmd_mem(self):
        self.kernel.show_memory()
    
    def cmd_ls(self):
        self.kernel.list_files()
    
    def cmd_demo(self):
        thread = Thread(target=self.kernel.run_demo)
        thread.daemon = True
        thread.start()
    
    def cmd_save(self):
        """Save system state"""
        self.kernel.save_system_state()
        self.add_output("✓ System state saved to disk!")
    
    def cmd_load(self):
        """Load system state"""
        self.kernel.load_system_state()
        self.add_output("✓ System state loaded from disk!")
        self.update_status()  # Refresh display
    
    def cmd_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit the OS?"):
            self.kernel.exit_os()
            self.root.quit()
    
    def cmd_create_file(self):
        filename = self.new_filename.get().strip()
        content = self.new_file_content.get("1.0", tk.END).strip()
        if filename:
            self.kernel.file_system.create_file(filename, content)
            self.add_output(f"Created file: {filename}")
            self.new_filename.delete(0, tk.END)
            self.new_file_content.delete("1.0", tk.END)
        else:
            self.add_output("Please enter a filename")
    
    def run(self):
        """Start the GUI main loop"""
        self.add_output("="*70)
        self.add_output("🐍 PYTHON OPERATING SYSTEM v2.0 - GUI EDITION")
        self.add_output("="*70)
        self.add_output("Type 'help' for available commands")
        self.add_output("Use the quick buttons for common operations")
        self.add_output("Quick create files using the form on the right")
        self.add_output("")
        self.add_output("💾 PERSISTENT STORAGE ENABLED:")
        self.add_output("   - Files are saved to 'os_storage/' folder")
        self.add_output("   - System state saves to 'os_state/' folder")
        self.add_output("   - Use 'save' and 'load' commands or buttons")
        self.add_output("="*70)
        
        # Start status updates
        self.update_status()
        
        # Run main loop
        self.root.mainloop()