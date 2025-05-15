from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(_name_)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load credentials from environment variables
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")

# Dhan base API endpoint
BASE_URL = "https://api.dhan.co"

# Track net position in-memory
net_position = 0

def place_order(transaction_type, quantity, symbol, exchange='NSE'):
 url = f"{BASE_URL}/orders"
 headers = {
 "access-token": DHAN_ACCESS_TOKEN,
 "client-id": DHAN_CLIENT_ID,
 "Content-Type": "application/json"
 }
 payload = {
 "securityId": symbol,
 "transactionType": transaction_type.upper(),
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
 try:
 response = requests.post(url, headers=headers, json=payload)
 response.raise_for_status()
 return response.json()
 except requests.RequestException as e:
 logging.error(f"Order placement failed: {e}")
 return None

@app.route('/', methods=['POST'])
def webhook_server():
 global net_position
 try:
 data = request.json
 signal = data['strategy']['order_action']
 quantity = int(data['strategy']['order_contracts'])
 tv_ticker = data['ticker']
 symbol = tv_ticker.split(':')[-1] + '-EQ'
 
 if signal not in ["buy", "sell"]:
 return jsonify({"error": "Invalid signal"}), 400
 
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
 
 logging.info(f"New Position: {net_position}")
 return jsonify({"status": "Order processed", "net_position": net_position})
 except KeyError as e:
 logging.error(f"Missing key: {e}")
 return jsonify({"error": "Missing data"}), 400
 except Exception as e:
 logging.error(f"Error: {e}")
 return jsonify({"error": "Internal server error"}), 500

if _name_ == '_main_':
 port = int(os.environ.get('PORT', 10000))
 app.run(host='0.0.0.0', port=port)
