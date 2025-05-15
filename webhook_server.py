from flask import Flask, request, jsonify
import requests
import os

app = Flask(**name**)

# Load credentials from environment variables (Render Dashboard)

DHAN\_ACCESS\_TOKEN = os.getenv("DHAN\_ACCESS\_TOKEN")
DHAN\_CLIENT\_ID = os.getenv("DHAN\_CLIENT\_ID")  # Not used here but available

# Dhan base API endpoint

BASE\_URL = "[https://api.dhan.co](https://api.dhan.co)"

# Track net position in-memory (simple for testing)

net\_position = 0

def place\_order(transaction\_type, quantity, symbol, exchange='NSE'):
"""Send order request to Dhan"""
url = f"{BASE\_URL}/orders"
headers = {
"access-token": DHAN\_ACCESS\_TOKEN,
"Content-Type": "application/json"
}
payload = {
"securityId": symbol,
"transactionType": transaction\_type,  # BUY or SELL
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
print(f"Order Response: {response.status\_code} - {response.text}")
return response.json()

@app.route('/', methods=\['POST'])
def webhook\_server():
global net\_position

```
data = request.json
print("Received webhook:", data)

# Get signal and quantity safely
signal = data.get('strategy', {}).get('order_action')
quantity = int(data.get('strategy', {}).get('order_contracts', 1))

# Convert TradingView symbol like "NSE:RELIANCE" → "RELIANCE-EQ"
tv_ticker = data.get('ticker', 'NSE:RELIANCE')
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
```
