from flask import Flask, render_template, request, jsonify, send_file
import secrets
import string
import requests
import hashlib
import qrcode
from io import BytesIO
import base64
from utils import (
    calculate_entropy,
    time_to_crack,
    classify_strength,
    check_password_health,
    generate_passphrase
)
from forms import PasswordForm
import pdfkit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
HIBP_API_URL = "https://api.pwnedpasswords.com/range/"

def generate_password(length=12, use_digits=True, use_symbols=True):
    characters = string.ascii_letters
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def check_breach(password):
    sha1_password = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]
    try:
        response = requests.get(HIBP_API_URL + prefix, timeout=3)
        if response.status_code == 200:
            hashes = response.text.splitlines()
            return any(suffix in line for line in hashes)
    except Exception as e:
        print(f"Error checking breach: {str(e)}")
    return False

def generate_qr_code(password):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(password)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    form = PasswordForm()
    password = None
    entropy = None
    crack_time = None
    strength = None
    health_report = None
    breached = False
    qr_code = None
    password_type = None

    if form.validate_on_submit():
        print("\n=== FORM SUBMISSION ===")
        print(f"Password Type: {form.password_type.data}")
        print(f"Length: {form.length.data}")
        print(f"Digits: {form.use_digits.data}")
        print(f"Symbols: {form.use_symbols.data}")
        print(f"Strength: {form.strength_level.data}")

        password_type = form.password_type.data
        length = form.length.data
        use_digits = form.use_digits.data
        use_symbols = form.use_symbols.data
        strength_level = form.strength_level.data

        try:
            if password_type == 'passphrase':
                print("\nGENERATING PASSPHRASE")
                word_count = 4  # Default
                if strength_level == '1': word_count = 3
                elif strength_level == '3': word_count = 6
                
                password = generate_passphrase(word_count=word_count)
                print(f"Generated passphrase: {password}")
            else:
                print("\nGENERATING PASSWORD")
                if strength_level == '1':  # Easy
                    length = 8
                    use_symbols = False
                elif strength_level == '3':  # Hard
                    length = 16
                
                password = generate_password(length, use_digits, use_symbols)
                print(f"Generated password: {password}")

            # Calculate metrics
            entropy = calculate_entropy(password)
            strength = classify_strength(entropy)
            health_report = check_password_health(password)
            crack_time = time_to_crack(entropy)
            breached = check_breach(password)
            qr_code = generate_qr_code(password)

        except Exception as e:
            print(f"\nERROR DURING GENERATION: {str(e)}")
            password = "Error generating password. Please try again."

    return render_template(
        "index.html",
        form=form,
        password=password,
        password_type=password_type,
        entropy=entropy,
        strength=strength,
        health_report=health_report,
        crack_time=crack_time,
        breached=breached,
        qr_code=qr_code
    )
    

@app.route("/live-analysis", methods=["POST"])
def live_analysis():
    data = request.get_json()
    password = data.get('password', '')

    if not password:
        return jsonify({"error": "No password provided"}), 400

    entropy = calculate_entropy(password)
    strength = classify_strength(entropy)
    health_report = check_password_health(password)
    crack_time = time_to_crack(entropy)

    return jsonify({
        "entropy": entropy,
        "strength": strength,
        "health_report": health_report,
        "crack_time": crack_time
    })

@app.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.get_json()
    html = f"""
    <html>
        <head><title>Password Security Report</title></head>
        <body>
            <h1>Password Security Report</h1>
            <p><strong>Password:</strong> {data.get('password', '')}</p>
            <p><strong>Strength:</strong> {data.get('strength', '')}</p>
            <p><strong>Entropy:</strong> {data.get('entropy', '')} bits</p>
            <p><strong>Estimated Crack Time:</strong> {data.get('crack_time', '')}</p>
            <p><strong>Health Check:</strong> {data.get('health_report', '')}</p>
            <p><strong>Breached:</strong> {'Yes' if data.get('breached', False) else 'No'}</p>
        </body>
    </html>
    """

    pdf = pdfkit.from_string(html, False)
    return send_file(
        BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='password_report.pdf'
    )

if __name__ == "__main__":
    app.run(debug=True)