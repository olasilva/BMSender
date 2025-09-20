import os
import re
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-secret-key'

# Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAX_EMAILS'] = int(os.environ.get('MAX_EMAILS', 500))

mail = Mail(app)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_async_email(app, msg, recipient):
    """Send email in background thread"""
    with app.app_context():
        try:
            mail.send(msg)
            app.logger.info(f"Email sent to {recipient}")
        except Exception as e:
            app.logger.error(f"Failed to send email to {recipient}: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()
        recipients_text = request.form.get('recipients', '').strip()
        
        # Validate inputs
        if not subject:
            flash('Email subject is required', 'error')
            return render_template('index.html')
        
        if not body:
            flash('Email body is required', 'error')
            return render_template('index.html')
        
        if not recipients_text:
            flash('Recipient list is required', 'error')
            return render_template('index.html')
        
        # Process recipient list
        recipients = [email.strip() for email in recipients_text.split(',') if email.strip()]
        recipients = [email for email in recipients if is_valid_email(email)]
        
        if not recipients:
            flash('No valid email addresses found', 'error')
            return render_template('index.html')
        
        # Check recipient limit
        if len(recipients) > app.config['MAX_EMAILS']:
            flash(f'Maximum {app.config["MAX_EMAILS"]} emails allowed per batch', 'error')
            return render_template('index.html')
        
        # Remove duplicates
        recipients = list(set(recipients))
        
        # Send emails in background threads
        for recipient in recipients:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=body,
                html=body  # Assuming HTML content is the same as plain text
            )
            thread = Thread(target=send_async_email, args=[app, msg, recipient])
            thread.start()
        
        flash(f'Started sending {len(recipients)} emails', 'success')
        return redirect(url_for('success', count=len(recipients)))
    
    return render_template('index.html')

@app.route('/success')
def success():
    count = request.args.get('count', 0)
    return render_template('success.html', count=count)

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')