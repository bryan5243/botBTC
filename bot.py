import ccxt
import pandas as pd
import time
import datetime
import requests
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD

# ====== CONFIGURACIÓN INICIAL ======
# Tus claves de Binance (no se usarán en este modo)
API_KEY = 'TU_API_KEY'
API_SECRET = 'TU_API_SECRET'

# Telegram
TELEGRAM_TOKEN = '8163850761:AAFGQ8PQHQn-8WjVTTH5Zya_9lwcQUD8y_Y'
CHAT_ID = '6879089502'

# Parámetros del bot
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'
CHECK_INTERVAL = 900  # cada 15 minutos

# Solo conexión pública a Binance (sin autenticación)
exchange = ccxt.binance()

# Función para enviar mensajes a Telegram
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        print("Error al enviar mensaje Telegram")

# Preguntar cuánto BTC desea usar
btc_usar = float(input("\n¿Cuánto BTC deseas usar en este ciclo?: "))

# Función principal del bot (solo alertas, sin trading real)
def run_bot():
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Indicadores técnicos
            df['ema9'] = EMAIndicator(df['close'], window=9).ema_indicator()
            df['ema21'] = EMAIndicator(df['close'], window=21).ema_indicator()
            df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
            macd = MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()

            precio_actual = df['close'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            ema9 = df['ema9'].iloc[-1]
            ema21 = df['ema21'].iloc[-1]
            macd_val = df['macd'].iloc[-1]
            macd_signal = df['macd_signal'].iloc[-1]

            mensaje = f"\n[ANÁLISIS TÉCNICO]\nBTC/USDT: {precio_actual:.2f} USDT\nRSI: {rsi:.2f}\nEMA9: {ema9:.2f} | EMA21: {ema21:.2f}\nMACD: {macd_val:.2f} / {macd_signal:.2f}"

            # Solo alertas con recomendación, sin ejecutar órdenes
            if rsi < 30 and ema9 > ema21 and macd_val > macd_signal:
                mensaje += f"\n🟢 Señal: RECOMENDACIÓN DE COMPRA"

            elif rsi > 70 and ema9 < ema21 and macd_val < macd_signal:
                mensaje += f"\n🔴 Señal: RECOMENDACIÓN DE VENTA"
            else:
                mensaje += f"\n🟡 Sin señal clara: Esperar"

            print(mensaje)
            send_telegram(mensaje)

        except Exception as e:
            print(f"[ERROR] {e}")
            send_telegram(f"[ERROR] {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    send_telegram("🤖 Bot en modo solo análisis y alertas iniciado correctamente")
    run_bot()
