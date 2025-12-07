# Network File System Simulator

A multi-user network file system with an interactive terminal interface.

## Usage

Run the terminal simulator:

```bash
python terminal.py
```

## Commands

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
