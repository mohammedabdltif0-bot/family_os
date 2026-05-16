"""
I/O Management Module
Handles I/O devices and request queuing
"""

import time
from enum import Enum
from dataclasses import dataclass
from queue import Queue
from typing import Any, Dict

class IODevice(Enum):
    """Available I/O devices"""
    KEYBOARD = "keyboard"
    DISPLAY = "display"
    PRINTER = "printer"
    DISK = "disk"

@dataclass
class IORequest:
    """Represents an I/O request"""
    device: IODevice
    operation: str
    data: Any = None
    timestamp: float = None
    
    def __post_init__(self):
        self.timestamp = time.time()

class IOManager:
    """Manages I/O devices and requests"""
    
    def __init__(self):
        # Device availability status
        self.devices: Dict[IODevice, bool] = {
            IODevice.KEYBOARD: True,
            IODevice.DISPLAY: True,
            IODevice.PRINTER: True,
            IODevice.DISK: True
        }
        # Request queue for pending I/O operations
        self.request_queue: Queue = Queue()
        # Current status of each device
        self.device_status: Dict[IODevice, str] = {
            IODevice.KEYBOARD: "READY",
            IODevice.DISPLAY: "READY",
            IODevice.PRINTER: "READY",
            IODevice.DISK: "READY"
        }
        
    def request_io(self, device: IODevice, operation: str, data: Any = None) -> bool:
        """
        Submit an I/O request
        Args:
            device: Target I/O device
            operation: Operation to perform
            data: Optional data for the operation
        Returns:
            True if request was queued successfully
        """
        if self.devices[device]:
            request = IORequest(device, operation, data)
            self.request_queue.put(request)
            print(f"[IO] Queued request for {device.value}: {operation}")
            return True
        return False
    
    def process_io_requests(self):
        """Process all pending I/O requests"""
        while not self.request_queue.empty():
            request = self.request_queue.get()
            self.device_status[request.device] = "BUSY"
            # Simulate I/O operation time
            time.sleep(0.1)
            self._execute_io(request)
            self.device_status[request.device] = "READY"
    
    def _execute_io(self, request: IORequest):
        """Execute a specific I/O operation"""
        print(f"[IO] Processing {request.operation} on {request.device.value}")
        if request.device == IODevice.DISPLAY and request.operation == "write":
            print(f"[Display] {request.data}")
        # Add more device operations as needed
    
    def get_device_status(self) -> Dict:
        """Get status of all I/O devices"""
        return self.device_status.copy()