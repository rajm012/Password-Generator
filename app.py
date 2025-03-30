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
    except:
        return False
    return False

def generate_qr_code(password):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(password)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


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
    password_type = None  # Track password type for template

    if form.validate_on_submit():
        length = form.length.data
        use_digits = form.use_digits.data
        use_symbols = form.use_symbols.data
        strength_level = form.strength_level.data
        password_type = form.password_type.data  # Get the selected password type

        # Adjust settings based on strength level
        if strength_level == '1':  # Easy
            length = min(8, length)
            use_symbols = False
        elif strength_level == '3':  # Hard
            length = max(16, length)
            use_symbols = True
        else:
            length = length
            use_symbols = True

        # Generate password or passphrase based on selection
        if password_type == 'passphrase':
            # For passphrases, length represents word count (1-10 words)
            word_count = max(1, min(10, length))
            password = generate_passphrase(word_count=word_count,use_digits=use_digits, use_symbols=use_symbols)
        else:
            password = generate_password(length, use_digits, use_symbols)

        # Calculate metrics
        entropy = calculate_entropy(password)
        strength = classify_strength(entropy)
        health_report = check_password_health(password)
        crack_time = time_to_crack(entropy)
        breached = check_breach(password)
        qr_code = generate_qr_code(password)

    return render_template(
        "index.html",
        form=form,
        password=password,
        password_type=password_type,  # Pass to template
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