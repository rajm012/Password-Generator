document.addEventListener('DOMContentLoaded', function () {
    
        // Dark mode toggle
        const darkModeToggle = document.getElementById('dark-mode-toggle');
        const body = document.body;
        
        // Check for saved user preference or use system preference
        if (localStorage.getItem('darkMode') === 'enabled' || 
            (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            body.classList.add('dark-mode');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i><span>Light Mode</span>';
        }
        
        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            
            if (body.classList.contains('dark-mode')) {
                darkModeToggle.innerHTML = '<i class="fas fa-sun"></i><span>Light Mode</span>';
                localStorage.setItem('darkMode', 'enabled');
            } else {
                darkModeToggle.innerHTML = '<i class="fas fa-moon"></i><span>Dark Mode</span>';
                localStorage.setItem('darkMode', 'disabled');
            }
        });
    // Initialize form fields based on password type
    const passwordTypeRadios = document.querySelectorAll('input[name="password_type"]');
    if (passwordTypeRadios.length > 0) {
        const initialType = document.querySelector('input[name="password_type"]:checked')?.value || "password";
        updateFormFields(initialType);

        passwordTypeRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                updateFormFields(this.value);
            });
        });
    }

    function updateFormFields(type) {
        console.log(`Updating form for type: ${type}`);
        const lengthLabel = document.getElementById('length-label');
        const lengthInput = document.getElementById('length');
        const digitsCheckbox = document.getElementById('use_digits');
        const symbolsCheckbox = document.getElementById('use_symbols');

        if (type === 'passphrase') {
            lengthLabel.textContent = 'Number of Words (3-6)';
            lengthInput.min = 3;
            lengthInput.max = 6;
            lengthInput.value = 4;
            digitsCheckbox.disabled = true;
            symbolsCheckbox.disabled = true;
            digitsCheckbox.checked = false;
            symbolsCheckbox.checked = false;
        } else {
            lengthLabel.textContent = 'Password Length (8-64)';
            lengthInput.min = 8;
            lengthInput.max = 64;
            lengthInput.value = 12;
            digitsCheckbox.disabled = false;
            symbolsCheckbox.disabled = false;
        }
    }

    // Generate PDF Report
    const generateReportBtn = document.getElementById('generate-report');
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', () => {
            const password = document.getElementById('password')?.textContent || "";
            const strength = document.querySelector('.strength')?.textContent || "";
            const entropy = document.querySelectorAll('.info-item')[1]?.querySelector('.value')?.textContent || "";
            const crackTime = document.querySelectorAll('.info-item')[2]?.querySelector('.value')?.textContent || "";
            const healthReport = document.querySelectorAll('.info-item')[3]?.querySelector('.value')?.textContent || "";
            const breached = document.querySelector('.breached') !== null;

            fetch('/generate-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    password, 
                    strength, 
                    entropy, 
                    crack_time: crackTime, 
                    health_report: healthReport, 
                    breached 
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error); });
                }
                return response.blob();
            })
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
                alert('Failed to generate report: ' + error.message);
            });
        });
    }

    // Live Password Analysis
    const livePasswordInput = document.getElementById('live-password');
    if (livePasswordInput) {
        livePasswordInput.addEventListener('input', function () {
            const password = this.value;
            if (!password) {
                document.getElementById('live-strength').textContent = '-';
                document.getElementById('live-entropy').textContent = '-';
                document.getElementById('live-health').textContent = '-';
                return;
            }

            fetch('/live-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('live-strength').textContent = data.strength;
                document.getElementById('live-strength').className = 'value strength-' + data.strength.toLowerCase();
                document.getElementById('live-entropy').textContent = data.entropy + ' bits';
                document.getElementById('live-health').textContent = data.health_report;
            })
            .catch(error => console.error('Error:', error));
        });
    }
});
