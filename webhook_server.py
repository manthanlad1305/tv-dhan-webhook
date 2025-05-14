from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Read Dhan credentials from environment variables (set these in Render dashboard)
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")

# Dhan API base URL
BASE_URL = "https://api.dhan.co"

# Function to place an order
def place_order(transaction_type, quantity, symbol, exchange='NSE'):
    url = f"{BASE_URL}/orders"
    headers = {
        "access-token": DHAN_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "securityId": symbol,
        "transactionType": transaction_type,  # "BUY" or "SELL"
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
    print(response.status_code, response.text)
    return response.json()

# Flask route to handle webhook POST requests
@app.route('/', methods=['POST'])
def webhook_server():
    data = request.json
    print("Received webhook:", data)

    signal = data.get('strategy', {}).get('order_action')
    quantity = int(data.get('strategy', {}).get('order_contracts', 1))
    symbol = data.get('ticker', 'RELIANCE-EQ')  # Replace with your default symbol if needed

    if signal == "buy":
        place_order("BUY", quantity, symbol)
    elif signal == "sell":
        place_order("SELL", quantity, symbol)
    
    return jsonify({"status": "order received"})

# Run the Flask app and bind to the port Render provides
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
