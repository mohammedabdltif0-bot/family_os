"""
Process Management Module
Handles process creation, scheduling, and termination
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
from queue import Queue

class ProcessState(Enum):
    """Process states in the OS"""
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

@dataclass
class Process:
    """Process Control Block (PCB)"""
    pid: int
    name: str
    priority: int
    state: ProcessState
    program_counter: int
    memory_start: int = None
    memory_end: int = None

class ProcessManager:
    """Manages all processes in the system"""
    
    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.ready_queue: Queue = Queue()
        self.current_pid = 0
        self.running_process: Optional[Process] = None
        self.next_pid = 1
        
    def create_process(self, name: str, priority: int = 1) -> Process:
        """
        Create a new process
        Args:
            name: Process name
            priority: Process priority (higher number = higher priority)
        Returns:
            Created Process object
        """
        pid = self.next_pid
        self.next_pid += 1
        process = Process(pid, name, priority, ProcessState.NEW, 0)
        self.processes[pid] = process
        self.ready_queue.put(process)
        process.state = ProcessState.READY
        print(f"[Process] Created process {name} with PID {pid}, priority {priority}")
        return process
    
    def terminate_process(self, pid: int) -> bool:
        """
        Terminate a process by PID
        Args:
            pid: Process ID to terminate
        Returns:
            True if terminated successfully, False otherwise
        """
        if pid in self.processes:
            process = self.processes[pid]
            process.state = ProcessState.TERMINATED
            if self.running_process and self.running_process.pid == pid:
                self.running_process = None
            del self.processes[pid]
            print(f"[Process] Terminated process {pid}")
            return True
        return False
    
    def schedule(self) -> Optional[Process]:
        """
        Schedule the next process to run (FCFS scheduling)
        Returns:
            Next process to run or None if no processes ready
        """
        if not self.ready_queue.empty():
            self.running_process = self.ready_queue.get()
            self.running_process.state = ProcessState.RUNNING
            return self.running_process
        return None
    
    def list_processes(self) -> List[Process]:
        """Return list of all processes"""
        return list(self.processes.values())
    
    def get_process_info(self, pid: int) -> Optional[Process]:
        """Get process information by PID"""
        return self.processes.get(pid)