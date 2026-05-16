"""
File System Module with Persistent Storage
Handles file creation, reading, writing, and deletion
Saves files to actual disk
"""

import time
import os
import json
from typing import Dict, List, Optional

class File:
    """Represents a file in the system"""
    
    def __init__(self, name: str, data: str = ""):
        self.name = name
        self.data = data
        self.size = len(data)
        self.created = time.time()
        self.modified = time.time()

class FileSystem:
    """Manages files in the system with persistence"""
    
    def __init__(self, storage_dir="os_storage"):
        self.storage_dir = storage_dir
        self.files: Dict[str, File] = {}
        self.current_directory = "/"
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        # Load existing files from disk
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load all files from disk storage"""
        files_meta_path = os.path.join(self.storage_dir, "files_meta.json")
        
        # Load metadata
        if os.path.exists(files_meta_path):
            try:
                with open(files_meta_path, 'r') as f:
                    meta_data = json.load(f)
                
                for file_name, meta in meta_data.items():
                    # Load file content
                    file_path = os.path.join(self.storage_dir, f"{file_name}.txt")
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Create File object
                        file_obj = File(file_name, content)
                        file_obj.created = meta.get('created', time.time())
                        file_obj.modified = meta.get('modified', time.time())
                        file_obj.size = len(content)
                        self.files[file_name] = file_obj
                        
                print(f"[FileSystem] Loaded {len(self.files)} files from disk")
            except Exception as e:
                print(f"[FileSystem] Error loading files: {e}")
    
    def _save_to_disk(self, file_name: str):
        """Save a single file to disk"""
        if file_name in self.files:
            file_obj = self.files[file_name]
            
            # Save file content
            file_path = os.path.join(self.storage_dir, f"{file_name}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_obj.data)
            
            # Update metadata
            self._save_metadata()
    
    def _save_metadata(self):
        """Save all file metadata to disk"""
        meta_data = {}
        for name, file_obj in self.files.items():
            meta_data[name] = {
                'created': file_obj.created,
                'modified': file_obj.modified,
                'size': file_obj.size
            }
        
        files_meta_path = os.path.join(self.storage_dir, "files_meta.json")
        with open(files_meta_path, 'w') as f:
            json.dump(meta_data, f, indent=2)
    
    def create_file(self, name: str, data: str = "") -> bool:
        """Create a new file (persistent)"""
        if name in self.files:
            print(f"[FileSystem] File {name} already exists")
            return False
        
        self.files[name] = File(name, data)
        self._save_to_disk(name)
        print(f"[FileSystem] Created file {name} ({len(data)} bytes) [SAVED TO DISK]")
        return True
    
    def write_file(self, name: str, data: str, append: bool = False) -> bool:
        """Write data to a file (persistent)"""
        if name not in self.files:
            return False
        
        if append:
            self.files[name].data += data
        else:
            self.files[name].data = data
        
        self.files[name].size = len(self.files[name].data)
        self.files[name].modified = time.time()
        self._save_to_disk(name)
        print(f"[FileSystem] Wrote to file {name} [SAVED TO DISK]")
        return True
    
    def read_file(self, name: str) -> Optional[str]:
        """Read file content"""
        if name in self.files:
            return self.files[name].data
        return None
    
    def delete_file(self, name: str) -> bool:
        """Delete a file (persistent)"""
        if name in self.files:
            # Delete from memory
            del self.files[name]
            
            # Delete from disk
            file_path = os.path.join(self.storage_dir, f"{name}.txt")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update metadata
            self._save_metadata()
            
            print(f"[FileSystem] Deleted file {name} [REMOVED FROM DISK]")
            return True
        return False
    
    def list_files(self) -> List[Dict]:
        """List all files with their metadata"""
        return [{
            'name': f.name,
            'size': f.size,
            'created': f.created,
            'modified': f.modified
        } for f in self.files.values()]
    
    def get_file_info(self, name: str) -> Optional[Dict]:
        """Get detailed information about a file"""
        if name in self.files:
            f = self.files[name]
            return {
                'name': f.name,
                'size': f.size,
                'created': f.created,
                'modified': f.modified
            }
        return None