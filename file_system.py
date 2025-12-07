"""
Multi-User Network File System Simulator
Supports multiple users with isolated file systems
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Union


class File:
    """Represents a file in the file system"""
    
    def __init__(self, name: str, content: str = "", owner: str = ""):
        self.name = name
        self.content = content
        self.owner = owner
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.size = len(content)
    
    def read(self) -> str:
        """Read file content"""
        return self.content
    
    def write(self, content: str):
        """Write content to file"""
        self.content = content
        self.size = len(content)
        self.modified_at = datetime.now()
    
    def append(self, content: str):
        """Append content to file"""
        self.content += content
        self.size = len(self.content)
        self.modified_at = datetime.now()
    
    def get_info(self) -> Dict:
        """Get file information"""
        return {
            'name': self.name,
            'type': 'file',
            'owner': self.owner,
            'size': self.size,
            'created': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'modified': self.modified_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Directory:
    """Represents a directory in the file system"""
    
    def __init__(self, name: str, owner: str = "", parent=None):
        self.name = name
        self.owner = owner
        self.parent = parent
        self.children: Dict[str, Union[File, 'Directory']] = {}
        self.created_at = datetime.now()
    
    def add_file(self, file: File) -> bool:
        """Add a file to directory"""
        if file.name in self.children:
            return False
        self.children[file.name] = file
        return True
    
    def add_directory(self, directory: 'Directory') -> bool:
        """Add a subdirectory"""
        if directory.name in self.children:
            return False
        self.children[directory.name] = directory
        directory.parent = self
        return True
    
    def remove(self, name: str) -> bool:
        """Remove a file or directory"""
        if name in self.children:
            del self.children[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[Union[File, 'Directory']]:
        """Get a file or directory by name"""
        return self.children.get(name)
    
    def list_contents(self) -> List[Dict]:
        """List all contents in directory"""
        contents = []
        for name, item in sorted(self.children.items()):
            if isinstance(item, File):
                contents.append(item.get_info())
            else:
                contents.append({
                    'name': name,
                    'type': 'directory',
                    'owner': item.owner,
                    'created': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        return contents
    
    def get_path(self) -> str:
        """Get full path of directory"""
        if self.parent is None:
            return "/"
        parent_path = self.parent.get_path()
        if parent_path == "/":
            return f"/{self.name}"
        return f"{parent_path}/{self.name}"


class FileSystem:
    """Main file system class managing files and directories"""
    
    def __init__(self, owner: str = "system"):
        self.root = Directory("/", owner)
        self.current_directory = self.root
    
    def get_current_path(self) -> str:
        """Get current directory path"""
        return self.current_directory.get_path()
    
    def create_file(self, name: str, owner: str, content: str = "") -> tuple[bool, str]:
        """Create a new file in current directory"""
        if name in self.current_directory.children:
            return False, f"File or directory '{name}' already exists"
        
        file = File(name, content, owner)
        if self.current_directory.add_file(file):
            return True, f"File '{name}' created successfully"
        return False, "Failed to create file"
    
    def create_directory(self, name: str, owner: str) -> tuple[bool, str]:
        """Create a new directory"""
        if name in self.current_directory.children:
            return False, f"File or directory '{name}' already exists"
        
        if name in [".", ".."]:
            return False, "Invalid directory name"
        
        directory = Directory(name, owner, self.current_directory)
        if self.current_directory.add_directory(directory):
            return True, f"Directory '{name}' created successfully"
        return False, "Failed to create directory"
    
    def change_directory(self, path: str) -> tuple[bool, str]:
        """Change current directory"""
        if path == "/":
            self.current_directory = self.root
            return True, "Changed to root directory"
        
        if path == "..":
            if self.current_directory.parent:
                self.current_directory = self.current_directory.parent
                return True, f"Changed to {self.get_current_path()}"
            return False, "Already at root directory"
        
        if path == ".":
            return True, f"Current directory: {self.get_current_path()}"
        
        # Handle absolute paths
        if path.startswith("/"):
            target = self._navigate_absolute_path(path)
            if target and isinstance(target, Directory):
                self.current_directory = target
                return True, f"Changed to {self.get_current_path()}"
            return False, f"Directory '{path}' not found"
        
        # Handle relative paths
        item = self.current_directory.get(path)
        if item and isinstance(item, Directory):
            self.current_directory = item
            return True, f"Changed to {self.get_current_path()}"
        return False, f"Directory '{path}' not found"
    
    def _navigate_absolute_path(self, path: str) -> Optional[Union[File, Directory]]:
        """Navigate to an absolute path"""
        if path == "/":
            return self.root
        
        parts = path.strip("/").split("/")
        current = self.root
        
        for part in parts:
            if not isinstance(current, Directory):
                return None
            item = current.get(part)
            if item is None:
                return None
            current = item
        
        return current
    
    def list_directory(self) -> List[Dict]:
        """List contents of current directory"""
        return self.current_directory.list_contents()
    
    def read_file(self, name: str) -> tuple[bool, str]:
        """Read file content"""
        item = self.current_directory.get(name)
        if item is None:
            return False, f"File '{name}' not found"
        if not isinstance(item, File):
            return False, f"'{name}' is a directory, not a file"
        return True, item.read()
    
    def write_file(self, name: str, content: str, owner: str) -> tuple[bool, str]:
        """Write content to file (creates if doesn't exist)"""
        item = self.current_directory.get(name)
        if item is None:
            return self.create_file(name, owner, content)
        
        if not isinstance(item, File):
            return False, f"'{name}' is a directory, not a file"
        
        item.write(content)
        return True, f"File '{name}' updated successfully"
    
    def append_file(self, name: str, content: str) -> tuple[bool, str]:
        """Append content to file"""
        item = self.current_directory.get(name)
        if item is None:
            return False, f"File '{name}' not found"
        if not isinstance(item, File):
            return False, f"'{name}' is a directory, not a file"
        
        item.append(content)
        return True, f"Content appended to '{name}'"
    
    def delete(self, name: str) -> tuple[bool, str]:
        """Delete a file or directory"""
        item = self.current_directory.get(name)
        if item is None:
            return False, f"'{name}' not found"
        
        if isinstance(item, Directory) and len(item.children) > 0:
            return False, f"Directory '{name}' is not empty"
        
        if self.current_directory.remove(name):
            return True, f"'{name}' deleted successfully"
        return False, f"Failed to delete '{name}'"
    
    def move(self, source: str, destination: str) -> tuple[bool, str]:
        """Move a file or directory"""
        source_item = self.current_directory.get(source)
        if source_item is None:
            return False, f"Source '{source}' not found"
        
        dest_item = self.current_directory.get(destination)
        if dest_item is None:
            return False, f"Destination '{destination}' not found"
        
        if not isinstance(dest_item, Directory):
            return False, f"Destination '{destination}' is not a directory"
        
        # Check if name already exists in destination
        if source in dest_item.children:
            return False, f"'{source}' already exists in '{destination}'"
        
        # Move the item
        self.current_directory.remove(source)
        if isinstance(source_item, File):
            dest_item.add_file(source_item)
        else:
            dest_item.add_directory(source_item)
        
        return True, f"Moved '{source}' to '{destination}'"
    
    def copy_file(self, source: str, destination: str, owner: str) -> tuple[bool, str]:
        """Copy a file"""
        source_item = self.current_directory.get(source)
        if source_item is None:
            return False, f"Source file '{source}' not found"
        
        if not isinstance(source_item, File):
            return False, f"'{source}' is not a file"
        
        # Create a copy
        new_file = File(destination, source_item.content, owner)
        if self.current_directory.add_file(new_file):
            return True, f"File copied from '{source}' to '{destination}'"
        return False, f"File '{destination}' already exists"


class User:
    """Represents a user in the system"""
    
    def __init__(self, username: str, lastname: str):
        self.username = username
        self.lastname = lastname
        self.file_system = FileSystem(username)
        self.logged_in = True
    
    def get_prompt(self) -> str:
        """Get terminal prompt for user"""
        path = self.file_system.get_current_path()
        return f"{self.lastname}@filesystem:{path}$ "


class NetworkFileSystem:
    """Multi-user network file system"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
    
    def create_user(self, username: str, lastname: str) -> tuple[bool, str]:
        """Create a new user"""
        if username in self.users:
            return False, f"User '{username}' already exists"
        
        self.users[username] = User(username, lastname)
        return True, f"User '{username}' created successfully"
    
    def login(self, username: str) -> tuple[bool, str]:
        """Login a user"""
        if username not in self.users:
            return False, f"User '{username}' not found"
        
        self.current_user = self.users[username]
        self.current_user.logged_in = True
        return True, f"Welcome {self.current_user.lastname}!"
    
    def logout(self) -> tuple[bool, str]:
        """Logout current user"""
        if self.current_user:
            username = self.current_user.username
            self.current_user.logged_in = False
            self.current_user = None
            return True, f"User '{username}' logged out"
        return False, "No user logged in"
    
    def get_current_user(self) -> Optional[User]:
        """Get current logged in user"""
        return self.current_user
    
    def list_users(self) -> List[str]:
        """List all registered users"""
        return list(self.users.keys())
