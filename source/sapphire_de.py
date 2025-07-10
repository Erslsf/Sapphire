import json
import os
import sys
import getpass
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class BackupDecryptor:
    """Class for decrypting backup files"""
    
    def __init__(self):
        self.user_home = Path.home()
        self.app_data_dir = self.user_home / ".sapphire0.1.0"
        self.password_hash_file = self.app_data_dir / ".password_hash"
        self.backups_dir = self.app_data_dir / "ethereum_keys" / "backups"
        self.encryption_key = None
    
    def authenticate_and_get_key(self):
        """Authentication and obtaining decryption key"""
        if not self.password_hash_file.exists():
            print("❌ Password file not found")
            return False
        
        print("🔐 Enter password for decryption:")
        
        for attempt in range(3):
            password = getpass.getpass(f"Password (attempt {attempt + 1}/3): ")
            
            if self.verify_password(password):
                self.encryption_key = self.derive_key(password)
                print("✅ Password correct!")
                return True
            else:
                print(f"❌ Wrong password. Attempts remaining: {2 - attempt}")
        
        return False
    
    def verify_password(self, password):
        """Password verification"""
        try:
            with open(self.password_hash_file, 'r') as f:
                hash_data = json.load(f)
            
            salt = base64.b64decode(hash_data["salt"])
            stored_hash = base64.b64decode(hash_data["hash"])
            iterations = hash_data.get("iterations", 100000)
            
            password_hash = hashlib.pbkdf2_hmac('sha256',
                                              password.encode('utf-8'),
                                              salt,
                                              iterations)
            
            return password_hash == stored_hash
            
        except Exception as e:
            print(f"❌ Password verification error: {e}")
            return False
    
    def derive_key(self, password):
        """Creating encryption key from password"""
        try:
            with open(self.password_hash_file, 'r') as f:
                hash_data = json.load(f)
            salt = base64.b64decode(hash_data["salt"])
        except:
            print("❌ Failed to get salt")
            return None
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def decrypt_backup_file(self, backup_file_path):
        """Decrypting backup file"""
        if not self.encryption_key:
            print("❌ Encryption key not obtained")
            return None
        
        try:
            # Read encrypted data
            with open(backup_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.encryption_key.decrypt(encrypted_data)
            
            # Parse JSON
            wallet_data = json.loads(decrypted_data.decode())
            
            return wallet_data
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return None
    
    def decrypt_from_text(self, encrypted_text):
        """Decryption from text string"""
        if not self.encryption_key:
            print("❌ Encryption key not obtained")
            return None
        
        try:
            # Remove extra characters and line breaks
            encrypted_text = encrypted_text.strip()
            
            # Convert to bytes
            encrypted_data = encrypted_text.encode()
            
            # Decrypt
            decrypted_data = self.encryption_key.decrypt(encrypted_data)
            
            # Parse JSON
            wallet_data = json.loads(decrypted_data.decode())
            
            return wallet_data
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return None
    
    def list_backup_files(self):
        """List of backup files"""
        if not self.backups_dir.exists():
            print("❌ Backup folder not found")
            return []
        
        backup_files = list(self.backups_dir.glob("*.backup"))
        
        if not backup_files:
            print("📁 Backup files not found")
            return []
        
        print(f"\n📦 Found backup files: {len(backup_files)}")
        for i, backup_file in enumerate(backup_files, 1):
            print(f"{i}. {backup_file.name}")
        
        return backup_files
    
    def display_wallet_info(self, wallet_data):
        """Display wallet information"""
        if not wallet_data:
            return
        
        print("\n" + "="*60)
        print("💼 WALLET INFORMATION")
        print("="*60)
        
        print(f"📛 Name: {wallet_data.get('name', 'Unknown')}")
        print(f"📍 Address: {wallet_data.get('address', 'Unknown')}")
        print(f"🔑 Private key: {wallet_data.get('private_key', 'Not found')}")
        print(f"📅 Created: {wallet_data.get('created_at', 'Unknown')}")
        print(f"🏷️ Type: {wallet_data.get('type', 'Unknown')}")
        print(f"🌐 Network: {wallet_data.get('network', 'Unknown')}")
        
        if 'mnemonic' in wallet_data:
            print(f"🔤 Mnemonic: {wallet_data['mnemonic']}")
        
        print("="*60)

def main():
    """Main function"""
    print("🔓 Sapphire Backup Decryptor")
    print("="*40)
    
    decryptor = BackupDecryptor()
    
    # Authentication
    if not decryptor.authenticate_and_get_key():
        print("❌ Failed to authenticate")
        return
    
    print("\nChoose decryption method:")
    print("1. 📁 Decrypt file from backup folder")
    print("2. 📝 Decrypt text from clipboard")
    print("3. ✏️ Enter encrypted text manually")
    
    choice = input("\nEnter number (1-3): ").strip()
    
    if choice == "1":
        # File decryption
        backup_files = decryptor.list_backup_files()
        if not backup_files:
            return
        
        try:
            file_num = int(input("\nEnter file number: ")) - 1
            if 0 <= file_num < len(backup_files):
                backup_file = backup_files[file_num]
                print(f"\n🔓 Decrypting file: {backup_file.name}")
                
                wallet_data = decryptor.decrypt_backup_file(backup_file)
                decryptor.display_wallet_info(wallet_data)
            else:
                print("❌ Invalid file number")
        except ValueError:
            print("❌ Enter a valid number")
    
    elif choice == "2":
        # Decryption from clipboard (if available)
        try:
            import pyperclip
            encrypted_text = pyperclip.paste()
            print("📋 Got text from clipboard")
            
            wallet_data = decryptor.decrypt_from_text(encrypted_text)
            decryptor.display_wallet_info(wallet_data)
            
        except ImportError:
            print("❌ pyperclip module not installed")
            print("Install: pip install pyperclip")
    
    elif choice == "3":
        # Manual input
        print("\n📝 Enter encrypted text:")
        encrypted_text = input().strip()
        
        # Your encrypted text
        if not encrypted_text:
            encrypted_text = "gAAAAABoZyo0SCMTvc-K1WsV2qcHG64ZulxnKt8Dp_gbwuD3b-c23xd0nWvh_Gy530SV0uEyAsY5MpVyM5LUtJwXfIhzMrqeIKD_4tm8xJhtnA_lVLAD8BfG1GxxDM_8SSRHiETJwride0VsZhJikHy94mT4HZ0z5eHpdiPAiohFcadzXzUmD_hpdqtEo80Jhc1s1SkPkSdFpD6XDzHLWxsYjK8Od2k5uoCwDI1LTMNm_Sc9B9A6wtUeBWYb6zyNnZ0UlSufMVYnqKx8Lk14213gKtHGhYImjl8o5WOIR-b4F7tt3MaQG3hDRzZ__JzLX_-Al2gH0qRhq37czji1K5QziH2kyNENKrP9XtgobfZe5NNwJnZpIyjOypMH9kNZXchwnZRL6KQWpvJXQLTvT32jCu-wAHdut1SJPqeGu0yqAVwDBok48Rs="
            print("📋 Using provided encrypted text")
        
        wallet_data = decryptor.decrypt_from_text(encrypted_text)
        decryptor.display_wallet_info(wallet_data)
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Decryption interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")