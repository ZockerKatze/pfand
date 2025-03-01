import os
import shutil
import sys

# Get the parent directory (project root)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def print_status(message, success=True):
    """Print a status message with color if supported."""
    if os.name == 'nt':  # Windows
        print(message)
    else:  # Unix-like systems
        green = '\033[92m'
        red = '\033[91m'
        reset = '\033[0m'
        print(f"{green if success else red}{message}{reset}")

def remove_directory(path):
    """Remove a directory and all its contents."""
    full_path = os.path.join(ROOT_DIR, path)
    if os.path.exists(full_path):
        try:
            shutil.rmtree(full_path)
            print_status(f"✓ Removed directory: {path}")
        except Exception as e:
            print_status(f"✗ Failed to remove directory {path}: {str(e)}", False)

def remove_file(path):
    """Remove a single file."""
    full_path = os.path.join(ROOT_DIR, path)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            print_status(f"✓ Removed file: {path}")
        except Exception as e:
            print_status(f"✗ Failed to remove file {path}: {str(e)}", False)

def clean():
    """Clean all build artifacts from the repository."""
    print(f"Cleaning repository from: {ROOT_DIR}")
    
    # Directories to remove
    directories = [
        'build',
        'dist',
        '__pycache__',
        '.pytest_cache',
        '.coverage',
        '.mypy_cache',
    ]
    
    # Files to remove
    files = [
        'pfandrechner.spec',
        'build_log.txt',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.coverage',
        '.DS_Store'  # macOS system files
    ]
    
    # Remove directories
    for directory in directories:
        # Handle nested __pycache__ directories
        if directory == '__pycache__':
            for root, dirs, _ in os.walk(ROOT_DIR):
                for dir_name in dirs:
                    if dir_name == '__pycache__':
                        remove_directory(os.path.relpath(os.path.join(root, dir_name), ROOT_DIR))
        else:
            remove_directory(directory)
    
    # Remove files
    for file_pattern in files:
        if '*' in file_pattern:
            # Handle wildcard patterns
            import glob
            pattern_path = os.path.join(ROOT_DIR, file_pattern)
            for file_path in glob.glob(pattern_path):
                remove_file(os.path.relpath(file_path, ROOT_DIR))
        else:
            remove_file(file_pattern)
    
    print("\nRepository cleaned successfully!")
    print("\nThe following files and directories were removed (if they existed):")
    print("Directories:", ', '.join(directories))
    print("Files:", ', '.join(files))

if __name__ == "__main__":
    try:
        # Change to the project root directory
        os.chdir(ROOT_DIR)
        clean()
    except KeyboardInterrupt:
        print("\nCleaning interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1) 