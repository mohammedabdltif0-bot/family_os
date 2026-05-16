"""
OS Kernel Module
Core system that integrates all OS components
"""

import os
import sys
import json
from io import StringIO
from process_manager import ProcessManager, Process, ProcessState
from memory_manager import MemoryManager, MemoryBlock
from file_system import FileSystem
from io_manager import IOManager, IODevice

class OperatingSystem:
    """Main OS Kernel - coordinates all system components"""
    
    def __init__(self):
        # Initialize all system components
        self.process_manager = ProcessManager()
        self.memory_manager = MemoryManager(1024 * 100)  # 100KB memory
        self.file_system = FileSystem()
        self.io_manager = IOManager()
        self.running = True
        self.gui = None  # Will be set by GUI for output redirection
        
        # Command registry
        self.commands = {
            'help': self.show_help,
            'ps': self.list_processes,
            'run': self.run_process,
            'kill': self.kill_process,
            'mem': self.show_memory,
            'alloc': self.allocate_memory,
            'dealloc': self.deallocate_memory,
            'ls': self.list_files,
            'create': self.create_file,
            'cat': self.read_file,
            'write': self.write_file,
            'rm': self.delete_file,
            'io-status': self.io_status,
            'clear': self.clear_screen,
            'exit': self.exit_os,
            'status': self.show_status,
            'demo': self.run_demo,
            'save': self.save_system_state,
            'load': self.load_system_state
        }
        
        # Create initial files
        self._initialize_system()
        
        # Try to load previous state
        self.load_system_state()
    
    def _print(self, text):
        """Print to either GUI or console"""
        if self.gui:
            self.gui.add_output(text)
        else:
            print(text)
    
    def _initialize_system(self):
        """Initialize system with default files (only if no files exist)"""
        if len(self.file_system.list_files()) == 0:
            self.file_system.create_file("hello.txt", "Hello, this is your Python OS!")
            self.file_system.create_file("system.log", "OS initialized successfully\n")
    
    # ============= Persistence Methods =============
    
    def save_system_state(self, args=None):
        """Save entire system state to disk"""
        try:
            state_dir = "os_state"
            if not os.path.exists(state_dir):
                os.makedirs(state_dir)
            
            # Save process information
            processes_data = []
            for p in self.process_manager.list_processes():
                processes_data.append({
                    'pid': p.pid,
                    'name': p.name,
                    'priority': p.priority,
                    'state': p.state.value,
                    'memory_start': p.memory_start,
                    'memory_end': p.memory_end
                })
            
            with open(os.path.join(state_dir, "processes.json"), 'w') as f:
                json.dump(processes_data, f, indent=2)
            
            # Save next PID
            with open(os.path.join(state_dir, "next_pid.json"), 'w') as f:
                json.dump({'next_pid': self.process_manager.next_pid}, f)
            
            # Save memory information
            mem_info = self.memory_manager.get_memory_info()
            memory_data = {
                'total': mem_info['total'],
                'blocks': []
            }
            for block in mem_info['blocks']:
                memory_data['blocks'].append({
                    'start': block.start,
                    'size': block.size,
                    'pid': block.pid,
                    'is_free': block.is_free
                })
            
            with open(os.path.join(state_dir, "memory.json"), 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            self._print("[System] System state saved successfully!")
            return True
        except Exception as e:
            self._print(f"[System] Error saving state: {e}")
            return False
    
    def load_system_state(self, args=None):
        """Load entire system state from disk"""
        try:
            state_dir = "os_state"
            
            if not os.path.exists(state_dir):
                self._print("[System] No saved state found. Starting fresh.")
                return False
            
            # Load processes
            processes_path = os.path.join(state_dir, "processes.json")
            if os.path.exists(processes_path):
                with open(processes_path, 'r') as f:
                    processes_data = json.load(f)
                
                # Clear existing processes
                self.process_manager.processes.clear()
                
                # Restore processes
                for p_data in processes_data:
                    process = Process(
                        pid=p_data['pid'],
                        name=p_data['name'],
                        priority=p_data['priority'],
                        state=ProcessState(p_data['state']),
                        program_counter=0,
                        memory_start=p_data['memory_start'],
                        memory_end=p_data['memory_end']
                    )
                    self.process_manager.processes[process.pid] = process
                    # Update next_pid
                    if process.pid >= self.process_manager.next_pid:
                        self.process_manager.next_pid = process.pid + 1
                
                self._print(f"[System] Loaded {len(processes_data)} processes")
            
            # Load next PID
            next_pid_path = os.path.join(state_dir, "next_pid.json")
            if os.path.exists(next_pid_path):
                with open(next_pid_path, 'r') as f:
                    data = json.load(f)
                    self.process_manager.next_pid = data.get('next_pid', self.process_manager.next_pid)
            
            # Load memory state
            memory_path = os.path.join(state_dir, "memory.json")
            if os.path.exists(memory_path):
                with open(memory_path, 'r') as f:
                    memory_data = json.load(f)
                
                # Restore memory blocks
                self.memory_manager.blocks = []
                for block_data in memory_data['blocks']:
                    block = MemoryBlock(
                        start=block_data['start'],
                        size=block_data['size'],
                        pid=block_data['pid']
                    )
                    block.is_free = block_data['is_free']
                    self.memory_manager.blocks.append(block)
                
                # Restore allocation map
                self.memory_manager.allocation_map = {}
                for block in self.memory_manager.blocks:
                    if not block.is_free and block.pid:
                        self.memory_manager.allocation_map[block.pid] = block.start
                
                self._print("[System] Memory state loaded successfully")
            
            self._print("[System] System state loaded successfully!")
            return True
        except Exception as e:
            self._print(f"[System] Error loading state: {e}")
            return False
    
    # ============= Process Management Commands =============
    
    def list_processes(self, args=None):
        """Display all running processes"""
        processes = self.process_manager.list_processes()
        if not processes:
            self._print("No processes running")
            return
        self._print("\n" + "-"*80)
        self._print(f"{'PID':<6} {'Name':<15} {'Priority':<10} {'State':<12} {'Memory':<15}")
        self._print("-"*80)
        for p in processes:
            mem_info = f"{p.memory_start}-{p.memory_end}" if p.memory_start else "Not allocated"
            self._print(f"{p.pid:<6} {p.name:<15} {p.priority:<10} {p.state.value:<12} {mem_info:<15}")
        self._print("-"*80)
    
    def run_process(self, args):
        """Create and run a new process"""
        if not args:
            self._print("Usage: run <process_name>")
            return
        name = args[0]
        process = self.process_manager.create_process(name)
        self.process_manager.schedule()
        self._print(f"Running process {name} (PID: {process.pid})")
        # Auto-allocate memory
        self.memory_manager.allocate(1000, process.pid)
        process.memory_start = self.memory_manager.allocation_map.get(process.pid)
        process.memory_end = process.memory_start + 1000 if process.memory_start else None
    
    def kill_process(self, args):
        """Terminate a process by PID"""
        if not args:
            self._print("Usage: kill <pid>")
            return
        try:
            pid = int(args[0])
            self.memory_manager.deallocate(pid)
            if self.process_manager.terminate_process(pid):
                self._print(f"Process {pid} terminated")
            else:
                self._print(f"Process {pid} not found")
        except ValueError:
            self._print("PID must be a number")
    
    # ============= Memory Management Commands =============
    
    def show_memory(self, args=None):
        """Display memory information"""
        info = self.memory_manager.get_memory_info()
        self._print("\n" + "="*50)
        self._print("MEMORY INFORMATION")
        self._print("="*50)
        self._print(f"Total Memory: {info['total']} bytes")
        self._print(f"Used Memory:  {info['used']} bytes ({info['used']/info['total']*100:.1f}%)")
        self._print(f"Free Memory:  {info['free']} bytes ({info['free']/info['total']*100:.1f}%)")
        
        # Show memory map
        self._print("\n" + "="*50)
        self._print("Memory Map")
        self._print("="*50)
        for block in info['blocks']:
            status = "FREE" if block.is_free else f"PID {block.pid}"
            self._print(f"[{block.start:>8} - {block.start+block.size:>8}] {status:>10} ({block.size} bytes)")
    
    def allocate_memory(self, args):
        """Allocate memory to a process"""
        if len(args) < 2:
            self._print("Usage: alloc <pid> <size>")
            return
        try:
            pid = int(args[0])
            size = int(args[1])
            address = self.memory_manager.allocate(size, pid)
            if address:
                process = self.process_manager.get_process_info(pid)
                if process:
                    process.memory_start = address
                    process.memory_end = address + size
                self._print(f"Allocated {size} bytes to process {pid} at address {address}")
        except ValueError:
            self._print("PID and size must be numbers")
    
    def deallocate_memory(self, args):
        """Deallocate memory from a process"""
        if not args:
            self._print("Usage: dealloc <pid>")
            return
        try:
            pid = int(args[0])
            self.memory_manager.deallocate(pid)
        except ValueError:
            self._print("PID must be a number")
    
    # ============= File System Commands =============
    
    def list_files(self, args=None):
        """List all files in the system"""
        files = self.file_system.list_files()
        if not files:
            self._print("No files in filesystem")
            return
        self._print("\n" + "-"*70)
        self._print(f"{'Name':<20} {'Size':<10} {'Created':<25} {'Modified':<25}")
        self._print("-"*70)
        import time
        for f in files:
            self._print(f"{f['name']:<20} {f['size']:<10} {time.ctime(f['created']):<25} {time.ctime(f['modified']):<25}")
        self._print("-"*70)
    
    def create_file(self, args):
        """Create a new file"""
        if not args:
            self._print("Usage: create <filename>")
            return
        name = args[0]
        self.file_system.create_file(name)
    
    def read_file(self, args):
        """Read and display file content"""
        if not args:
            self._print("Usage: cat <filename>")
            return
        name = args[0]
        data = self.file_system.read_file(name)
        if data is not None:
            self._print(f"\n--- {name} ---")
            self._print(data)
            self._print("---" + "-"* len(name) + "---")
        else:
            self._print(f"File {name} not found")
    
    def write_file(self, args):
        """Write content to a file"""
        if not args:
            self._print("Usage: write <filename>")
            return
        name = args[0]
        
        # For GUI mode, we need a different approach
        if self.gui:
            self._print(f"Please use the 'create' command or edit files programmatically")
            return
        
        self._print(f"Enter content for {name} (type 'EOF' on a new line to finish):")
        lines = []
        while True:
            try:
                line = input()
                if line == "EOF":
                    break
                lines.append(line)
            except EOFError:
                break
        content = "\n".join(lines)
        self.file_system.write_file(name, content)
    
    def delete_file(self, args):
        """Delete a file"""
        if not args:
            self._print("Usage: rm <filename>")
            return
        name = args[0]
        if self.file_system.delete_file(name):
            self._print(f"Deleted {name}")
        else:
            self._print(f"File {name} not found")
    
    # ============= I/O Commands =============
    
    def io_status(self, args=None):
        """Display I/O device status"""
        status = self.io_manager.get_device_status()
        self._print("\n" + "="*40)
        self._print("I/O DEVICE STATUS")
        self._print("="*40)
        for device, stat in status.items():
            self._print(f"{device.value.upper():<15} : {stat}")
        self._print("="*40)
    
    # ============= System Commands =============
    
    def show_status(self, args=None):
        """Display overall system status"""
        self._print("\n" + "="*60)
        self._print("SYSTEM STATUS")
        self._print("="*60)
        processes = self.process_manager.list_processes()
        self._print(f"Running Processes: {len(processes)}")
        mem_info = self.memory_manager.get_memory_info()
        self._print(f"Memory Usage: {mem_info['used']}/{mem_info['total']} bytes ({mem_info['used']/mem_info['total']*100:.1f}%)")
        files = self.file_system.list_files()
        self._print(f"Files in System: {len(files)}")
        self._print(f"Total Storage Used: {sum(f['size'] for f in files)} bytes")
        self._print("="*60)
    
    def run_demo(self, args=None):
        """Run a demonstration of OS features"""
        self._print("\n" + "="*60)
        self._print("RUNNING OS DEMO")
        self._print("="*60)
        
        self._print("\n[1] Creating processes...")
        p1 = self.process_manager.create_process("Firefox", priority=2)
        p2 = self.process_manager.create_process("Terminal", priority=1)
        
        self._print("\n[2] Allocating memory...")
        self.memory_manager.allocate(5000, p1.pid)
        self.memory_manager.allocate(3000, p2.pid)
        if p1.memory_start:
            p1.memory_end = p1.memory_start + 5000
        if p2.memory_start:
            p2.memory_end = p2.memory_start + 3000
        
        self._print("\n[3] Creating files...")
        self.file_system.create_file("readme.txt", "Welcome to Python OS!")
        self.file_system.create_file("config.ini", "[settings]\nauto_save=true\n")
        
        self._print("\n[4] Testing I/O...")
        self.io_manager.request_io(IODevice.DISPLAY, "write", "Hello from Python OS!")
        self.io_manager.process_io_requests()
        
        self._print("\n[5] Final system status:")
        self.show_status()
        
        self._print("\n" + "="*60)
        self._print("Demo completed! Use 'status' to see current system state.")
        self._print("="*60)
    
    def clear_screen(self, args=None):
        """Clear the output area"""
        if self.gui:
            self.gui.clear_output()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_help(self, args=None):
        """Display help information"""
        self._print("\n" + "="*60)
        self._print("OS COMMANDS")
        self._print("="*60)
        self._print("Process Management:")
        self._print("  ps              - List all processes")
        self._print("  run <name>      - Create and run a new process")
        self._print("  kill <pid>      - Terminate a process")
        self._print("\nMemory Management:")
        self._print("  mem             - Show memory information")
        self._print("  alloc <pid> <size> - Allocate memory for process")
        self._print("  dealloc <pid>   - Deallocate process memory")
        self._print("\nFile System:")
        self._print("  ls              - List all files")
        self._print("  create <name>   - Create a new file")
        self._print("  write <name>    - Write to a file")
        self._print("  cat <name>      - Read a file")
        self._print("  rm <name>       - Delete a file")
        self._print("\nI/O Management:")
        self._print("  io-status       - Check I/O device status")
        self._print("\nPersistence:")
        self._print("  save            - Save current system state to disk")
        self._print("  load            - Load previously saved system state")
        self._print("\nSystem:")
        self._print("  status          - Show overall system status")
        self._print("  demo            - Run demo showing all features")
        self._print("  clear           - Clear screen")
        self._print("  help            - Show this help")
        self._print("  exit            - Exit OS")
        self._print("="*60)
    
    def exit_os(self, args=None):
        """Shutdown the operating system and save state"""
        self._print("Saving system state before shutdown...")
        self.save_system_state()
        self._print("Shutting down Operating System...")
        self.running = False
        if self.gui:
            self.gui.root.quit()