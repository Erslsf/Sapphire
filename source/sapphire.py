"""" 
version = 1.4.a2
This file is part of the Sapphire project, a decentralized finance (DeFi) application.
It is distributed under the GNU General Public License v3.0 (GPL-3.0).
Main architecturer: B.E.S 
Designed in Astana, Kazakhstan.
This file contains the main GUI for the Sapphire application, including login and wallet management.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QSizePolicy,
    QStackedWidget, QFormLayout, QInputDialog, QListWidgetItem, QDialog,
    QDialogButtonBox, QTextEdit, QComboBox, QScrollArea
)
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QPainterPath, QClipboard
from PyQt6.QtCore import Qt, QSize, QTimer

# Определяем базовый путь для ресурсов
def get_base_path():
    """Возвращает базовый путь для ресурсов приложения."""
    if hasattr(sys, '_MEIPASS'):
        # Если приложение запущено как PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Обычный запуск Python скрипта
        return Path(__file__).parent.parent

# Получаем базовый путь
BASE_PATH = get_base_path()

# Добавляем путь к source в sys.path, если его там нет
source_path = str(BASE_PATH / "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

# Импортируем sapphire_hood
try:
    from sapphire_hood import SapphireHood
except ImportError as e:
    print(f"Ошибка импорта sapphire_hood: {e}")
    print(f"Текущий рабочий каталог: {os.getcwd()}")
    print(f"Базовый путь: {BASE_PATH}")
    print(f"Путь к source: {source_path}")
    sys.exit(1)

# Определяем пути к ресурсам
ASSETS_PATH = BASE_PATH / "assets"
APP_ICON_PATH = str(ASSETS_PATH / "icons" / "shg.png")

class LoginWindow(QWidget):
    """Window for login or initial setup."""
    def __init__(self, hood: SapphireHood, main_window):
        super().__init__()
        self.hood = hood
        self.main_window = main_window
        self.is_first_launch = self.hood.is_first_launch()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sapphire')
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.setFixedSize(400, 380)

        # --- Styles --- #
        self.setStyleSheet("""
            QWidget {
                background-color: #000000; /* Dark background */
                color: #FFFFFF;           /* Light text */
            }
            QLabel#TitleLabel {
                font-size: 16pt;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #000000;
                border: 2px solid #555; /* Changed border to solid */
                border-radius: 6px;
                padding: 10px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px dashed #ffffff;
            }
            QPushButton {
                background-color: #1f1f1f;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 5px;
                border: none;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: blueviolet;
            }
            QPushButton:pressed {
                background-color: blueviolet;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Logo
        logo_label = QLabel(self)
        logo_path = str(ASSETS_PATH / "icons" / "logo_sap.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("SAPPHIRE")
            logo_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel") # Set object name for styling
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.submit_button = QPushButton()
        self.submit_button.setFixedHeight(40)

        if self.is_first_launch:
            self.title_label.setText("Welcome!")
            self.submit_button.setText("Create Vault")
            self.submit_button.clicked.connect(self.setup)
        else:
            self.title_label.setText("Welcome Back!")
            self.confirm_password_input.hide()
            self.submit_button.setText("Enter")
            self.submit_button.clicked.connect(self.login)

        layout.addWidget(logo_label)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.password_input.returnPressed.connect(self.submit_button.click)
        self.confirm_password_input.returnPressed.connect(self.submit_button.click)

    def login(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return

        success, message = self.hood.initialize(password)
        if success:
            self.main_window.post_login_setup()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Login Error", message)
            self.password_input.clear()

    def setup(self):
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        success, message = self.hood.setup_new_installation(password, confirm_password)
        if success:
            QMessageBox.information(self, "Success", "Vault created! Now log in using your password.")
            # Update the window for login
            self.is_first_launch = False
            self.title_label.setText("Sapphire Login")
            self.confirm_password_input.hide()
            self.submit_button.setText("Login")
            self.submit_button.clicked.disconnect()
            self.submit_button.clicked.connect(self.login)
            self.password_input.clear()
            self.confirm_password_input.clear()
        else:
            QMessageBox.critical(self, "Setup Error", message)

class MainWindow(QWidget):
    """Main application window."""
    def __init__(self, hood: SapphireHood):
        super().__init__()
        self.hood = hood
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sapphire')
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.setGeometry(100, 100, 950, 700)
        
        # Установка стиля окна для кастомной рамки
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #000000;
                color: #F0F0F0;
            }
            QWidget {
                background-color: #000000;
                color: #F0F0F0;
            }
            /* Список кошельков - современный дизайн */
            QListWidget {
                border-radius: 12px;
                outline: none;
                font-size: 10pt;
            }
            QListWidget::item {
                border-radius: 8px;
                border: 2px solid;
                border-color: #ffffff; /* Белая рамка */
                padding: 12px 16px;
                margin: 3px 0px;
                color: #ffffff;
                font-weight: 500;
                font-size: 16pt; /* Увеличенный размер шрифта для названий кошельков */
            }
            QListWidget::item:selected {
                border: 2px solid #ffffff; /* White border on selection */
                color: white;
                font-weight: bold;
            }
            QListWidget::item:hover {
                border: 2px dashed #ffffff;
            }
            QListWidget::item:selected:hover {
                border: 2px dashed #ffffff;
            }
            /* Убираем скроллбар полностью - только прокрутка колесиком */
            QListWidget::scrollbar:vertical {
                width: 0px;
            }
            QListWidget::scrollbar:horizontal {
                height: 0px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            /* Delete Wallet Button - Custom styling */
            QPushButton#deleteWalletButton {
                background-color: none;
                color: white;
                font-weight: bold;
                border-radius: 15px;
                padding: 5px 10px;
                border: 2px dashed #e61919;
                font-size: 9pt;
                max-width: 80px;
                min-width: 80px;
            }
            QPushButton#deleteWalletButton:hover {
                background-color: #c82333;
                border: 2px solid #c82333;
            }
            QPushButton#deleteWalletButton:pressed {
                background-color: #bd2130;
                border: 2px solid #bd2130;
            }
            /* Add Wallet Button - Custom styling */
            QPushButton#addWalletButton {
                background: none;
                color: white;
                font-weight: bold;
                border : 2px dashed #ffffff ;
                border-radius: 8px;
                padding: 8px 16px;
                text-align: left;
                font-size: 10pt;
            }
            QPushButton#addWalletButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #333333, stop: 1 #555555);
                border: 2px solid #ffffff;
            }
            QPushButton#addWalletButton:pressed {
                           border : 2px dashed #ffffff ;
            }
            QPushButton#roundButton {
                background-color: #0078d7;
                border-radius: 6px;
                width: 40px;
                height: 40px;
                padding: 0px;
            }
            QPushButton#roundButton:hover {
                background-color: #005a9e;
            }
            QPushButton#roundButton:pressed {
                background-color: #004578;
            }
            /* Home Button - Blue gradient */
            QPushButton#homeButton {
                background: rgba(56, 142, 60, 0);
                border-radius: 6px;
                width: 40px;
                height: 40px;
                padding: 0px;
            }
            QPushButton#homeButton:hover {
                           background: #1f1f1f; /* Darker background on hover */
            }
            QPushButton#homeButton:pressed {
                           background: #1f1f1f;}
            /* IDFTs Button - Green gradient */
            QPushButton#idftsButton {
                background: rgba(255, 255, 255, 255);
                border-radius: 6px;
                width: 40px;
                height: 40px;
                padding: 0px;
            }
            QPushButton#idftsButton:hover {
                           background: #1f1f1f; /* Darker background on hover */
            }
            QPushButton#idftsButton:pressed {
                           background: #1f1f1f;
            }
            /* Exit Button - Red gradient */
            QPushButton#exitButton {
                background: rgba(255, 255, 255, 0);
                border-radius: 6px;
                width: 40px;
                height: 40px;
                padding: 0px;
            }
            QPushButton#exitButton:hover {
                background: #1f1f1f;                
            }
            QPushButton#exitButton:pressed {
                background: #1f1f1f;
            }
            QWidget#buttonContainer {
                background-color: #1a1a1a;
                border-radius: 15px;
            }
            QLabel {
                font-size: 10pt;
            }
            QFormLayout > QLabel {
                font-weight: bold;
            }
        """)

        # Main vertical layout
        main_layout = QVBoxLayout(self)

        # Top panel with wallets and details
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)

        # Left panel (wallet list)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(250)

        self.wallet_list_widget = QListWidget()
        self.wallet_list_widget.itemClicked.connect(self.show_wallet_details)
        # Полностью отключаем скроллбары программно
        self.wallet_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.wallet_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Установим размер иконок в списке
        self.wallet_list_widget.setIconSize(QSize(24, 24))
        # Set size policy to allow vertical growth and set a max height
        self.wallet_list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.wallet_list_widget.setMaximumHeight(600) # Adjust this value as needed

        left_layout.addWidget(self.wallet_list_widget)

        # Add wallet button under the list
        self.add_wallet_btn = QPushButton()
        self.add_wallet_btn.setObjectName("addWalletButton")
        wallet_icon_path = str(ASSETS_PATH / "icons" / "wallet_24dp_000000_E8EAED_FILL0_wght400_GRAD0_opsz24.svg")
        if os.path.exists(wallet_icon_path):
            self.add_wallet_btn.setIcon(QIcon(wallet_icon_path))
            self.add_wallet_btn.setIconSize(QSize(20, 20))
        self.add_wallet_btn.setText("+Add Wallet")
        self.add_wallet_btn.setFixedHeight(40)
        left_layout.addWidget(self.add_wallet_btn)
        left_layout.addStretch()

        # Right panel (details)
        self.right_panel = QStackedWidget()

        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label = QLabel("Select a wallet to view its information")
        welcome_label.setFont(QFont("Arial", 14))
        welcome_layout.addWidget(welcome_label)

        self.wallet_details_widget = QWidget()
        details_main_layout = QVBoxLayout(self.wallet_details_widget)
        
        # Wallet name at the top
        wallet_name_widget = QWidget()
        wallet_name_layout = QHBoxLayout(wallet_name_widget)
        wallet_name_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.wallet_name_display = QLabel()
        self.wallet_name_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wallet_name_display.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        wallet_name_layout.addWidget(self.wallet_name_display)
        
        # QR code below name
        qr_widget = QWidget()
        qr_layout = QHBoxLayout(qr_widget)
        qr_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.qr_code_label = QLabel()
        self.qr_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_code_label.setFixedSize(250, 250)
        self.qr_code_label.setStyleSheet("""
            QLabel {
                border-radius: 50px;
            }
        """)
        self.qr_code_label.setText("No QR Code")
        
        qr_layout.addWidget(self.qr_code_label)
        
        # Address below QR code
        address_widget = QWidget()
        address_layout = QHBoxLayout(address_widget)
        address_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        address_layout.setContentsMargins(0, 10, 0, 0)  # Небольшой отступ от QR кода
        
        self.wallet_address_display = QLabel()
        self.wallet_address_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wallet_address_display.setWordWrap(True)
        self.wallet_address_display.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #cccccc;
                max-width: 400px;
            }
        """)
        
        self.copy_address_btn = QPushButton("Copy")
        self.copy_address_btn.setFixedSize(65, 30)
        self.copy_address_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                font-weight: bold;
                border-radius: 12px;
                padding: 3px;
                border: 1px solid #555555;
                font-size: 8pt;
            }
        """)
        self.copy_address_btn.clicked.connect(self.copy_address_to_clipboard)
        
        address_layout.addWidget(self.wallet_address_display)
        address_layout.addWidget(self.copy_address_btn)
        
        # Bottom - wallet information (without address, as it's now under QR)
        info_widget = QWidget()
        self.wallet_details_layout = QFormLayout(info_widget)

        # Add delete button to wallet details - smaller and to the right
        delete_container = QWidget()
        delete_layout = QHBoxLayout(delete_container)
        delete_layout.setContentsMargins(0, 10, 0, 0)
        delete_layout.addStretch()  # Push button to the right
        
        self.delete_wallet_btn = QPushButton("Delete")
        self.delete_wallet_btn.setObjectName("deleteWalletButton")
        self.delete_wallet_btn.setFixedSize(80, 30)
        
        delete_layout.addWidget(self.delete_wallet_btn)
        self.wallet_details_layout.addRow("", delete_container)
        
        # Add wallet name at top, then QR code, then address, then wallet info below
        details_main_layout.addWidget(wallet_name_widget)
        details_main_layout.addWidget(qr_widget)
        details_main_layout.addWidget(address_widget)
        details_main_layout.addWidget(info_widget)
        details_main_layout.addStretch()  # Push content to top

        self.right_panel.addWidget(self.welcome_widget)
        self.right_panel.addWidget(self.wallet_details_widget)

        top_layout.addWidget(left_panel)
        top_layout.addWidget(self.right_panel)

        # Bottom control panel ("island")
        control_panel = QWidget()
        control_panel.setFixedHeight(120)
        control_layout = QVBoxLayout(control_panel)  # Изменили на QVBoxLayout
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # Добавляем stretch сверху для центрирования по вертикали
        control_layout.addStretch()

        # Row 2
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(0, 0, 0, 0)

        # Create a container widget for buttons with max width
        buttons_container = QWidget()
        buttons_container.setObjectName("buttonContainer")
        buttons_container.setMaximumWidth(600)
        buttons_container.setFixedHeight(60)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(15, 10, 15, 10)
        buttons_layout.setSpacing(60)

        self.home_btn = QPushButton()
        self.home_btn.setObjectName("homeButton")
        home_icon_path = str(ASSETS_PATH / "icons" / "home_24dp_E8EAED_FILL0_wght400_GRAD0_opsz24.svg")
        if os.path.exists(home_icon_path):
            self.home_btn.setIcon(QIcon(home_icon_path))
            self.home_btn.setIconSize(QSize(24, 24))
        self.home_btn.setFixedSize(40, 40)
        self.home_btn.setToolTip("Home")
        
        self.show_idfts_btn = QPushButton()
        self.show_idfts_btn.setObjectName("idftsButton")
        token_icon_path = str(ASSETS_PATH / "icons" / "token_24dp_000000_FILL0_wght400_GRAD0_opsz24.svg")
        if os.path.exists(token_icon_path):
            self.show_idfts_btn.setIcon(QIcon(token_icon_path))
            self.show_idfts_btn.setIconSize(QSize(24, 24))
        self.show_idfts_btn.setFixedSize(40, 40)
        self.show_idfts_btn.setToolTip("All IDFTs")
        
        self.exit_btn = QPushButton()
        self.exit_btn.setObjectName("exitButton")
        exit_icon_path = str(ASSETS_PATH / "icons" / "logout_24dp_E8EAED_FILL0_wght400_GRAD0_opsz24.svg")
        if os.path.exists(exit_icon_path):
            self.exit_btn.setIcon(QIcon(exit_icon_path))
            self.exit_btn.setIconSize(QSize(24, 24))
        self.exit_btn.setFixedSize(40, 40)
        self.exit_btn.setToolTip("Exit")

        buttons_layout.addWidget(self.home_btn)
        buttons_layout.addWidget(self.show_idfts_btn)
        buttons_layout.addWidget(self.exit_btn)

        row2_layout.addStretch()
        row2_layout.addWidget(buttons_container)
        row2_layout.addStretch()
        
        # Добавляем row2_layout в основной layout
        control_layout.addLayout(row2_layout)
        
        # Добавляем stretch снизу для центрирования по вертикали
        control_layout.addStretch()

        # Connect signals to slots
        self.add_wallet_btn.clicked.connect(self.add_wallet_dialog)
        self.delete_wallet_btn.clicked.connect(self.delete_wallet) # Connect to delete_wallet method
        self.home_btn.clicked.connect(self.show_not_implemented_message)
        self.show_idfts_btn.clicked.connect(self.show_not_implemented_message)
        self.exit_btn.clicked.connect(self.close)

        # Add everything to the main layout
        main_layout.addWidget(top_panel)
        main_layout.addWidget(control_panel)

    def post_login_setup(self):
        """Executes after a successful login."""
        self.update_wallet_list()

    def update_wallet_list(self):
        self.wallet_list_widget.clear()
        try:
            wallets = self.hood.list_wallets()
            if not wallets:
                no_wallets_item = QListWidgetItem("No wallets found.")
                no_wallets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Выравнивание текста по правому краю
                self.wallet_list_widget.addItem(no_wallets_item)
            else:
                eth_icon_path = str(ASSETS_PATH / "icons" / "cdnlogo.com_ethereum-eth.svg")
                eth_icon = QIcon(eth_icon_path) if os.path.exists(eth_icon_path) else QIcon()
                for wallet in wallets:
                    wallet_name = wallet['name']
                    if len(wallet_name) > 12:  # Если название больше 12 символов
                        wallet_name = wallet_name[:12] + "..."
                    list_item = QListWidgetItem(None)
                    list_item.setText(wallet_name)
                    list_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)  # Выравнивание текста по левому краю
                    list_item.setIcon(eth_icon)
                    list_item.setData(Qt.ItemDataRole.UserRole, wallet) # Store all data
                    self.wallet_list_widget.addItem(list_item)

            # Adjust height based on content
            self.adjust_wallet_list_height()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load wallets: {e}")

    def adjust_wallet_list_height(self):
        """Adjusts the QListWidget height based on the number of items."""
        count = self.wallet_list_widget.count()
        if count == 0:
            # Set a default minimum height if empty
            self.wallet_list_widget.setMinimumHeight(100)
            self.wallet_list_widget.setMaximumHeight(100)
        else:
            # Calculate preferred height
            # This is an approximation: item height might vary
            item_height = self.wallet_list_widget.sizeHintForRow(0)
            margins = self.wallet_list_widget.contentsMargins()
            preferred_height = item_height * count + margins.top() + margins.bottom() + 2 * self.wallet_list_widget.spacing()

            # Set a reasonable max height to avoid taking too much space
            max_height = 400

            self.wallet_list_widget.setMinimumHeight(min(preferred_height, max_height))
            self.wallet_list_widget.setMaximumHeight(min(preferred_height, max_height))


    def show_wallet_details(self, item):
        wallet_data = item.data(Qt.ItemDataRole.UserRole)
        if not wallet_data:
            return

        self.wallet_name_display.setText(wallet_data.get("name", "N/A"))
        self.wallet_address_display.setText(wallet_data.get("address", "N/A"))

        # Generate and display QR code
        self.generate_qr_code(wallet_data.get("address", ""))
        
        self.right_panel.setCurrentWidget(self.wallet_details_widget)

    def generate_qr_code(self, address):
        """Generate QR code for wallet address"""
        try:
            # Generate QR code using the backend method
            logo_path = str(ASSETS_PATH / "icons" / "logo_sap.png")
            qr_buffer = self.hood.generate_payment_qrcode(
                wallet=address, 
                currency="eth", 
                logo_path=logo_path if os.path.exists(logo_path) else None
            )
            
            # Convert BytesIO to QPixmap
            qr_buffer.seek(0)
            qr_data = qr_buffer.read()
            
            pixmap = QPixmap()
            pixmap.loadFromData(qr_data)
            
            # Scale pixmap to fit the label
            scaled_pixmap = pixmap.scaled(
                250, 250, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Create a rounded rectangle mask instead of circle
            rounded_pixmap = QPixmap(250, 250)
            rounded_pixmap.fill(Qt.GlobalColor.transparent)
            
            from PyQt6.QtGui import QPainter, QPainterPath
            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Create rounded rectangle path with 50px radius
            path = QPainterPath()
            path.addRoundedRect(0, 0, 250, 250, 50, 50)
            painter.setClipPath(path)
            
            # Draw the QR code
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()
            
            self.qr_code_label.setPixmap(rounded_pixmap)
            
        except Exception as e:
            # Fallback if QR generation fails
            self.qr_code_label.setText(f"QR Error:\n{str(e)[:50]}...")
            self.qr_code_label.setStyleSheet("""
                QLabel {
                    border-radius: 50px;
                }
            """)

    def add_wallet_dialog(self):
        """Open advanced wallet creation dialog"""
        dialog = WalletDialog(self.hood, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_wallet_list()

    def delete_wallet(self):
        """Deletes the selected wallet after confirmation."""
        selected_items = self.wallet_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a wallet to delete.")
            return

        wallet_name = selected_items[0].text()

        reply = QMessageBox.question(self, "Confirmation",
                                     f"Are you sure you want to delete wallet '{wallet_name}'?\nThis action is irreversible.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.hood.delete_wallet(wallet_name)
                QMessageBox.information(self, "Success", f"Wallet '{wallet_name}' has been successfully deleted.")
                self.update_wallet_list() # Refresh the wallet list
                self.right_panel.setCurrentWidget(self.welcome_widget) # Switch to welcome widget
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete wallet: {e}")

    def show_not_implemented_message(self):
        """Shows a message that the feature is not implemented."""
        QMessageBox.information(self, "In Development", "This functionality will be added in future versions.")

    def copy_address_to_clipboard(self):
        """Copy wallet address to clipboard and show notification."""
        address = self.wallet_address_display.text()
        if address and address != "N/A":
            clipboard = QApplication.clipboard()
            clipboard.setText(address)
            
            # Temporarily change button text to show feedback
            original_text = self.copy_address_btn.text()
            self.copy_address_btn.setText("Copied!")
            self.copy_address_btn.setStyleSheet("""
                QPushButton {
                    background-color: #000000;
                    color: white;
                    font-weight: bold;
                    border-radius: 12px;
                    padding: 3px;
                    border: 2px solid #ffffff;
                    font-size: 8pt;
                }
            """)
            
            # Reset button after 1.5 seconds
            QTimer.singleShot(1500, lambda: self.reset_copy_button(original_text))

    def reset_copy_button(self, original_text):
        """Reset copy button to original state."""
        self.copy_address_btn.setText(original_text)
        self.copy_address_btn.setFixedSize(65, 30)
        self.copy_address_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                font-weight: bold;
                border-radius: 12px;
                padding: 3px;
                font-size: 8pt;
            }
        """)

class WalletDialog(QDialog):
    """Advanced dialog for creating or importing wallets"""
    def __init__(self, hood: SapphireHood, parent=None):
        super().__init__(parent)
        self.hood = hood
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Add Wallet')
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12pt;
            }
            QComboBox {
                background-color: #1f1f1f;
                color: #FFFFFF;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QLineEdit, QTextEdit {
                background-color: #1f1f1f;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
                color: #FFFFFF;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px;
                border: none;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Add New Wallet")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Wallet type selection
        type_label = QLabel("Wallet Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Create New Wallet",
            "Import from Private Key", 
            "Import from Mnemonic Phrase",
            "Watch-Only Address"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)

        # Wallet name input
        name_label = QLabel("Wallet Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name for your wallet")
        
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # Dynamic input area
        self.input_label = QLabel()
        self.input_widget = QLineEdit()
        self.input_widget.setPlaceholderText("No additional input required")
        self.input_widget.setEnabled(False)
        
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_widget)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_wallet)
        button_box.rejected.connect(self.reject)
        
        layout.addStretch()
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.on_type_changed("Create New Wallet")  # Initialize with default

    def on_type_changed(self, wallet_type):
        """Handle wallet type change"""
        if wallet_type == "Create New Wallet":
            self.input_label.setText("")
            self.input_widget.setPlaceholderText("No additional input required")
            self.input_widget.setEnabled(False)
            self.input_widget.clear()
            
        elif wallet_type == "Import from Private Key":
            self.input_label.setText("Private Key:")
            self.input_widget.setPlaceholderText("Enter your private key (64 characters)")
            self.input_widget.setEnabled(True)
            self.input_widget.setEchoMode(QLineEdit.EchoMode.Password)
            
        elif wallet_type == "Import from Mnemonic Phrase":
            # Replace with QTextEdit for multiline
            if isinstance(self.input_widget, QLineEdit):
                self.input_widget.setParent(None)
                self.input_widget = QTextEdit()
                self.input_widget.setStyleSheet(self.styleSheet())
                self.layout().insertWidget(5, self.input_widget)
            
            self.input_label.setText("Mnemonic Phrase:")
            self.input_widget.setPlaceholderText("Enter your 12 or 24 word mnemonic phrase")
            self.input_widget.setEnabled(True)
            
        elif wallet_type == "Watch-Only Address":
            # Ensure it's QLineEdit
            if isinstance(self.input_widget, QTextEdit):
                self.input_widget.setParent(None)
                self.input_widget = QLineEdit()
                self.input_widget.setStyleSheet(self.styleSheet())
                self.layout().insertWidget(5, self.input_widget)
                
            self.input_label.setText("Ethereum Address:")
            self.input_widget.setPlaceholderText("0x...")
            self.input_widget.setEnabled(True)
            if hasattr(self.input_widget, 'setEchoMode'):
                self.input_widget.setEchoMode(QLineEdit.EchoMode.Normal)

    def accept_wallet(self):
        """Process wallet creation/import"""
        wallet_name = self.name_input.text().strip()
        wallet_type = self.type_combo.currentText()
        
        if not wallet_name:
            QMessageBox.warning(self, "Error", "Please enter a wallet name.")
            return

        try:
            if wallet_type == "Create New Wallet":
                success, message, data = self.hood.create_new_wallet(wallet_name)
                if success:
                    QMessageBox.information(self, "Success", 
                        f"{message}\n\n"
                        f"Address: {data['address']}\n"
                        f"Private Key: {data['private_key']}\n\n"
                        f"⚠️ IMPORTANT: Save your private key in a secure location!")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", message)
                    
            elif wallet_type == "Import from Private Key":
                private_key = self.input_widget.text().strip()
                if not private_key:
                    QMessageBox.warning(self, "Error", "Please enter a private key.")
                    return
                    
                success, message = self.hood.import_private_key(private_key, wallet_name)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", message)
                    
            elif wallet_type == "Import from Mnemonic Phrase":
                mnemonic = self.input_widget.toPlainText().strip()
                if not mnemonic:
                    QMessageBox.warning(self, "Error", "Please enter a mnemonic phrase.")
                    return
                    
                success, message = self.hood.import_mnemonic(mnemonic, wallet_name)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", message)
                    
            elif wallet_type == "Watch-Only Address":
                address = self.input_widget.text().strip()
                if not address:
                    QMessageBox.warning(self, "Error", "Please enter an Ethereum address.")
                    return
                    
                success, message = self.hood.add_watch_only_wallet(address, wallet_name)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", message)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

def main():
    app = QApplication(sys.argv)

    # Styling
    app.setStyle('Fusion')
    # Set a modern, clean font
    font = QFont("Open Sans", 10)
    app.setFont(font)

    hood = SapphireHood()
    main_win = MainWindow(hood)
    login_win = LoginWindow(hood, main_win)

    login_win.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
