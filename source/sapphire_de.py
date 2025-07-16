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
    """Класс для расшифровки backup файлов"""
    
    def __init__(self):
        self.user_home = Path.home()
        self.app_data_dir = self.user_home / ".sapphire0.1.0"
        self.password_hash_file = self.app_data_dir / ".password_hash"
        self.backups_dir = self.app_data_dir / "ethereum_keys" / "backups"
        self.encryption_key = None
    
    def authenticate_and_get_key(self):
        """Аутентификация и получение ключа расшифровки"""
        if not self.password_hash_file.exists():
            print("❌ Файл с паролем не найден")
            return False
        
        print("🔐 Введите пароль для расшифровки:")
        
        for attempt in range(3):
            password = getpass.getpass(f"Пароль (попытка {attempt + 1}/3): ")
            
            if self.verify_password(password):
                self.encryption_key = self.derive_key(password)
                print("✅ Пароль верный!")
                return True
            else:
                print(f"❌ Неверный пароль. Осталось попыток: {2 - attempt}")
        
        return False
    
    def verify_password(self, password):
        """Проверка пароля"""
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
            print(f"❌ Ошибка проверки пароля: {e}")
            return False
    
    def derive_key(self, password):
        """Создание ключа шифрования из пароля"""
        try:
            with open(self.password_hash_file, 'r') as f:
                hash_data = json.load(f)
            salt = base64.b64decode(hash_data["salt"])
        except:
            print("❌ Не удалось получить соль")
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
        """Расшифровка backup файла"""
        if not self.encryption_key:
            print("❌ Ключ шифрования не получен")
            return None
        
        try:
            # Читаем зашифрованные данные
            with open(backup_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Расшифровываем
            decrypted_data = self.encryption_key.decrypt(encrypted_data)
            
            # Парсим JSON
            wallet_data = json.loads(decrypted_data.decode())
            
            return wallet_data
            
        except Exception as e:
            print(f"❌ Ошибка расшифровки: {e}")
            return None
    
    def decrypt_from_text(self, encrypted_text):
        """Расшифровка из текстовой строки"""
        if not self.encryption_key:
            print("❌ Ключ шифрования не получен")
            return None
        
        try:
            # Убираем лишние символы и переводы строк
            encrypted_text = encrypted_text.strip()
            
            # Конвертируем в байты
            encrypted_data = encrypted_text.encode()
            
            # Расшифровываем
            decrypted_data = self.encryption_key.decrypt(encrypted_data)
            
            # Парсим JSON
            wallet_data = json.loads(decrypted_data.decode())
            
            return wallet_data
            
        except Exception as e:
            print(f"❌ Ошибка расшифровки: {e}")
            return None
    
    def list_backup_files(self):
        """Список backup файлов"""
        if not self.backups_dir.exists():
            print("❌ Папка backup не найдена")
            return []
        
        backup_files = list(self.backups_dir.glob("*.backup"))
        
        if not backup_files:
            print("📁 Backup файлы не найдены")
            return []
        
        print(f"\n📦 Найдено backup файлов: {len(backup_files)}")
        for i, backup_file in enumerate(backup_files, 1):
            print(f"{i}. {backup_file.name}")
        
        return backup_files
    
    def display_wallet_info(self, wallet_data):
        """Отображение информации о кошельке"""
        if not wallet_data:
            return
        
        print("\n" + "="*60)
        print("💼 ИНФОРМАЦИЯ О КОШЕЛЬКЕ")
        print("="*60)
        
        print(f"📛 Имя: {wallet_data.get('name', 'Неизвестно')}")
        print(f"📍 Адрес: {wallet_data.get('address', 'Неизвестно')}")
        print(f"🔑 Приватный ключ: {wallet_data.get('private_key', 'Не найден')}")
        print(f"📅 Создан: {wallet_data.get('created_at', 'Неизвестно')}")
        print(f"🏷️ Тип: {wallet_data.get('type', 'Неизвестно')}")
        print(f"🌐 Сеть: {wallet_data.get('network', 'Неизвестно')}")
        
        if 'mnemonic' in wallet_data:
            print(f"🔤 Мнемоника: {wallet_data['mnemonic']}")
        
        print("="*60)

def main():
    """Основная функция"""
    print("🔓 Расшифровщик Sapphire Backup")
    print("="*40)
    
    decryptor = BackupDecryptor()
    
    # Аутентификация
    if not decryptor.authenticate_and_get_key():
        print("❌ Не удалось аутентифицироваться")
        return
    
    print("\nВыберите способ расшифровки:")
    print("1. 📁 Расшифровать файл из папки backup")
    print("2. 📝 Расшифровать текст из буфера обмена")
    print("3. ✏️ Ввести зашифрованный текст вручную")
    
    choice = input("\nВведите номер (1-3): ").strip()
    
    if choice == "1":
        # Расшифровка файла
        backup_files = decryptor.list_backup_files()
        if not backup_files:
            return
        
        try:
            file_num = int(input("\nВведите номер файла: ")) - 1
            if 0 <= file_num < len(backup_files):
                backup_file = backup_files[file_num]
                print(f"\n🔓 Расшифровка файла: {backup_file.name}")
                
                wallet_data = decryptor.decrypt_backup_file(backup_file)
                decryptor.display_wallet_info(wallet_data)
            else:
                print("❌ Неверный номер файла")
        except ValueError:
            print("❌ Введите корректный номер")
    
    elif choice == "2":
        # Расшифровка из буфера обмена (если доступно)
        try:
            import pyperclip
            encrypted_text = pyperclip.paste()
            print("📋 Получен текст из буфера обмена")
            
            wallet_data = decryptor.decrypt_from_text(encrypted_text)
            decryptor.display_wallet_info(wallet_data)
            
        except ImportError:
            print("❌ Модуль pyperclip не установлен")
            print("Установите: pip install pyperclip")
    
    elif choice == "3":
        # Ручной ввод
        print("\n📝 Введите зашифрованный текст:")
        encrypted_text = input().strip()
        
        # Ваш зашифрованный текст
        if not encrypted_text:
            encrypted_text = "gAAAAABoZyo0SCMTvc-K1WsV2qcHG64ZulxnKt8Dp_gbwuD3b-c23xd0nWvh_Gy530SV0uEyAsY5MpVyM5LUtJwXfIhzMrqeIKD_4tm8xJhtnA_lVLAD8BfG1GxxDM_8SSRHiETJwride0VsZhJikHy94mT4HZ0z5eHpdiPAiohFcadzXzUmD_hpdqtEo80Jhc1s1SkPkSdFpD6XDzHLWxsYjK8Od2k5uoCwDI1LTMNm_Sc9B9A6wtUeBWYb6zyNnZ0UlSufMVYnqKx8Lk14213gKtHGhYImjl8o5WOIR-b4F7tt3MaQG3hDRzZ__JzLX_-Al2gH0qRhq37czji1K5QziH2kyNENKrP9XtgobfZe5NNwJnZpIyjOypMH9kNZXchwnZRL6KQWpvJXQLTvT32jCu-wAHdut1SJPqeGu0yqAVwDBok48Rs="
            print("📋 Используется предоставленный зашифрованный текст")
        
        wallet_data = decryptor.decrypt_from_text(encrypted_text)
        decryptor.display_wallet_info(wallet_data)
    
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Расшифровка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")