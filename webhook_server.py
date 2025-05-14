from flask import Flask, request, jsonify
import requests
app = Flask(__name__)

# Replace with your Dhan credentials
DHAN_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzQ5Nzg0MDYxLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNzAwMzY0NSJ9.Y2j1F2jkDHeFmzCSMf8gtqqroiZx7msdC1eb8KuMGaj5CRIf138oLXQ6rV40E0n8P-caWfWOZzy62MwrMc3MTQ"
DHAN_CLIENT_ID = "1107003645"

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
    symbol = data.get('ticker', 'PIRAMAL PHARMA LTD-EQ')  # Example: "RELIANCE-EQ"

    if signal == "buy":
        place_order("BUY", quantity, symbol)
    elif signal == "sell":
        place_order("SELL", quantity, symbol)
    
    return jsonify({"status": "order received"})
