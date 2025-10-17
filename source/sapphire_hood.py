"""
Manages Ethereum keys and user data "under the hood" for the GUI.
Designed by DEECKER with ❤️, in Astana, Kazakhstan.
Handles:
- Initialization and setup
- Password management and authentication
- Wallet creation, import, and management
- Encryption and decryption of wallet files
- QR code generation for payments
"""

import base64
import hashlib
import json
import os
import re
import secrets
import sys
import uuid
import requests
from datetime import datetime
from pathlib import Path
from io import BytesIO
from hashlib import sha256
import base58
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ecdsa import SigningKey, SECP256k1
from tronpy import Tron
from eth_account import Account
from tronpy.keys import PrivateKey
try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import VerticalBarsDrawer
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False



class SapphireHood:
    """
    Manages Ethereum keys and user data "under the hood" for the GUI.
    """
    def __init__(self):
        # Define paths for key storage
        self.user_home = Path.home()
        self.app_data_dir = self.user_home / ".sapphire.data"
        self.eth_dir = self.app_data_dir / "ethereum"
        self.btc_dir = self.app_data_dir / "bitcoin"
        self.tron_dir = self.app_data_dir / "tron"
        self.eth_wallets_dir = self.eth_dir / "eth_wallets"
        self.btc_wallets_dir = self.btc_dir / "btc_wallets"
        self.tron_wallets_dir = self.tron_dir / "tron_wallets"
        self.backups_dir = self.eth_dir / "backups"
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
    def get_btc_balance(self, address):
        url = f"https://mempool.space/api/address/{address}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                balance_sats = data.get("chain_stats", {}).get("funded_txo_sum", 0) - data.get("chain_stats", {}).get("spent_txo_sum", 0)
                balance_btc = balance_sats / 1e8
                return balance_btc
            else:
                return None
        except Exception:
            return None
    
    def get_eth_balance(self, address):
        url = f'https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("ETH", {}).get("balance", 0)
            else:
                return None
        except Exception:
            return None
        
    def get_binance_klines(self, symbol="BTCUSDT", interval="1h", limit=100) -> list[dict]:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        data = requests.get(url).json()
        candles = [
            {
                "time": k[0] // 1000,  # в секундах
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4])
            }
            for k in data
        ]
        return candles
    
    def get_tron_balance(self, address):
        url = f'https://api.trongrid.io/v1/accounts/{address}'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    return data['data'][0].get('balance', 0) / 1e6  # TRX has 6 decimals
                else:
                    return 0
            else:
                return None
        except Exception:
            return None
    
    def get_wallet_files(self):
        """Returns a list of wallet files."""
        if not self.eth_wallets_dir.exists():
            return []
        return list(self.eth_wallets_dir.glob("*.json"))

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
    #+++
    def  generate_eth_address(self):
        account = Account.create()
        private_key = account.key.hex()
        address = account.address
        return private_key, address
    #+++
    def generate_tron_address(self):
        # Создаем приватный ключ
        priv_key = PrivateKey.random()
        # Получаем адрес
        address = priv_key.public_key.to_base58check_address()
        private_key = priv_key.hex()
        return private_key, address
    #+++
    def generate_btc_address(self):
        """
        Генерирует новый Bitcoin-кошелёк:
        - Приватный ключ
        - Публичный ключ
        - Bitcoin-адрес
        """
        private_key = os.urandom(32)
        private_key_hex = private_key.hex()

        sk = SigningKey.from_string(private_key, curve=SECP256k1)
        verifying_key = sk.get_verifying_key()
        public_key_bytes = b'\x04' + verifying_key.to_string()  # некомпрессированный формат
        public_key_hex = public_key_bytes.hex()

        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

        network_payload = b'\x00' + ripemd160_hash  # префикс для основной сети
        checksum = hashlib.sha256(hashlib.sha256(network_payload).digest()).digest()[:4]
        full_payload = network_payload + checksum
        address = base58.b58encode(full_payload).decode()

        return private_key_hex, public_key_hex, address
    
    def create_new_wallet_tron(self, wallet_name: str):
        """Create a new Tron wallet"""
        if not self.is_authenticated:
            return False, "Authentication required", None
        if not wallet_name or len(wallet_name) == 0:
            return False, "Name cannot be empty", None

        private_key, address = self.generate_tron_address()
        
        wallet_data = {
            "name": wallet_name,
            "address": address,
            "private_key": private_key,
            "created_at": datetime.now().isoformat(),
            "type": "generated",
            "currency": "tron",
            "network": "mainnet"
        }
        if self.save_wallet(dir=self.tron_wallets_dir, wallet_data=wallet_data):
            return True, f"Wallet '{wallet_name}' of Tron created successfully!", {"address": address, "private_key": private_key}
        else:
            return False, "Error saving wallet", None
    def create_new_wallet_btc(self, wallet_name: str):
        """Create a new Bitcoin wallet"""
        if not self.is_authenticated:
            return False, "Authentication required", None
        if not wallet_name or len(wallet_name) == 0:
            return False, "Name cannot be empty", None
        private_key, pub_key, address = self.generate_btc_address()
        wallet_data = {
            "name": wallet_name,
            "address": address,
            "private_key": private_key,
            "created_at": datetime.now().isoformat(),
            "type": "generated",
            "public_key": pub_key,
            "currency": "btc",
            "network": "mainnet"
        }
        if self.save_wallet(dir=self.btc_wallets_dir, wallet_data=wallet_data):
            return True, f"Bitcoin wallet '{wallet_name}' created successfully!", {"address": address, "private_key": private_key}
        else:
            return False, "Error saving wallet", None
    def create_new_wallet_eth(self, wallet_name: str):
        """Create a new Ethereum wallet"""
        if not self.is_authenticated:
            return False, "Authentication required", None
        if not wallet_name or len(wallet_name) == 0:
            return False, "Name cannot be empty", None

        private_key, address = self.generate_eth_address()
        
        wallet_data = {
            "name": wallet_name,
            "address": address,
            "private_key": private_key,
            "created_at": datetime.now().isoformat(),
            "type": "generated",
            "currency": "eth",
            "network": "mainnet"
        }

        if self.save_wallet(dir=self.eth_wallets_dir, wallet_data=wallet_data):
            return True, f"Wallet '{wallet_name}' of Ethereum created successfully!", {"address": address, "private_key": private_key}
        else:
            return False, "Error saving wallet", None

    def import_private_key(self,  wallet_name: str):
        """Import wallet from private key"""
        if not self.is_authenticated:
            return False, "Authentication required"
        if not self.validate_private_key(private_key):
            return False, "Invalid private key format"
        if not wallet_name or len(wallet_name) == 0:
            return False, "Name cannot be empty"

        private_key, address = self.generate_eth_address()
        
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

        private_key, address = self.generate_eth_address()
        
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
        
    def derive_private_key_from_mnemonic(self, mnemonic):
        """Simplified private key derivation from mnemonic"""
        mnemonic_hash = hashlib.sha256(mnemonic.encode()).hexdigest()
        return mnemonic_hash

    def save_wallet(self, dir, wallet_data):
        """Save a wallet in encrypted form"""
        try:
            safe_name = re.sub(r'[^\w\-_\.]', '_', wallet_data['name'])
            filename = f"{safe_name}_{wallet_data['address'][:8]}.json"
            filepath = dir / filename
            
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
            
            return wallet_data
        except Exception as e:
            # For a GUI, it's better to log or return an error than to print
            raise IOError(f"Error reading wallet {wallet_file.name}") from e

    def create_wallet_backup(self, wallet_name):
        """Create a backup of a wallet"""
        if not self.is_authenticated:
            return False, "Authentication required"
        try:
            wallet_files = list(self.eth_wallets_dir.glob(f"{wallet_name}*.json"))
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
            self.eth_dir,
            self.btc_dir,
            self.tron_dir,
            self.eth_wallets_dir,
            self.btc_wallets_dir,
            self.tron_wallets_dir,
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
    def decrypt_wallet_file(self, hood, file_path: str):
        """
        Дешифрует и показывает содержимое wallet файла
        
        Использование:
        python sapphire_hood.py --decrypt "path/to/wallet.json"
        """
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = hood.encryption_key.decrypt(encrypted_data)
            wallet_data = json.loads(decrypted_data.decode())            
            print(json.dumps(wallet_data, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")

    def validated_btc_address(self, address: str) -> bool:
        """Validate a Bitcoin address"""
        if not isinstance(address, str):
            return False
        if re.match(r'^(1|3|bc1)[a-zA-Z0-9]{25,39}$', address):
            return True
        return False
    def validated_tron_address(self, address: str) -> bool:
        """Validate a Tron address"""
        if not isinstance(address, str):
            return False
        if re.match(r'^(T)[a-zA-Z0-9]{33}$', address):
            return True
        return False
    def information_for_qr(self, amount: float = None, currency: str = "eth", address: str = None) -> str:
        """Generate URI for QR code payment"""
        if address is None: 
            raise ValueError("Address cannot be None")
        if currency == "eth":
            uri = f"ethereum:{address}"
        elif currency == "btc":
            uri = f"bitcoin:{address}"
        elif currency == "tron":
            uri = f"tron:{address}"
        else:
            uri = f"{currency}:{address}"
        
        if amount is not None:
            uri += f"?amount={amount}"
        return uri
    
    def generate_payment_qrcode(self, wallet: str = None, currency: str = "eth", amount: float = None, logo_path: str = None) -> BytesIO:
        """Generate QR code for payment"""
        if not QR_AVAILABLE:
            raise ImportError("QR code libraries not available. Install with: pip install qrcode[pil] pillow")
        
        uri = self.information_for_qr(amount=amount, currency=currency, address=wallet)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High correction for logo
            box_size=10, 
            border=4
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # Create QR code
        img = qr.make_image(
            image_factory=StyledPilImage, 
            module_drawer=VerticalBarsDrawer(horizontal_shrink=0.8)
        )
        
        # Инвертируем цвета изображения (черное становится белым и наоборот)
        from PIL import ImageOps
        img = ImageOps.invert(img.convert('RGB'))
        
        # Add logo if file exists
        if logo_path and os.path.exists(logo_path):
            try:
                # Open logo
                logo = Image.open(logo_path)
                
                # Get QR code dimensions
                qr_width, qr_height = img.size
                
                # Calculate logo size (20% of QR code size)
                logo_size = min(qr_width, qr_height) // 3  # 33% of size

                # Resize logo maintaining proportions
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # White background for better QR code readability (after inversion)
                if logo.mode != 'RGBA':
                    # Create WHITE square slightly larger than logo
                    background_size = logo_size + 10
                    background = Image.new('RGB', (background_size, background_size), 'white')  # White background
                    
                    # Place logo in center of white background
                    logo_bg_pos = ((background_size - logo_size) // 2, (background_size - logo_size) // 2)
                    background.paste(logo, logo_bg_pos)
                    logo = background
                    logo_size = background_size
                
                # Calculate position to place logo exactly in center
                logo_x = (qr_width - logo_size) // 2
                logo_y = (qr_height - logo_size) // 2
                
                # Insert logo in center of QR code
                if logo.mode == 'RGBA':
                    img.paste(logo, (logo_x, logo_y), logo)  # With alpha channel
                else:
                    img.paste(logo, (logo_x, logo_y))  # Without alpha channel
                    
            except Exception as e:
                print(f"Error adding logo: {e}")
                # Continue without logo
        
        # Save image to BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
    def delete_wallet(self, dir, wallet_name):
        """Delete a wallet by name"""
        if not self.is_authenticated:
            raise PermissionError("Authentication required")
        
        # Find wallet file by name
        wallet_files = list(dir.glob(f"*{wallet_name}*.json"))
        if not wallet_files:
            raise FileNotFoundError(f"Wallet '{wallet_name}' not found")
        
        # Delete the wallet file
        wallet_file = wallet_files[0]
        try:
            wallet_file.unlink()
            return True
        except Exception as e:
            raise IOError(f"Failed to delete wallet file: {e}")