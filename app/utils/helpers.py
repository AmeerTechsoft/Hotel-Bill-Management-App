import smtplib

def send_email(email, username, password):
    # Replace the following with your email provider's SMTP server details
    smtp_server = 'smtp.your-email-provider.com'
    smtp_port = 587
    sender_email = 'your-email@example.com'
    sender_password = 'your-email-password'

    subject = 'Your Login Credentials'
    body = f'Here is your login details to login to the hotel bill management system.\nUsername: {username}\nPassword: {password}'

    message = f'Subject: {subject}\n\n{body}'

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
