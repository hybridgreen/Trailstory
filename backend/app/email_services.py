import resend
import os
from config import config
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
    
    
resend.api_key = config.resend


def send_email(sender: str, receiver: str, subject: str, content: str):
    pass

def send_password_reset_email(email: str, reset_token: str):
    reset_url = f"{config.client}/reset-password?token={reset_token}"
    
    with open(TEMPLATES_DIR+"/reset_email", "r") as file:
        PASSWORD_RESET_TEMPLATE = file.read()
        html_content = PASSWORD_RESET_TEMPLATE.replace("{{reset_url}}", reset_url)
    
    email = resend.Emails.send({
        "from": "TrailStory <noreply@trailstory.com>",
        "to": email,
        "subject": "Reset Your TrailStory Password",
        "html": html_content
    })
    return email

def send_password_changed_email(email: str, username: str):
    
    now = datetime.now()
    date = now.strftime("%B %d, %Y")  # "January 15, 2025"
    time = now.strftime("%I:%M %p")   # "03:45 PM"
    
    with open(TEMPLATES_DIR+"/reset_email", "r") as file:
        PASSWORD_CHANGED_TEMPLATE = file.read()
        html_content = PASSWORD_CHANGED_TEMPLATE.replace("{{username}}", username)
        html_content = html_content.replace("{{date}}", date)
        html_content = html_content.replace("{{time}}", time)
        html_content = html_content.replace("{{login_url}}", f"{config.client}/login")
    
    resend.Emails.send({
        "from": "TrailStory <noreply@trailstory.com>",
        "to": email,
        "subject": "Your TrailStory Password Was Changed",
        "html": html_content
    })