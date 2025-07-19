import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def get_stock_decision(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="3mo")

    if hist.empty or len(hist) < 30:
        return "Not enough data to make a decision."

    # Add indicators
    hist['SMA_5'] = hist['Close'].rolling(window=5).mean()
    hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
    hist['RSI'] = calculate_rsi(hist)
    hist['MACD'], hist['MACD_Signal'] = calculate_macd(hist)

    latest = hist.iloc[-1]

    # Decision logic
    decision_reasons = []

    # Moving Average Cross
    if latest['SMA_5'] > latest['SMA_20']:
        decision_reasons.append("Short-term trend is bullish (SMA5 > SMA20)")
    elif latest['SMA_5'] < latest['SMA_20']:
        decision_reasons.append("Short-term trend is bearish (SMA5 < SMA20)")

    # RSI logic
    if latest['RSI'] < 30:
        decision_reasons.append("Stock is oversold (RSI < 30) — potential BUY")
    elif latest['RSI'] > 70:
        decision_reasons.append("Stock is overbought (RSI > 70) — potential SELL")

    # MACD crossover
    if latest['MACD'] > latest['MACD_Signal']:
        decision_reasons.append("MACD bullish crossover — BUY signal")
    elif latest['MACD'] < latest['MACD_Signal']:
        decision_reasons.append("MACD bearish crossover — SELL signal")

    # Final decision logic (simple rule-based voting)
    buy_signals = sum([
        latest['SMA_5'] > latest['SMA_20'],
        latest['RSI'] < 30,
        latest['MACD'] > latest['MACD_Signal']
    ])
    sell_signals = sum([
        latest['SMA_5'] < latest['SMA_20'],
        latest['RSI'] > 70,
        latest['MACD'] < latest['MACD_Signal']
    ])

    if buy_signals >= 2:
        final_decision = "BUY"
    elif sell_signals >= 2:
        final_decision = "SELL"
    else:
        final_decision = "WAIT"

    return f"{final_decision}\nReasons:\n- " + "\n- ".join(decision_reasons)

if __name__ == "__main__":
    symbol = input("Enter stock symbol (e.g., AAPL, TSLA): ").upper()
    decision = get_stock_decision(symbol)
    print(f"\nDecision for {symbol}:\n{decision}")
