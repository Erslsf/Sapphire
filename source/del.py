import sys
import json
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QSize

# ---- 1. Загружаем данные с Binance ----
def get_binance_klines(symbol="BTCUSDT", interval="1h", limit=100) -> list[dict]:
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
# ---- 2. HTML с Lightweight Charts ----
def generate_html(candles_json):
    html = f"""
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
                width: window.innerWidth,
                height: window.innerHeight,
                layout: {{
                    background: {{ color: '#131722' }},
                    textColor: '#d1d4dc',
                }},
                grid: {{
                    vertLines: {{ color: 'rgba(43, 43, 67, 0.5)', style: 1 }},
                    horzLines: {{ color: 'rgba(43, 43, 67, 0.5)', style: 1 }},
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
            
            const data = {json.dumps(candles_json)};
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
    return html


# ---- 3. Основное окно PyQt ----
class CryptoChartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sapphire Chart — BTC/USDT")
        self.resize(1200, 800)
        self.setMinimumSize(QSize(800, 600))

        candles = get_binance_klines(limit=200)  # Увеличим количество свечей
        html = generate_html(candles)

        self.browser = QWebEngineView()
        self.browser.setHtml(html)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)  # Уберем отступы
        layout.addWidget(self.browser)
        self.setCentralWidget(central)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Обновим размер графика при изменении окна
        self.browser.page().runJavaScript(
            f"chart.resize({self.width()}, {self.height()});"
        )


# ---- 4. Запуск ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoChartApp()
    window.show()
    sys.exit(app.exec())
