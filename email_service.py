from pybreaker import CircuitBreaker
from tenacity import retry, wait_exponential, stop_after_attempt
import smtplib
import os

EMAIL_CB = CircuitBreaker(fail_max=5, reset_timeout=20)

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
@EMAIL_CB
def send_email(to: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")

    if not smtp_host:
        print(f"[email] to={to}, subject={subject}, body={body}")
        return True

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        message = f"Subject: {subject}\n\n{body}"
        smtp.sendmail(username, to, message)
    return True