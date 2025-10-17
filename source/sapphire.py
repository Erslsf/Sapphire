"""" 
version = 1.4.a2
This file is part of the Sapphire project, a decentralized finance (DeFi) application.
It is distributed under the GNU General Public License v3.0 (GPL-3.0).
Main architecturer: B.E.S
Designed with ❤️ by DEECKER in Astana, Kazakhstan.
This file contains the main GUI for the Sapphire application, including login and wallet management.
"""
# 0xff226e6a8406454f95aae9e4d16c36be5960c9ff


import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QSizePolicy,
    QStackedWidget, QFormLayout, QInputDialog, QListWidgetItem, QDialog,
    QDialogButtonBox, QTextEdit, QComboBox, QScrollArea, QFrame
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QPainterPath, QClipboard
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent
    
BASE_PATH = get_base_path()

source_path = str(BASE_PATH / "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)
try:
    from sapphire_hood import SapphireHood
except ImportError as e:
    print(f"Ошибка импорта sapphire_hood: {e}")
    print(f"Текущий рабочий каталог: {os.getcwd()}")
    print(f"Базовый путь: {BASE_PATH}")
    print(f"Путь к source: {source_path}")
    sys.exit(1)

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
    def __init__(self, hood: SapphireHood):
        super().__init__()
        self.hood = hood
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sapphire')
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #1A1A1A;
                border: none;
                border-radius: 8px;
                padding: 10px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)

        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        
        # 2. Content container
        content = QHBoxLayout()
        content.setContentsMargins(0, 10, 0, 10)  # Добавляем отступы сверху и снизу
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        self.sidebar.setFixedWidth(0)  # Устанавливаем начальную ширину 0

        # 1. Header
        header = self.create_header()

        # Main content area
        main_area = QVBoxLayout()
        main_area.setContentsMargins(10, 0, 10, 0)  # Добавляем отступы слева и справа
        
        # График
        chart_container = QFrame()
        chart_container.setStyleSheet("background-color: None; border-radius: 10px; margin: 10px;")
        chart_layout = QVBoxLayout(chart_container)
        
        self.chart_view = QWebEngineView()
        self.chart_view.setFixedHeight(400)
        
        chart_layout.addWidget(self.chart_view)
        
        # Список криптовалют
        crypto_list = self.create_crypto_list()
        
        main_area.addWidget(chart_container)
        main_area.addWidget(crypto_list)
        main_area.addStretch()
        
        content.addWidget(self.sidebar)
        content.addLayout(main_area)
        
        # Footer
        # footer = self.create_footer()
        
        main_layout.addWidget(header)
        main_layout.addLayout(content)
        # main_layout.addWidget(footer)

    def create_header(self):
        header = QFrame()
        header.setStyleSheet("background-color: #1A1A1A;")
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Меню кнопка
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A1A1A;
                border: none;
                color: #FFFFFF;
                font-size: 18pt;
            }""")

        self.menu_btn.clicked.connect(self.toggle_sidebar)
        
        # Баланс
        balance = QLabel("Balance: $10,245.50")
        balance.setStyleSheet("font-size: 12px; font-weight: bold;")
        
        # Лого
        logo = QLabel()
        logo_path = str(ASSETS_PATH / "icons" / "sp.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo.setPixmap(pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio))
        
        layout.addWidget(self.menu_btn)
        layout.addWidget(balance)
        layout.addStretch()
        layout.addWidget(logo)
        
        return header

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                margin: 10px 10px;  /* Отступ сверху и снизу */
                border-radius: 10px;
            }
            QPushButton {
                 font-weight: 600;
                font-size: 15px;
                text-align: left;
                margin: 5px 10px;
                border-radius: 8px;
            }
        """)
        sidebar.setFixedWidth(250)
        
        # Добавляем внутренние отступы
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Контейнер для кнопок с отступами
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        buttons_layout.setSpacing(8)
        buttons_container.setStyleSheet("""
            QWidget {
                background: none;
            }
            QPushButton {
                background: none;
                text-align: left;
                margin: 5px 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2D2D2D;
            }
        """)
        
        buttons = ['Dashboard', 'Wallets', 'Settings', 'Exchange', 'Buy', 'Sell', 'Send']
        for text in buttons:
            btn = QPushButton(text)
            buttons_layout.addWidget(btn)
        
        buttons_layout.addStretch()
        layout.addWidget(buttons_container)
        
        return sidebar

    def create_crypto_list(self):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border-radius: 10px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(container)
        
        # Заголовок
        header = QHBoxLayout()
        header.addWidget(QLabel("Asset"))
        header.addWidget(QLabel("Price"))
        header.addWidget(QLabel("Change"))
        layout.addLayout(header)
        
        # Список криптовалют
        cryptos = [
            ("BTC", "$48,235.00", "+2.5%"),
            ("ETH", "$2,354.00", "+1.8%"),
            ("BNB", "$312.45", "-0.5%"),
        ]
        
        for symbol, price, change in cryptos:
            row = QHBoxLayout()
            row.addWidget(QLabel(symbol))
            row.addWidget(QLabel(price))
            
            change_label = QLabel(change)
            change_label.setStyleSheet(
                f"color: {'#22c55e' if '+' in change else '#ef4444'};"
            )
            row.addWidget(change_label)
            
            layout.addLayout(row)
        
        return container

    def create_footer(self):
        footer = QFrame()
        footer.setStyleSheet("background-color: #1A1A1A;")
        footer.setFixedHeight(40)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)
        
        version = QLabel("Version 1.4.a2")
        copyright = QLabel("© 2024 Sapphire")
        
        layout.addWidget(version)
        layout.addStretch()
        layout.addWidget(copyright)
        
        return footer
    
    def toggle_sidebar(self):
        current_width = self.sidebar.width()
        target_width = 250 if current_width == 0 else 0
        
        # Создаем анимацию
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        # Также анимируем maximumWidth для обеспечения правильного поведения
        self.animation2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.animation2.setDuration(200)
        self.animation2.setStartValue(current_width)
        self.animation2.setEndValue(target_width)
        self.animation2.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        # Запускаем анимации
        self.animation.start()
        self.animation2.start()

    def post_login_setup(self):
        """Called after successful login"""
        self.load_chart_data()

    def load_chart_data(self):
        # Получаем данные через hood
        candle_data = self.hood.get_binance_klines()
        
        chart_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://unpkg.com/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js"></script>
    </head>
    <body style="margin:0; background-color:#131722;">
        <div id="chart" style="width:100%; height:100vh;"></div>
        <script>
            const chartOptions = {{
                layout: {{
                    background: {{ color: '#000000' }},
                    textColor: '#d1d4dc',
                }},
                grid: {{
                    vertLines: {{ color: 'rgba(43, 43, 67, 0.7)', style: 1 }},
                    horzLines: {{ color: 'rgba(43, 43, 67, 0.7)', style: 1 }},
                }},
                crosshair: {{
                    mode: LightweightCharts.CrosshairMode.Normal,
                    vertLine: {{
                        color: '#555',
                        width: 1,
                        style: 1,
                        labelBackgroundColor: '#131722',
                    }},
                    horzLine: {{
                        color: '#555',
                        width: 1,
                        style: 1,
                        labelBackgroundColor: '#131722',
                    }},
                }},
                timeScale: {{
                    borderColor: '#2B2B43',
                    timeVisible: true,
                    secondsVisible: false,
                    rightOffset: 12,
                    barSpacing: 6,
                }},
                rightPriceScale: {{
                    borderColor: '#2B2B43',
                    scaleMargins: {{
                        top: 0.1,
                        bottom: 0.1,
                    }},
                }},
            }};
            
            const chart = LightweightCharts.createChart(document.getElementById('chart'), chartOptions);
            const candlestickSeries = chart.addCandlestickSeries({{
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderVisible: false,
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
                priceFormat: {{ type: 'price', precision: 2, minMove: 0.01 }},
            }});
            
            const data = {json.dumps(candle_data)};
            candlestickSeries.setData(data);
            
            // Автомасштабирование и адаптивность
            chart.timeScale().fitContent();
            
            window.addEventListener('resize', () => {{
                chart.applyOptions({{
                    width: window.innerWidth,
                    height: window.innerHeight
                }});
            }});
        </script>
    </body>
    </html>
    """
        
        self.chart_view.setHtml(chart_html)

def main():
    app = QApplication(sys.argv)
    hood = SapphireHood()
    main_window = MainWindow(hood)
    login_window = LoginWindow(hood, main_window)
    login_window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()