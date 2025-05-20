@app.route('/', methods=['POST'])
def webhook_server():
    global net_position

    data = request.json
    print("Received webhook:", data)

    # Support both new payload and TradingView-style payloads
    signal = data.get('transactionType') or data.get('strategy', {}).get('order_action')
    quantity = int(data.get('quantity') or data.get('strategy', {}).get('order_contracts', 1))

    # Convert TradingView or direct ticker to Dhan format
    tv_ticker = data.get('ticker') or data.get('tradingSymbol') or "NSE:PPLPHARMA"
    symbol = tv_ticker.split(':')[-1].replace('-EQ', '') + '-EQ'

    print(f"Signal: {signal}, Quantity: {quantity}, Symbol: {symbol}, Current Position: {net_position}")

    if signal and signal.lower() == "buy":
        if net_position >= 0:
            place_order("BUY", quantity, symbol)
            net_position += quantity
        else:
            reversal_qty = abs(net_position) + quantity
            place_order("BUY", reversal_qty, symbol)
            net_position = quantity

    elif signal and signal.lower() == "sell":
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
