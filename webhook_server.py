from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load credentials from environment variables (Render Dashboard)
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")

# Dhan base API endpoint
BASE_URL = "https://api.dhan.co"

# Track net position in-memory (simple for testing)
net_position = 0

def place_order(transaction_type, quantity, symbol, exchange='NSE'): 
    """Send order request to Dhan"""
    url = f"{BASE_URL}/orders"
    headers = {
        "access-token": DHAN_ACCESS_TOKEN,
        "client-id": DHAN_CLIENT_ID,
        "Content-Type": "application/json"
    }
    payload = {
        "securityId": symbol,
        "transactionType": transaction_type.upper(),  # BUY or SELL
        "exchangeSegment": "NSE_EQ",
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
    print(f"Order Response: {response.status_code} - {response.text}")
    return response.json()

@app.route('/', methods=['POST'])
def webhook_server():
    global net_position

    data = request.json
    print("Received webhook:", data)

    # Get signal and quantity safely
    signal = data.get('strategy', {}).get('order_action')
    quantity = int(data.get('strategy', {}).get('order_contracts', 1))

    # Convert TradingView symbol like "NSE:RELIANCE" → "RELIANCE-EQ"
    tv_ticker = data.get('ticker', 'NSE:PPLPHARMA')
    symbol = tv_ticker.split(':')[-1] + '-EQ'

    print(f"Signal: {signal}, Quantity: {quantity}, Symbol: {symbol}, Current Position: {net_position}")

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
        print("Invalid or missing signal.")
        return jsonify({"error": "Invalid signal"}), 400

    print(f"New Position: {net_position}")
    return jsonify({"status": "Order processed", "net_position": net_position})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
