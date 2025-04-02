import os
import sys
import shutil
import subprocess
import site
import datetime
import traceback

# Get the parent directory (project root)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def log_message(message, log_file='build_log.txt'):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(message)
    with open(os.path.join(ROOT_DIR, log_file), 'a', encoding='utf-8') as f:
        f.write(log_entry)

def get_pyinstaller_path():
    log_message("Locating PyInstaller...")
    if os.name == 'nt':  # Windows
        try:
            scripts_dir = os.path.join(site.getsitepackages()[0], 'Scripts')
            pyinstaller_exe = os.path.join(scripts_dir, 'pyinstaller.exe')
            log_message(f"Checking PyInstaller at: {pyinstaller_exe}")
            if os.path.exists(pyinstaller_exe):
                log_message(f"Found PyInstaller at: {pyinstaller_exe}")
                return pyinstaller_exe
        except Exception as e:
            log_message(f"Error locating PyInstaller: {str(e)}")
    
    log_message("Using default 'pyinstaller' command")
    return 'pyinstaller'

def check_required_files():
    log_message("Checking required files...")
    required_files = {
        'main.py': "Main application file",
        'images': "Images directory"
    }
    
    missing_files = []
    for file, description in required_files.items():
        full_path = os.path.join(ROOT_DIR, file)
        if not os.path.exists(full_path):
            missing_files.append(f"- {file} ({description})")
            log_message(f"Missing required file: {file}")
        else:
            log_message(f"Found required file: {file}")
    
    if missing_files:
        error_msg = "\nError: Missing required files:\n" + '\n'.join(missing_files)
        log_message(error_msg)
        log_message("Please ensure all required files are present in the correct directory.")
        sys.exit(1)

def create_images_directory():
    log_message("Checking images directory...")
    images_dir = os.path.join(ROOT_DIR, 'images')
    if not os.path.exists(images_dir):
        log_message("Creating images directory...")
        try:
            os.makedirs(images_dir)
            log_message("Images directory created successfully")
            log_message("Warning: images directory was created but is empty. Please add required images.")
        except Exception as e:
            log_message(f"Error creating images directory: {str(e)}")
            raise

def install_requirements():
    log_message("Installing required packages...")
    try:
        # First try to uninstall PyInstaller to ensure a clean installation
        try:
            log_message("Uninstalling existing PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "pyinstaller"])
        except:
            log_message("No existing PyInstaller installation found or could not uninstall")

        # Install/Upgrade pip first
        log_message("Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install each package separately to better handle errors
        packages = [
            "pyinstaller",
            "pillow",
            "opencv-python",
            "pyzbar",
            "numpy",
            "tkcalendar",
            "requests"
        ]
        for package in packages:
            log_message(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
                log_message(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                log_message(f"Error installing {package}: {str(e)}")
                raise
            
        log_message("Successfully installed all required packages.")
    except Exception as e:
        log_message(f"Error installing packages: {str(e)}")
        log_message("Please try installing packages manually using:")
        log_message("pip install pyinstaller pillow tkcalendar opencv-python pyzbar numpy")
        raise

def cleanup():
    log_message("Cleaning up previous builds...")
    dirs_to_remove = ['build', 'dist']
    files_to_remove = ['pfandrechner.spec']
    
    for dir_name in dirs_to_remove:
        full_path = os.path.join(ROOT_DIR, dir_name)
        if os.path.exists(full_path):
            try:
                shutil.rmtree(full_path)
                log_message(f"Removed {dir_name} directory")
            except Exception as e:
                log_message(f"Warning: Could not remove {dir_name}: {str(e)}")
    
    for file_name in files_to_remove:
        full_path = os.path.join(ROOT_DIR, file_name)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                log_message(f"Removed {file_name}")
            except Exception as e:
                log_message(f"Warning: Could not remove {file_name}: {str(e)}")

def copy_resources():
    log_message("Copying resources...")
    try:
        if not os.path.exists('dist/pfandrechner/images'):
            os.makedirs('dist/pfandrechner/images')
            log_message("Created dist/pfandrechner/images directory")
        
        # Copy all files from images directory
        if os.path.exists('images'):
            for file in os.listdir('images'):
                src = os.path.join('images', file)
                dst = os.path.join('dist/pfandrechner/images', file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    log_message(f"Copied {file} to dist directory")
        
        resource_files = ['README.md', 'LICENSE']
        for file in resource_files:
            if os.path.exists(file):
                shutil.copy2(file, 'dist/pfandrechner/')
                log_message(f"Copied {file} to dist directory")
    except Exception as e:
        log_message(f"Error copying resources: {str(e)}")
        raise

def build():
    log_message("Building executable...")
    try:
        # Change to the root directory for the build process
        os.chdir(ROOT_DIR)
        
        # Build the PyInstaller command arguments
        cmd = [
            sys.executable,
            '-m',
            'PyInstaller',
            '--name=pfandrechner',
            '--windowed',
            '--onedir',
            '--clean',
            '--noconfirm',
            '--log-level=INFO',
            '--hidden-import=PIL._tkinter_finder',
            '--hidden-import=tkcalendar',
            '--hidden-import=cv2',
            '--hidden-import=pyzbar.pyzbar',
            '--hidden-import=numpy',
            '--collect-all=tkcalendar',
            '--collect-all=opencv-python',
            '--collect-all=pyzbar',
            '--collect-all=numpy'
        ]
        
        # Add icon if available
        if os.path.exists('images/auszeichnung.png'):
            cmd.append('--icon=images/auszeichnung.png')
            log_message("Added icon to build command")
        
        # Add data files
        if os.path.exists('images'):
            separator = ';' if os.name == 'nt' else ':'
            cmd.extend(['--add-data', f'images{separator}images'])
            log_message("Added images directory to build command")
        
        # Add the main script
        cmd.append('main.py')  # Changed from run.py to main.py
        
        log_message("Running PyInstaller with command:")
        log_message(' '.join(cmd))
        log_message("\nThis may take several minutes. Please wait...")
        
        # Run PyInstaller with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                line = line.strip()
                if line:  # Only log non-empty lines
                    log_message(line)
        
        returncode = process.poll()
        if returncode != 0:
            log_message("\nError: PyInstaller failed.")
            raise Exception(f"PyInstaller failed with return code {returncode}")
        else:
            log_message("\nPyInstaller completed successfully!")
            
    except Exception as e:
        log_message(f"Error during PyInstaller execution: {str(e)}")
        log_message("Full traceback:")
        log_message(traceback.format_exc())
        raise

def main():
    # Clear the log file at the start
    with open(os.path.join(ROOT_DIR, 'build_log.txt'), 'w', encoding='utf-8') as f:
        f.write("")
    
    log_message("Starting build process...")
    log_message(f"Project root directory: {ROOT_DIR}")
    log_message(f"Python version: {sys.version}")
    log_message(f"Operating system: {os.name}")
    log_message(f"Python executable: {sys.executable}")
    
    try:
        check_required_files()
        create_images_directory()
        install_requirements()
        cleanup()
        build()
        copy_resources()
        
        log_message("\nBuild completed successfully!")
        log_message("The executable can be found in the 'dist/pfandrechner' directory.")
        
        # Print contents of dist directory
        dist_dir = os.path.join(ROOT_DIR, 'dist/pfandrechner')
        log_message("\nContents of dist/pfandrechner directory:")
        for root, dirs, files in os.walk(dist_dir):
            level = root.replace(dist_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            log_message(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                log_message(f"{subindent}{f}")
                
    except Exception as e:
        log_message(f"\nError during build: {str(e)}")
        log_message("Full traceback:")
        log_message(traceback.format_exc())
        log_message("\nFor more help, please check the README.md file or report this issue on GitHub.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
