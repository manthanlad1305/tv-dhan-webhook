from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load credentials from environment variables
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")  # Not used but loaded

# Check for token presence
if not DHAN_ACCESS_TOKEN:
    raise ValueError("Missing DHAN_ACCESS_TOKEN environment variable")

BASE_URL = "https://api.dhan.co"
net_position = 0  # Simple state tracker

def place_order(transaction_type, quantity, symbol, exchange='NSE'):
    url = f"{BASE_URL}/orders"
    headers = {
        "access-token": DHAN_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "securityId": symbol,
        "transactionType": transaction_type,
        "exchangeSegment": exchange,
        "orderType": "MARKET",
        "productType": "INTRADAY",
        "quantity": quantity,
        "price": 0.0,
        "disclosedQuantity": 0,
        "afterMarketOrder": False,
        "validity": "DAY",
        "tag": "TV-Auto"
    }
    response = requests.post(url, headers=headers, json=payload)

    try:
        response.raise_for_status()
        logging.info("Order successful: %s", response.text)
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error("Order failed: %s", response.text)
        return {"error": str(e), "details": response.text}

@app.route('/', methods=['POST'])
def webhook_server():
    global net_position
    data = request.json
    logging.info("Received webhook: %s", data)

    signal = data.get('strategy', {}).get('order_action')
    quantity = int(data.get('strategy', {}).get('order_contracts', 1))

    tv_ticker = data.get('ticker', 'NSE:RELIANCE')
    symbol_base = tv_ticker.split(':')[-1] if ':' in tv_ticker else tv_ticker
    symbol = symbol_base + '-EQ'

    logging.info("Signal: %s, Quantity: %d, Symbol: %s, Current Position: %d", signal, quantity, symbol, net_position)

    if signal == "buy":
        if net_position >= 0:
            place_order("BUY", quantity, symbol)
            net_position += quantity
        else:
            reversal_qty = abs(net_position) + quantity
            place_order("BUY", reversal_qty, symbol)
            net_position = quantity

    elif signal == "sell":
        if net_position <= 0:
            place_order("SELL", quantity, symbol)
            net_position -= quantity
        else:
            reversal_qty = net_position + quantity
            place_order("SELL", reversal_qty, symbol)
            net_position = -quantity
    else:
        logging.warning("Invalid or missing signal.")
        return jsonify({"error": "Invalid signal"}), 400

    logging.info("New Position: %d", net_position)
    return jsonify({"status": "Order processed", "net_position": net_position})
