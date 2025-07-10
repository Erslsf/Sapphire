import base64
import hashlib
import json
import os
import re
import secrets
import sys
import uuid
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SapphireHood:
    """
    Manages Ethereum keys and user data "under the hood" for the GUI.
    """
    def __init__(self):
        # Define paths for key storage
        self.user_home = Path.home()
        self.app_data_dir = self.user_home / ".sapphire0.1.0"
        self.keys_dir = self.app_data_dir / "ethereum_keys"
        self.wallets_dir = self.keys_dir / "wallets"
        self.backups_dir = self.keys_dir / "backups"
        self.config_file = self.app_data_dir / "config.json"
        self.password_hash_file = self.app_data_dir / ".password_hash"
        self.lock_file = self.app_data_dir / ".locked"
        
        # Authentication flag
        self.is_authenticated = False
        self.encryption_key = None
        
        # Initialization should be called explicitly from the GUI

    def is_first_launch(self):
        """Checks if this is the first launch of the application."""
        return not self.app_data_dir.exists()

    def initialize(self, password: str):
        """
        Initialization with password verification.
        Returns (is_success, message)
        """
        if not self.is_first_launch():
            authenticated, message = self.authenticate_user(password)
            if authenticated:
                self.is_authenticated = True
                self.ensure_directories_exist()
                return True, "Authorization successful!"
            else:
                return False, message
        else:
            # This case is handled by setup_new_installation,
            # but initialize needs one password, and setup needs two.
            # The GUI should call setup_new_installation directly.
            return False, "First launch. Use setup_new_installation."

    def get_wallet_files(self):
        """Returns a list of wallet files."""
        if not self.wallets_dir.exists():
            return []
        return list(self.wallets_dir.glob("*.json"))

    def check_wallets(self):
        """
        Check for existing wallets.
        Returns a list of wallet information.
        """
        if not self.is_authenticated:
            raise PermissionError("Authentication required")

        wallet_files = self.get_wallet_files()
        wallets_info = []
        
        if not wallet_files:
            return []
        
        for wallet_file in wallet_files:
            try:
                wallet_info = self.get_wallet_info(wallet_file)
                if wallet_info:
                    wallets_info.append(wallet_info)
            except Exception:
                wallets_info.append({'name': wallet_file.name, 'address': 'Read error', 'error': True})
        return wallets_info

    def create_new_wallet(self, wallet_name: str):
        """Create a new Ethereum wallet"""
        if not self.is_authenticated:
            return False, "Authentication required", None
        if not wallet_name or len(wallet_name) == 0:
            return False, "Name cannot be empty", None

        private_key = secrets.token_hex(32)
        address = self.generate_eth_address(private_key)
        
        wallet_data = {
            "name": wallet_name,
            "address": address,
            "private_key": private_key,
            "created_at": datetime.now().isoformat(),
            "type": "generated",
            "network": "mainnet"
        }
        
        if self.save_wallet(wallet_data):
            return True, f"Wallet '{wallet_name}' created successfully!", {"address": address, "private_key": private_key}
        else:
            return False, "Error saving wallet", None

    def import_private_key(self, private_key: str, wallet_name: str):
        """Import wallet from private key"""
        if not self.is_authenticated:
            return False, "Authentication required"
        if not self.validate_private_key(private_key):
            return False, "Invalid private key format"
        if not wallet_name or len(wallet_name) == 0:
            return False, "Name cannot be empty"

        address = self.generate_eth_address(private_key)
        
        wallet_data = {
            "name": wallet_name,
            "address": address,
            "private_key": private_key,
            "created_at": datetime.now().isoformat(),
            "type": "imported",
            "network": "mainnet"
        }
        
        if self.save_wallet(wallet_data):
            return True, f"Wallet '{wallet_name}' imported successfully!"
        else:
            return False, "Error saving wallet"

    def import_mnemonic(self, mnemonic: str, wallet_name: str):
        """Import wallet from mnemonic phrase"""
        if not self.is_authenticated:
            return False, "Authentication required"

        words = mnemonic.strip().split()
        if len(words) not in [12, 24]:
            return False, f"Invalid word count: {len(words)}. Must be 12 or 24"
        if not wallet_name or len(wallet_name) == 0:
            return False, "Name cannot be empty"

        private_key = self.derive_private_key_from_mnemonic(mnemonic)
        address = self.generate_eth_address(private_key)
        
        wallet_data = {
            "name": wallet_name,
            "address": address,
            "private_key": private_key,
            "mnemonic": mnemonic,
            "created_at": datetime.now().isoformat(),
            "type": "mnemonic",
            "network": "mainnet"
        }

        if self.save_wallet(wallet_data):
            return True, f"Wallet '{wallet_name}' restored successfully!"
        else:
            return False, "Error saving wallet"

    def validate_private_key(self, private_key):
        """Validate a private key"""
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        if len(private_key) != 64:
            return False
        try:
            int(private_key, 16)
            return True
        except ValueError:
            return False

    def generate_eth_address(self, private_key):
        """Simplified Ethereum address generation"""
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        key_hash = hashlib.sha256(private_key.encode()).hexdigest()
        return "0x" + key_hash[:40]

    def derive_private_key_from_mnemonic(self, mnemonic):
        """Simplified private key derivation from mnemonic"""
        mnemonic_hash = hashlib.sha256(mnemonic.encode()).hexdigest()
        return mnemonic_hash

    def save_wallet(self, wallet_data):
        """Save a wallet in encrypted form"""
        try:
            safe_name = re.sub(r'[^\w\-_\.]', '_', wallet_data['name'])
            filename = f"{safe_name}_{wallet_data['address'][:8]}.json"
            filepath = self.wallets_dir / filename
            
            wallet_json = json.dumps(wallet_data, indent=2)
            encrypted_wallet = self.encryption_key.encrypt(wallet_json.encode())
            
            with open(filepath, 'wb') as f:
                f.write(encrypted_wallet)
            
            if os.name != 'nt':
                os.chmod(filepath, 0o600)
            
            return True
        except Exception:
            return False

    def get_wallet_info(self, wallet_file):
        """Get information about a wallet"""
        try:
            with open(wallet_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.encryption_key.decrypt(encrypted_data)
            wallet_data = json.loads(decrypted_data.decode())
            
            return {
                'name': wallet_data.get('name', 'Unknown'),
                'address': wallet_data.get('address', 'Unknown'),
                'type': wallet_data.get('type', 'Unknown'),
                'created_at': wallet_data.get('created_at', 'Unknown')
            }
        except Exception as e:
            # For a GUI, it's better to log or return an error than to print
            raise IOError(f"Error reading wallet {wallet_file.name}") from e

    def create_wallet_backup(self, wallet_name):
        """Create a backup of a wallet"""
        if not self.is_authenticated:
            return False, "Authentication required"
        try:
            wallet_files = list(self.wallets_dir.glob(f"{wallet_name}*.json"))
            if not wallet_files:
                return False, "Wallet not found"
            
            wallet_file = wallet_files[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{wallet_name}_{timestamp}.backup"
            backup_path = self.backups_dir / backup_name
            
            with open(wallet_file, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            
            if os.name != 'nt':
                os.chmod(backup_path, 0o600)
            
            return True, f"Backup created: {backup_path}"
        except Exception as e:
            return False, f"Error creating backup: {e}"

    def list_wallets(self):
        """List all wallets"""
        if not self.is_authenticated:
            raise PermissionError("Authentication required")
        return self.check_wallets()

    def setup_new_installation(self, password: str, confirm_password: str):
        """Setup on first launch"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if password != confirm_password:
            return False, "Passwords do not match"
        
        self.save_password_hash(password)
        self.encryption_key = self.derive_key(password)
        self.is_authenticated = True # <-- Set flag BEFORE creating directories
        self.ensure_directories_exist()
        return True, "Setup complete!"

    def authenticate_user(self, password: str):
        """Authenticate the user. Returns (bool, str)"""
        if not self.password_hash_file.exists():
            return False, "Password file not found. This might be the first launch."
        
        if self.verify_password(password):
            self.encryption_key = self.derive_key(password)
            return True, "Authentication successful"
        else:
            return False, "Invalid password"

    def save_password_hash(self, password):
        """Save the password hash"""
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        hash_data = {
            "salt": base64.b64encode(salt).decode('utf-8'),
            "hash": base64.b64encode(password_hash).decode('utf-8'),
            "iterations": 100000
        }
        try:
            self.app_data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.password_hash_file, 'w') as f:
                json.dump(hash_data, f)
            if os.name != 'nt':
                os.chmod(self.password_hash_file, 0o600)
        except Exception as e:
            raise IOError(f"Error saving password: {e}") from e

    def verify_password(self, password):
        """Verify the password"""
        try:
            with open(self.password_hash_file, 'r') as f:
                hash_data = json.load(f)
            salt = base64.b64decode(hash_data["salt"])
            stored_hash = base64.b64decode(hash_data["hash"])
            iterations = hash_data.get("iterations", 100000)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
            return password_hash == stored_hash
        except Exception:
            return False

    def derive_key(self, password):
        """Derive encryption key from password"""
        try:
            with open(self.password_hash_file, 'r') as f:
                hash_data = json.load(f)
            salt = base64.b64decode(hash_data["salt"])
        except Exception:
            salt = os.urandom(16) # Fallback, should not happen in normal flow
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def ensure_directories_exist(self):
        """Check and create all necessary directories"""
        if not self.is_authenticated:
            raise PermissionError("Authentication required to create directories")
        
        directories_to_create = [
            self.app_data_dir,
            self.keys_dir,
            self.wallets_dir,
            self.backups_dir
        ]
        
        for directory in directories_to_create:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    if os.name != 'nt':
                        os.chmod(directory, 0o700)
                except Exception as e:
                    raise IOError(f"Error creating directory {directory}: {e}") from e

    def show_existing_wallets(self):
        """Return information about existing wallets"""
        if not self.is_authenticated:
            raise PermissionError("Authentication required")
        return self.check_wallets()

    def import_keystore(self, keystore_path: str, keystore_password: str, wallet_name: str):
        """Import a wallet from a keystore file"""
        if not self.is_authenticated:
            return False, "Authentication required"
        if not os.path.exists(keystore_path):
            return False, "File not found"
        if not wallet_name:
            return False, "Name cannot be empty"

        try:
            with open(keystore_path, 'r') as f:
                keystore_data = json.load(f)
            
            if 'address' not in keystore_data:
                return False, "Invalid keystore file format"
            
            address = keystore_data['address']
            if not address.startswith('0x'):
                address = '0x' + address
            
            # In a real application, the private key would be decrypted here
            # using keystore_password. For this demo, we just save it.
            
            wallet_data = {
                "name": wallet_name,
                "address": address,
                "keystore": keystore_data,
                "created_at": datetime.now().isoformat(),
                "type": "keystore",
                "network": "mainnet",
            }
            
            if self.save_wallet(wallet_data):
                return True, f"Keystore wallet '{wallet_name}' imported successfully!"
            else:
                return False, "Error saving wallet"
        except Exception as e:
            return False, f"Error importing keystore: {e}"

    def add_watch_only_wallet(self, address: str, wallet_name: str):
        """Add a watch-only wallet"""
        if not self.is_authenticated:
            return False, "Authentication required"
        if not self.validate_ethereum_address(address):
            return False, "Invalid Ethereum address format"
        if not wallet_name:
            return False, "Name cannot be empty"

        wallet_data = {
            "name": wallet_name,
            "address": address,
            "created_at": datetime.now().isoformat(),
            "type": "watch_only",
            "network": "mainnet",
        }
        
        if self.save_wallet(wallet_data):
            return True, f"Address '{wallet_name}' added for watching!"
        else:
            return False, "Error saving wallet"

    def validate_ethereum_address(self, address):
        """Validate an Ethereum address"""
        if not isinstance(address, str) or not address.startswith('0x'):
            return False
        address_hex = address[2:]
        if len(address_hex) != 40:
            return False
        try:
            int(address_hex, 16)
            return True
        except ValueError:
            return False