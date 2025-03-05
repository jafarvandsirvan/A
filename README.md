import requests
import yfinance as yf
import pandas_ta as ta
import time

# اطلاعات ربات تلگرام
TOKEN = "8133831090:AAGOvWpNA7SZmu_N0YajzHXIHvIYwEsqKE4"
CHAT_ID = "5328616873"

# لیست جفت‌ارزهای فارکس
symbols = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
    "EURGBP=X", "EURJPY=X", "EURCHF=X", "AUDJPY=X", "AUDCHF=X", "CADJPY=X", "GBPJPY=X",
    "GBPCHF=X", "NZDJPY=X", "NZDCHF=X", "CHFJPY=X"
]

# دریافت داده‌های قیمت از یاهو فایننس
def get_data(symbol="EURUSD=X"):
    try:
        df = yf.download(symbol, period="7d", interval="1h")
        df = df[["Open", "High", "Low", "Close"]]
        df.columns = ["open", "high", "low", "close"]
        return df
    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}")
        return None

# تحلیل بازار و تعیین میزان سرمایه‌گذاری
def analyze_market(symbol):
    df = get_data(symbol)
    if df is None or df.empty:
        return None, None, None, None, None, None, None

    # محاسبه اندیکاتورها
    df["RSI"] = ta.rsi(df["close"], length=14)

    macd_result = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if macd_result is None or macd_result.empty:
        return None, None, None, None, None, None, None

    df["MACD"] = macd_result["MACD_12_26_9"]
    df["MACD_signal"] = macd_result["MACDs_12_26_9"]
    df["SMA_50"] = ta.sma(df["close"], length=50)

    last = df.iloc[-1]
    entry_price = round(last["close"], 5)  # قیمت ورود به معامله

    signal = None
    tp = None
    sl = None
    risk_percentage = 1  # حداقل درصد سرمایه
    signal_strength = "🟢 ضعیف"  # مقدار پیش‌فرض

    # شرایط ورود به معامله
    if last["RSI"] < 40 and last["MACD"] > last["MACD_signal"] and last["close"] > last["SMA_50"] * 0.99:
        signal = "Buy"
        tp = round(last["close"] * 1.01, 5)  # حد سود 1٪ بالاتر
        sl = round(last["close"] * 0.99, 5)  # حد ضرر 1٪ پایین‌تر

        if last["RSI"] < 30:
            risk_percentage = 5  # سرمایه‌گذاری ۵٪ سرمایه
            signal_strength = "🔴 قوی"
        else:
            risk_percentage = 3  # سرمایه‌گذاری ۳٪ سرمایه
            signal_strength = "🟡 متوسط"

    elif last["RSI"] > 60 and last["MACD"] < last["MACD_signal"] and last["close"] < last["SMA_50"] * 1.01:
        signal = "Sell"
        tp = round(last["close"] * 0.99, 5)  # حد سود 1٪ پایین‌تر
        sl = round(last["close"] * 1.01, 5)  # حد ضرر 1٪ بالاتر

        if last["RSI"] > 70:
            risk_percentage = 5  # سرمایه‌گذاری ۵٪ سرمایه
            signal_strength = "🔴 قوی"
        else:
            risk_percentage = 3  # سرمایه‌گذاری ۳٪ سرمایه
            signal_strength = "🟡 متوسط"

    return signal, entry_price, tp, sl, risk_percentage, signal_strength

# ارسال سیگنال به تلگرام
def send_signal():
    for symbol in symbols:
        signal, entry_price, tp, sl, risk_percentage, signal_strength = analyze_market(symbol)
        if signal:
            message = f"📊 **سیگنال فارکس** 📊\n\n" \
                      f"📈 **جفت ارز:** {symbol}\n" \
                      f"📉 **سیگنال:** {signal}\n" \
                      f"🔹 **قیمت ورود:** {entry_price}\n" \
                      f"🎯 **حد سود (TP):** {tp}\n" \
                      f"🛑 **حد ضرر (SL):** {sl}\n" \
                      f"💰 **درصد سرمایه پیشنهادی:** {risk_percentage}%\n" \
                      f"⚡ **قدرت سیگنال:** {signal_strength}"
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
            except Exception as e:
                print(f"Error sending message to Telegram: {e}")
        else:
            print(f"No signal for {symbol}")

# اجرای کد هر یک ساعت یکبار
while True:
    send_signal()
    time.sleep(3600)
