from file_system import NetworkFileSystem, User
import sys


class TerminalSimulator:
    """Interactive terminal for the file system"""
    
    def __init__(self):
        self.nfs = NetworkFileSystem()
        self.running = True
        self.commands = {
            'help': self.help_command,
            'createuser': self.create_user_command,
            'login': self.login_command,
            'logout': self.logout_command,
            'users': self.list_users_command,
            'whoami': self.whoami_command,
            'pwd': self.pwd_command,
            'ls': self.ls_command,
            'cd': self.cd_command,
            'mkdir': self.mkdir_command,
            'touch': self.touch_command,
            'write': self.write_command,
            'read': self.read_command,
            'cat': self.read_command,
            'rm': self.rm_command,
            'mv': self.mv_command,
            'cp': self.cp_command,
            'clear': self.clear_command,
            'exit': self.exit_command,
            'quit': self.exit_command
        }
    
    def print_banner(self):
        """Print welcome banner"""
        print("=" * 60)
        print("  NETWORK FILE SYSTEM SIMULATOR - Multi-User Environment")
        print("=" * 60)
        print("Type 'help' for available commands")
        print("Type 'createuser <username> <lastname>' to create a user")
        print("Type 'login <username>' to login")
        print("-" * 60)
    
    def help_command(self, args):
        """Display help information"""
        help_text = """
Available Commands:
==================

USER MANAGEMENT:
  createuser <username> <lastname>  - Create a new user account
  login <username>                  - Login as a user
  logout                            - Logout current user
  users                             - List all registered users
  whoami                            - Show current user information

FILE SYSTEM NAVIGATION:
  pwd                               - Print working directory
  ls                                - List directory contents
  cd <directory>                    - Change directory
  cd ..                             - Go to parent directory
  cd /                              - Go to root directory

FILE & DIRECTORY OPERATIONS:
  mkdir <dirname>                   - Create a new directory
  touch <filename>                  - Create an empty file
  write <filename> <content>        - Write content to a file
  read <filename>                   - Read file content
  cat <filename>                    - Read file content (alias for read)
  rm <name>                         - Delete a file or empty directory
  mv <source> <destination>         - Move file/directory to another directory
  cp <source> <destination>         - Copy a file

SYSTEM:
  clear                             - Clear the screen
  exit / quit                       - Exit the terminal

Note: Most file operations require you to be logged in as a user.
"""
        print(help_text)
    
    def create_user_command(self, args):
        """Create a new user"""
        if len(args) < 2:
            print("Usage: createuser <username> <lastname>")
            return
        
        username = args[0]
        lastname = args[1]
        success, message = self.nfs.create_user(username, lastname)
        print(message)
    
    def login_command(self, args):
        """Login a user"""
        if len(args) < 1:
            print("Usage: login <username>")
            return
        
        username = args[0]
        success, message = self.nfs.login(username)
        print(message)
    
    def logout_command(self, args):
        """Logout current user"""
        success, message = self.nfs.logout()
        print(message)
    
    def list_users_command(self, args):
        """List all users"""
        users = self.nfs.list_users()
        if not users:
            print("No users registered")
            return
        
        print("Registered Users:")
        for user in users:
            status = "✓" if self.nfs.users[user].logged_in else " "
            print(f"  [{status}] {user} ({self.nfs.users[user].lastname})")
    
    def whoami_command(self, args):
        """Show current user"""
        user = self.nfs.get_current_user()
        if user:
            print(f"Current user: {user.username} (Last name: {user.lastname})")
            print(f"Working directory: {user.file_system.get_current_path()}")
        else:
            print("No user logged in")
    
    def check_login(self) -> bool:
        """Check if a user is logged in"""
        if not self.nfs.get_current_user():
            print("Error: No user logged in. Please login first.")
            return False
        return True
    
    def pwd_command(self, args):
        """Print working directory"""
        if not self.check_login():
            return
        
        user = self.nfs.get_current_user()
        print(user.file_system.get_current_path())
    
    def ls_command(self, args):
        """List directory contents"""
        if not self.check_login():
            return
        
        user = self.nfs.get_current_user()
        contents = user.file_system.list_directory()
        
        if not contents:
            print("(empty directory)")
            return
        
        # Print header
        print(f"{'Type':<12} {'Name':<20} {'Size':<10} {'Owner':<15} {'Modified'}")
        print("-" * 80)
        
        # Print contents
        for item in contents:
            item_type = item['type']
            name = item['name']
            size = str(item.get('size', '-')) if item_type == 'file' else '<DIR>'
            owner = item['owner']
            modified = item.get('modified', item.get('created', ''))
            
            print(f"{item_type:<12} {name:<20} {size:<10} {owner:<15} {modified}")
    
    def cd_command(self, args):
        """Change directory"""
        if not self.check_login():
            return
        
        if len(args) < 1:
            print("Usage: cd <directory>")
            return
        
        user = self.nfs.get_current_user()
        path = args[0]
        success, message = user.file_system.change_directory(path)
        if not success:
            print(f"Error: {message}")
    
    def mkdir_command(self, args):
        """Create a directory"""
        if not self.check_login():
            return
        
        if len(args) < 1:
            print("Usage: mkdir <directory_name>")
            return
        
        user = self.nfs.get_current_user()
        dirname = args[0]
        success, message = user.file_system.create_directory(dirname, user.username)
        print(message)
    
    def touch_command(self, args):
        """Create an empty file"""
        if not self.check_login():
            return
        
        if len(args) < 1:
            print("Usage: touch <filename>")
            return
        
        user = self.nfs.get_current_user()
        filename = args[0]
        success, message = user.file_system.create_file(filename, user.username)
        print(message)
    
    def write_command(self, args):
        """Write content to a file"""
        if not self.check_login():
            return
        
        if len(args) < 2:
            print("Usage: write <filename> <content>")
            return
        
        user = self.nfs.get_current_user()
        filename = args[0]
        content = ' '.join(args[1:])
        success, message = user.file_system.write_file(filename, content, user.username)
        print(message)
    
    def read_command(self, args):
        """Read file content"""
        if not self.check_login():
            return
        
        if len(args) < 1:
            print("Usage: read <filename>")
            return
        
        user = self.nfs.get_current_user()
        filename = args[0]
        success, content = user.file_system.read_file(filename)
        
        if success:
            print(f"--- Contents of '{filename}' ---")
            print(content)
            print("--- End of file ---")
        else:
            print(f"Error: {content}")
    
    def rm_command(self, args):
        """Delete a file or directory"""
        if not self.check_login():
            return
        
        if len(args) < 1:
            print("Usage: rm <name>")
            return
        
        user = self.nfs.get_current_user()
        name = args[0]
        success, message = user.file_system.delete(name)
        print(message)
    
    def mv_command(self, args):
        """Move a file or directory"""
        if not self.check_login():
            return
        
        if len(args) < 2:
            print("Usage: mv <source> <destination_directory>")
            return
        
        user = self.nfs.get_current_user()
        source = args[0]
        destination = args[1]
        success, message = user.file_system.move(source, destination)
        print(message)
    
    def cp_command(self, args):
        """Copy a file"""
        if not self.check_login():
            return
        
        if len(args) < 2:
            print("Usage: cp <source_file> <destination_file>")
            return
        
        user = self.nfs.get_current_user()
        source = args[0]
        destination = args[1]
        success, message = user.file_system.copy_file(source, destination, user.username)
        print(message)
    
    def clear_command(self, args):
        """Clear the screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def exit_command(self, args):
        """Exit the terminal"""
        print("Exiting Network File System. Goodbye!")
        self.running = False
    
    def parse_command(self, input_str: str):
        """Parse and execute a command"""
        parts = input_str.strip().split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:]
        
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                print(f"Error executing command: {e}")
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")
    
    def get_prompt(self) -> str:
        """Get the current prompt"""
        user = self.nfs.get_current_user()
        if user:
            return user.get_prompt()
        return "guest@filesystem$ "
    
    def run(self):
        """Main terminal loop"""
        self.clear_command([])
        self.print_banner()
        
        while self.running:
            try:
                prompt = self.get_prompt()
                user_input = input(prompt)
                self.parse_command(user_input)
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to leave the terminal")
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")


def main():
    terminal = TerminalSimulator()
    terminal.run()


if __name__ == "__main__":
    main()
