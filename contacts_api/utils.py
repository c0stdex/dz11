def send_verification_email(email: str, token: str):
    verification_url = f"http://localhost:8000/verify-email?token={token}"
    print(f"Send this link to {email}: {verification_url}")

def send_reset_password_email(email: str, token: str):
    reset_url = f"http://localhost:8000/reset-password/confirm?token={token}"
    print(f"Send this link to {email}: {reset_url}")
