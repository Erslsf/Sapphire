
# Sapphire - Decentralized Finance Application

![Sapphire Logo](assets/icons/sp.png)

## Description

Sapphire is a decentralized finance (DeFi) application with a graphical interface for managing Ethereum wallets. The application allows you to create, manage and securely store cryptocurrency wallets.

## Features

- 🔐 Secure wallet storage with encryption
- 💼 Multiple Ethereum wallet management
- 🎨 Modern dark interface
- 🔑 Password protection and local data storage
- 📱 Cross-platform compatibility (Windows, Linux, macOS)

## System Requirements

- Python 3.8 or higher
- PyQt6
- cryptography

## Quick Start

### Windows

1. Download or clone the repository
2. Run `run_sapphire.bat`
3. The script will automatically install dependencies and launch the application

### Linux/macOS

1. Download or clone the repository
2. Make the file executable: `chmod +x run_sapphire.sh`
3. Run: `./run_sapphire.sh`
4. The script will automatically install dependencies and launch the application

## Manual Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/sapphire.git
cd sapphire
```

### 2. Install dependencies

```bash
pip install -r requirements/requirements.txt
```

### 3. Run the application

```bash
python source/sapphire.py
```

## Project Structure

```
sapphire/
├── source/                 # Source code
│   ├── sapphire.py        # Main application file
│   ├── sapphire_hood.py   # Backend logic
│   └── __pycache__/       # Python cache
├── assets/                # Resources
│   └── icons/            # Interface icons
├── requirements/          # Dependencies
│   └── requirements.txt  # Python package list
├── run_sapphire.bat      # Launch for Windows
├── run_sapphire.sh       # Launch for Linux/macOS
├── README.md             # Documentation
└── policy.md             # Privacy policy
```

## Usage

### First Launch

1. On first launch, create a master password to protect your wallets
2. The password will be used to encrypt all data

### Creating a Wallet

1. Click the "+Add Wallet" button
2. Enter a name for the new wallet
3. The application will create a new Ethereum wallet and display the address and private key
4. **IMPORTANT**: Save the private key in a secure location!

### Managing Wallets

- Select a wallet from the list to view details
- Use the "Delete Wallet" button to remove a wallet
- All data is stored locally in encrypted form

## Security

- All wallet data is encrypted using your master password
- Private keys are stored only locally on your device
- The application does not send data to the internet
- Uses cryptographically strong encryption (Fernet)

## Development

### Architecture

- `sapphire.py` - main file with GUI interface (PyQt6)
- `sapphire_hood.py` - backend logic for wallet operations and encryption

### Development Requirements

```bash
pip install PyQt6 cryptography
```

## Support

If you encounter problems:

1. Make sure you have Python 3.8+ installed
2. Check that all dependencies are installed
3. Try running through the `run_sapphire.bat` or `run_sapphire.sh` scripts

## License

This project is distributed under the GNU General Public License v3.0 (GPL-3.0).

## Author

Lead Architect: B.E.S  
Developed in Astana, Kazakhstan

## Support the Project

**Development is entirely funded by donations!** 💝

Sapphire is a free and open-source project developed independently. All development, maintenance, and improvements depend entirely on community support through donations. Your contribution, no matter how small, helps keep this project alive and growing.

If you find Sapphire useful, consider supporting its development with a donation:

### Cryptocurrency Donations

| Currency | QR Code | Address |
|----------|---------|---------|
| **Bitcoin (BTC)** | ![BTC QR](qr/btc_qr.png) | `bc1ql9un693nq0p4wed6xx9kgna920hccf6e2mpyde` |
| **Ethereum (ETH)** | ![ETH QR](qr/eth_qr.png) | `EdC5D58f1b4c2AfAdc40a33fB4A0BDB2E43` |
| **Tether (USDT)** | ![USDT QR](qr/usdt_qr.png) | `TKKduSc6JfeDY22YyeTc2dxpb7qM1vMJaU` |

_Your support helps maintain and improve Sapphire. Thank you! 🙏_

## Version

Current version: 0.1.a1

---

⚠️ **Warning**: This is an alpha version. Use at your own risk. Always make backups of important data.
