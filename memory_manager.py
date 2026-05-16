"""
Memory Management Module
Handles memory allocation and deallocation using first-fit algorithm
"""

from typing import List, Dict, Optional

class MemoryBlock:
    """Represents a block of memory"""
    
    def __init__(self, start: int, size: int, pid: int = None):
        self.start = start
        self.size = size
        self.pid = pid
        self.is_free = pid is None

class MemoryManager:
    """Manages memory allocation and deallocation"""
    
    def __init__(self, total_size: int = 1024 * 100):  # 100KB default
        self.total_size = total_size
        # Initialize with one free block of total size
        self.blocks: List[MemoryBlock] = [MemoryBlock(0, total_size, None)]
        self.allocation_map = {}  # Maps PID to start address
        
    def allocate(self, size: int, pid: int) -> Optional[int]:
        """
        Allocate memory for a process using First-Fit algorithm
        Args:
            size: Amount of memory to allocate
            pid: Process ID
        Returns:
            Start address if successful, None otherwise
        """
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                # Found a suitable block
                if block.size > size:
                    # Split the block
                    new_block = MemoryBlock(block.start + size, block.size - size, None)
                    block.size = size
                    self.blocks.insert(i + 1, new_block)
                block.is_free = False
                block.pid = pid
                self.allocation_map[pid] = block.start
                print(f"[Memory] Allocated {size} bytes to process {pid} at address {block.start}")
                return block.start
        print(f"[Memory] Failed to allocate {size} bytes for process {pid}")
        return None
    
    def deallocate(self, pid: int) -> bool:
        """
        Deallocate memory for a process
        Args:
            pid: Process ID
        Returns:
            True if successful, False otherwise
        """
        for block in self.blocks:
            if block.pid == pid:
                block.is_free = True
                block.pid = None
                self._merge_free_blocks()
                print(f"[Memory] Deallocated memory for process {pid}")
                return True
        return False
    
    def _merge_free_blocks(self):
        """Merge adjacent free blocks to reduce fragmentation"""
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i].is_free and self.blocks[i+1].is_free:
                # Merge with next block
                self.blocks[i].size += self.blocks[i+1].size
                del self.blocks[i+1]
            else:
                i += 1
    
    def get_memory_info(self) -> Dict:
        """Get memory usage information"""
        total_free = sum(block.size for block in self.blocks if block.is_free)
        total_used = self.total_size - total_free
        return {
            'total': self.total_size,
            'used': total_used,
            'free': total_free,
            'blocks': self.blocks.copy()
        }
    
    def display_memory_map(self):
        """Display visual memory map"""
        print("\n" + "="*50)
        print("Memory Map")
        print("="*50)
        for block in self.blocks:
            status = "FREE" if block.is_free else f"PID {block.pid}"
            print(f"[{block.start:>8} - {block.start+block.size:>8}] {status:>10} ({block.size} bytes)")