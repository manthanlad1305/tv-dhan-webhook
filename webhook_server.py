from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your Dhan credentials
DHAN_ACCESS_TOKEN = "your_access_token_here"
DHAN_CLIENT_ID = "your_client_id_here"

# Dhan API endpoints
BASE_URL = "https://api.dhan.co"

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

@app.route('/', methods=['POST'])
def webhook_server():
    data = request.json
    print("Received webhook:", data)

    signal = data.get('strategy', {}).get('order_action')
    quantity = int(data.get('strategy', {}).get('order_contracts', 1))
    symbol = data.get('ticker', 'RELIANCE-EQ')  # Example: "RELIANCE-EQ"

    if signal == "buy":
        place_order("BUY", quantity, symbol)
    elif signal == "sell":
        place_order("SELL", quantity, symbol)
    
    return jsonify({"status": "order received"})
