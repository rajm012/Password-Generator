document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    console.log("DOM fully loaded");
    const darkModeToggle = document.getElementById('toggle-dark');
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });

    // Initialize dark mode from localStorage
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }

    // Clipboard copy
    if (document.getElementById('copy-btn')) {
        new ClipboardJS('#copy-btn');
        document.getElementById('copy-btn').addEventListener('click', () => {
            alert('Password copied to clipboard! Clipboard will clear in 10 seconds.');
            setTimeout(() => navigator.clipboard.writeText(''), 10000);
        });
    }

    // Initialize form fields based on password type
    const passwordTypeRadios = document.querySelectorAll('input[name="password_type"]');
    
    // Set initial state
    const initialType = document.querySelector('input[name="password_type"]:checked').value;
    updateFormFields(initialType);
    console.log(`Initial type: ${initialType}`);
    // Update on change

    passwordTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateFormFields(this.value);
        });
    });

    // Update on type change
    document.querySelectorAll('input[name="password_type"]').forEach(radio => {
        radio.addEventListener('change', function() {
            console.log(`Password type changed to: ${this.value}`);
            updateFormFields(this.value);
        });
    });

    function updateFormFields(type) {
        console.log(`Updating form for type: ${type}`);
        const lengthLabel = document.getElementById('length-label');
        const lengthInput = document.getElementById('length');
        const digitsCheckbox = document.getElementById('use_digits');
        const symbolsCheckbox = document.getElementById('use_symbols');

        if (type === 'passphrase') {
            console.log("Configuring for passphrase");
            lengthLabel.textContent = 'Number of Words (3-6)';
            lengthInput.min = 3;
            lengthInput.max = 6;
            lengthInput.value = 4;
            digitsCheckbox.disabled = true;
            symbolsCheckbox.disabled = true;
            digitsCheckbox.checked = false;
            symbolsCheckbox.checked = false;
        } else {
            console.log("Configuring for password");
            lengthLabel.textContent = 'Password Length (8-64)';
            lengthInput.min = 8;
            lengthInput.max = 64;
            lengthInput.value = 12;
            digitsCheckbox.disabled = false;
            symbolsCheckbox.disabled = false;
        }
    }


    // Generate PDF report
    if (document.getElementById('generate-report')) {
        document.getElementById('generate-report').addEventListener('click', () => {
            const password = document.getElementById('password').textContent;
            const strength = document.querySelector('.strength').textContent;
            const entropy = document.querySelectorAll('.info-item')[1].querySelector('.value').textContent;
            const crackTime = document.querySelectorAll('.info-item')[2].querySelector('.value').textContent;
            const healthReport = document.querySelectorAll('.info-item')[3].querySelector('.value').textContent;
            const breached = document.querySelector('.breached') !== null;

            fetch('/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    password,
                    strength,
                    entropy,
                    crack_time: crackTime,
                    health_report: healthReport,
                    breached
                })
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'password_report.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to generate report');
            });
        });
    }

    // Live password analysis
    const livePasswordInput = document.getElementById('live-password');
    if (livePasswordInput) {
        livePasswordInput.addEventListener('input', function() {
            const password = this.value;
            if (password.length === 0) {
                document.getElementById('live-strength').textContent = '-';
                document.getElementById('live-entropy').textContent = '-';
                document.getElementById('live-health').textContent = '-';
                return;
            }

            fetch('/live-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('live-strength').textContent = data.strength;
                document.getElementById('live-strength').className = 'value strength-' + data.strength.toLowerCase();
                document.getElementById('live-entropy').textContent = data.entropy + ' bits';
                document.getElementById('live-health').textContent = data.health_report;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
