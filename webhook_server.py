from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received alert:", data)

    action = data.get("action")
    qty = data.get("qty", 1)

    # Placeholder for Dhan API call
    print(f"Executing {action.upper()} for quantity {qty}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
