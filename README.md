# Pfandrechner Application Suite

A comprehensive application for managing deposit (Pfand) calculations with a modern GUI and build utilities.

## 🗂️ Project Structure

### Core Application (`main.py`)
The main application for deposit calculations featuring:
- 💰 Deposit calculation for various container types
- 🏆 Achievement system with unlockable rewards
- 📊 Deposit history tracking and export
- 💾 Data persistence and management
- 🖼️ Image support for containers and achievements
- 🌟 Modern tkinter-based GUI

Key Features:
- Real-time deposit calculations
- Achievement system with multiple tiers
- History tracking with CSV export
- Automatic data saving
- Image management system
- Keyboard shortcuts for common actions

### Build Utility (`buildutil/`)
A suite of tools for building, managing, and deploying the application.

#### GUI Interface (`buildutil/gui.py`)
Modern graphical interface for build management:
- 🎨 Professional UI with Light/Dark themes
- 🔄 Real-time build monitoring
- 📝 Log management system
- ⌨️ Keyboard shortcuts
- 🛠️ Build and clean operations
- 💡 Enhanced tooltips

Shortcuts:
- `Ctrl+B` - Build executable
- `Ctrl+C` - Clean repository
- `Ctrl+S` - Save log
- `Ctrl+L` - Clear log
- `Ctrl+T` - Toggle theme

#### Build Script (`buildutil/build.py`)
Handles the creation of executables:
- 📦 PyInstaller integration
- 🔄 Automatic dependency management
- 📁 Resource bundling
- 📝 Build logging
- ⚠️ Error handling
- 🧹 Build cleanup

Features:
- Automatic package installation
- Resource management
- Cross-platform support
- Build verification
- Progress reporting

#### Cleanup Utility (`buildutil/clean.py`)
Manages repository cleanliness:
- 🧹 Build artifact removal
- 🗑️ Cache cleanup
- 🔍 Pattern matching
- 🎨 Colored output
- ✅ Safe operations

Capabilities:
- Intelligent cleanup
- Safe file handling
- Progress feedback
- Dry-run support

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Required packages:
  ```
  tkinter
  pillow
  tkcalendar
  pyinstaller
  ```

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pfandrechner
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Running the Application
```bash
python main.py
=======
git clone https://github.com/ZockerKatze/pfand.git
cd pfand
```

#### Building the Executable
1. Using the GUI:
   ```bash
   python buildutil/gui.py
   ```

2. Using command line:
   ```bash
   python buildutil/build.py
   ```

#### Cleaning the Repository
1. Using the GUI:
   - Launch the build utility
   - Click "Clean Repository" or use `Ctrl+C`

2. Using command line:
   ```bash
   python buildutil/clean.py
   ```

## 🎨 Themes and Styling / For buildutil

### Light Theme
```
Background: #ffffff
Text: #2c3e50
Buttons: #3498db
Accents: #34495e
Success: #2ecc71
Error: #e74c3c
```

### Dark Theme
```
Background: #2c3e50
Text: #ecf0f1
Buttons: #3498db
Accents: #95a5a6
Success: #27ae60
Error: #c0392b
```

## 🔄 File Interactions

### Application Flow
1. `main.py` - Core application
   - Handles user interface
   - Manages data
   - Processes calculations
   - Tracks achievements

2. `buildutil/gui.py` - Build interface
   - Coordinates build operations
   - Manages cleaning operations
   - Handles logging
   - Provides user feedback

3. `buildutil/build.py` - Build operations
   - Creates executable
   - Manages dependencies
   - Bundles resources
   - Handles errors

4. `buildutil/clean.py` - Cleanup operations
   - Removes build artifacts
   - Cleans caches
   - Maintains repository

## 🛠️ Development

### Code Structure
- Modern Python practices
- Object-oriented design
- Event-driven architecture
- Thread-safe operations
- Error handling
- Resource management

### Best Practices
- Consistent error handling
- Professional logging
- Safe file operations
- Cross-platform compatibility
- User-centric design
- Clean code principles


### Version Control
- Regular commits
- Feature branches
- Version tagging
- Change logging

## 📝 License
MIT
=======
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 👏

- Thanks to all contributors and users of the application
- Icons and images used in this project 

