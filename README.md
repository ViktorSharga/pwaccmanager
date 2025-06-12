# Perfect World Account Manager

A Windows desktop application for managing Perfect World game accounts with multi-client support, batch file generation, and process tracking.

## Features

- **Account Management**: Add, edit, delete, and organize multiple game accounts
- **Multi-Client Support**: Launch and manage multiple game clients simultaneously
- **Process Tracking**: Monitor running game instances and terminate them as needed
- **Batch File Generation**: Automatically create batch files for quick game launching
- **Account Import**: Scan folders to import existing account batch files
- **Secure Storage**: Account data stored locally in JSON format
- **User-Friendly Interface**: Modern GUI built with PySide6 (Qt)

## Requirements

- Windows 10 or later
- Python 3.8 or higher
- Perfect World game client installed

## Installation

### Option 1: Running from Source

1. **Clone the repository**
   ```cmd
   git clone https://github.com/ViktorSharga/pwaccmanager.git
   cd pwaccmanager
   ```

2. **Create a virtual environment** (recommended)
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```cmd
   python main.py
   ```

### Option 2: Building Standalone Executable

1. **Install PyInstaller**
   ```cmd
   pip install pyinstaller
   ```

2. **Create the icon file (required for Windows)**
   ```cmd
   python create_icon.py
   ```

3. **Build the executable**
   ```cmd
   pyinstaller --onefile --windowed --name "PW Account Manager" --icon=icons/app-icon.ico main.py
   ```

4. **Find the executable**
   - The standalone exe will be in the `dist` folder
   - You can distribute this single file to run without Python installed

## First Time Setup

1. **Launch the application**
   - Run `python main.py` or the built executable

2. **Configure Game Folder**
   - Click the **Settings** button in the toolbar
   - Browse and select your Perfect World game folder
   - The folder must contain `elementclient.exe`
   - Click OK to save

3. **Add Your First Account**
   - Click **Add Account** in the toolbar
   - Enter login credentials and optional details
   - Click OK to save

## Usage Guide

### Managing Accounts

- **Add Account**: Click "Add Account" button and fill in the details
- **Edit Account**: Click the menu button (⋮) next to an account and select "Edit"
- **Delete Account**: Click the menu button (⋮) and select "Delete"
- **Launch Account**: Click the play button (▶) or select accounts and click "Launch Selected"
- **Close Account**: Click the close button (✖) or use "Close Selected"

### Batch Operations

- **Select Multiple Accounts**: Use the checkboxes to select multiple accounts
- **Launch Selected**: Launch all selected accounts at once
- **Close Selected**: Terminate all selected game clients

### Importing Existing Accounts

- Click **Scan Folder** to search for existing batch files
- The app will parse batch files and import account information
- Duplicate accounts (by login) will be skipped

### Account Fields

- **Login**: Required, must be unique
- **Password**: Required, stored locally
- **Character Name**: Optional, auto-selects character on login
- **Description**: Optional, for your reference
- **Owner**: Optional, to track account ownership

## Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed: `python --version`
- Check all dependencies are installed: `pip install -r requirements.txt`
- Run from command line to see error messages

### Can't find game folder
- Make sure Perfect World is installed
- The game folder must contain `elementclient.exe`
- Try browsing to the folder manually in Settings

### Game won't launch
- Verify the game folder path in Settings
- Check if the game launches normally without the manager
- Ensure no antivirus is blocking the batch files
- Run the application as Administrator if needed

### Process tracking issues
- The app uses `psutil` which may require admin privileges
- Try running as Administrator if processes aren't tracked properly

## Security Notes

- Account data is stored locally in `accounts.json`
- Passwords are stored in plain text (required for auto-login)
- Keep your `accounts.json` file secure
- The app does not send data over the network

## File Structure

```
pwaccmanager/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── settings.json        # App settings (auto-created)
├── accounts.json        # Account data (auto-created)
├── icons/              # Application icons
│   ├── app-icon.svg    # Main application icon
│   └── generate_icons.py # Icon generation script
├── core/               # Business logic modules
├── ui/                 # User interface modules
└── utils/              # Utility functions
```

## Building from Source

### Development Setup

1. **Install development dependencies**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller black pylint
   ```

2. **Optional: Generate icon files**
   ```cmd
   pip install Pillow cairosvg
   cd icons
   python generate_icons.py
   ```

3. **Run tests** (if available)
   ```cmd
   python -m pytest
   ```

4. **Format code**
   ```cmd
   black .
   ```

### Creating a Release

1. **Update version** in main.py if needed
2. **Create icon file**
   ```cmd
   python create_icon.py
   ```
3. **Build executable**
   ```cmd
   pyinstaller --onefile --windowed --name "PW Account Manager" --icon=icons/app-icon.ico main.py
   ```
4. **Test the executable** thoroughly
5. **Create release** on GitHub with the exe file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your fork
5. Create a Pull Request

## License

This project is provided as-is for personal use with Perfect World game client.

## Support

For issues, questions, or suggestions:
- Open an issue on [GitHub](https://github.com/ViktorSharga/pwaccmanager/issues)
- Check existing issues before creating a new one

## Disclaimer

This is an unofficial tool and is not affiliated with Perfect World Entertainment. Use at your own risk.