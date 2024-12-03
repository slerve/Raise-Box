from flask import Flask, request, jsonify, render_template
import requests
import datetime

app = Flask(__name__)

# M-Pesa API Credentials
CONSUMER_KEY = 'your_consumer_key'
CONSUMER_SECRET = 'your_consumer_secret'
SHORTCODE = 'your_till_number'
B2C_SHORTCODE = 'your_b2c_shortcode'
SECURITY_CREDENTIAL = 'your_security_credential'
TARGET_PHONE = '2547xxxxxxxx'  # Replace with target phone number

BASE_URL = 'https://sandbox.safaricom.co.ke'  # Use https://api.safaricom.co.ke for production


def get_access_token():
    """Fetch the access token from M-Pesa API."""
    response = requests.get(
        f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
        auth=(CONSUMER_KEY, CONSUMER_SECRET)
    )
    return response.json()['access_token']


@app.route('/')
def home():
    """Serve the homepage."""
    return render_template('index.html')


@app.route('/stk_push', methods=['POST'])
def initiate_stk_push():
    """Initiate an STK Push transaction."""
    data = request.json
    phone_number = data['phone']
    amount = data['amount']

    # Generate M-Pesa password
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = f"{SHORTCODE}your_lipa_na_mpesa_passkey{timestamp}".encode('utf-8')
    
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://your-render-url.com/callback",
        "AccountReference": "Payment",
        "TransactionDesc": "STK Push Payment"
    }

    response = requests.post(
        f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )
    return jsonify(response.json())


@app.route('/callback', methods=['POST'])
def handle_callback():
    """Handle the STK Push callback."""
    data = request.json

    # Check if transaction was successful
    result_code = data['Body']['stkCallback']['ResultCode']
    if result_code == 0:
        amount = int(data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'])
        process_payout(amount)

    return jsonify({"Result": "Callback received"})


def process_payout(amount):
    """Send 98% of the received amount to the target phone."""
    payout_amount = int(amount * 0.98)

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "InitiatorName": "your_initiator_name",
        "SecurityCredential": SECURITY_CREDENTIAL,
        "CommandID": "BusinessPayment",
        "Amount": payout_amount,
        "PartyA": B2C_SHORTCODE,
        "PartyB": TARGET_PHONE,
        "Remarks": "Payout",
        "QueueTimeOutURL": "https://your-render-url.com/timeout",
        "ResultURL": "https://your-render-url.com/result",
        "Occasion": "Payout"
    }

    response = requests.post(
        f"{BASE_URL}/mpesa/b2c/v1/paymentrequest",
        json=payload,
        headers=headers
    )
    print(response.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
