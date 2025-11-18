import resend
import os
from app.config import config
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = Path.joinpath(BASE_DIR,"templates")
    
    
resend.api_key = config.resend

def render_email(title: str, content: str):
      with open(Path.joinpath(TEMPLATES_DIR,"base.html"), "r") as file:
        template = file.read()
      return template.replace('{{title}}', title).replace('{{content}}', content)
      

def send_password_reset_email(email: str, reset_token: str):
  
    reset_url = f"{config.client}/reset-password?token={reset_token}"

    content = """
    <tr>
            <td style="padding: 40px;">
              <h2 style="margin: 0 0 20px 0; color: #3d4f2f; font-size: 24px; font-weight: 600;">Reset Your Password</h2>
              
              <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
                Hi there,
              </p>
              
              <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
                We received a request to reset your password for your TrailStory account. Click the button below to create a new password:
              </p>

              <!-- Button -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                <tr>
                  <td align="center">
                    <a href="{{reset_url}}" style="display: inline-block; padding: 16px 32px; background-color: #e07a3f; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">Reset Password</a>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 20px 0; color: #666; font-size: 14px; line-height: 1.5;">
                Or copy and paste this link into your browser:
              </p>
              
              <p style="margin: 0 0 30px 0; color: #e07a3f; font-size: 14px; word-break: break-all;">
                {{reset_url}}
              </p>

              <p style="margin: 0 0 10px 0; color: #666; font-size: 14px; line-height: 1.5;">
                This link will expire in <strong>1 hour</strong> for security reasons.
              </p>

              <p style="margin: 0 0 30px 0; color: #666; font-size: 14px; line-height: 1.5;">
                If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.
              </p>
              """

    content = content.replace('{{reset_url}}', reset_url)  

    
    html_content = render_email("Passwork reset link", content)

    
    params: resend.Emails.SendParams = {
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Reset Password",
        "html": html_content,
    }
    
    email = resend.Emails.send(params)
    print(email)
    return email

def send_password_changed_email(email: str, username: str):
    
    now = datetime.now()
    date = now.strftime("%B %d, %Y")  # "January 15, 2025"
    time = now.strftime("%I:%M %p")   # "03:45 PM"
    content= """
    <!-- Success Icon -->
          <tr>
            <td style="padding: 40px 40px 20px 40px; text-align: center;">
              <div style="display: inline-block; width: 80px; height: 80px; background-color: #4caf50; border-radius: 50%; position: relative;">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                  <path d="M20 6L9 17L4 12" stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="padding: 0 40px 40px 40px;">
              <h2 style="margin: 0 0 20px 0; color: #3d4f2f; font-size: 24px; font-weight: 600; text-align: center;">Password Changed Successfully</h2>
              
              <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
                Hi {{username}},
              </p>
              
              <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
                Your TrailStory password was successfully changed on <strong>{{date}}</strong> at <strong>{{time}}</strong>.
              </p>

              <p style="margin: 0 0 30px 0; color: #333; font-size: 16px; line-height: 1.5;">
                You can now sign in to your account using your new password.
              </p>

              <!-- Button -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                <tr>
                  <td align="center">
                    <a href="{{login_url}}" style="display: inline-block; padding: 16px 32px; background-color: #e07a3f; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">Sign In to TrailStory</a>
                  </td>
                </tr>
              </table>

              <!-- Security Warning Box -->
              <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 30px 0; border-radius: 4px;">
                <p style="margin: 0 0 10px 0; color: #856404; font-size: 14px; font-weight: 600;">
                  ⚠️ Didn't make this change?
                </p>
                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.5;">
                  If you didn't change your password, please secure your account immediately by contacting us at <a href="mailto:support@trailstory.com" style="color: #e07a3f; text-decoration: none;">support@trailstory.com</a>
                </p>
              </div>

              <!-- Divider -->
              <div style="border-top: 1px solid #e5e5e5; margin: 30px 0;"></div>

              <p style="margin: 0 0 10px 0; color: #666; font-size: 14px; line-height: 1.5;">
                <strong>Security Tips:</strong>
              </p>
              <ul style="margin: 0 0 20px 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.5;">
                <li>Never share your password with anyone</li>
                <li>Use a unique password for TrailStory</li>
                <li>Enable two-factor authentication when available</li>
              </ul>

              <p style="margin: 0; color: #999; font-size: 12px; line-height: 1.5;">
                Need help? Contact us at support@trailstory.com
              </p>
            </td>
          </tr>
          """
    
    content = content.replace("{{username}}", username)
    content = content.replace("{{date}}", date)
    content = content.replace("{{time}}", time)
    content = content.replace("{{login_url}}", f"{config.client}/login")
    
    html_content = render_email("Password Changed Successfully", content)
    
    resend.Emails.send({
        "from": "TrailStory <onboarding@resend.dev>",
        "to": email,
        "subject": "Your TrailStory password was changed",
        "html": html_content
    })
    
def send_welcome_email(email:str, username:str, token:str):
  
  verification_url = f"{config.client}/verify?token={token}"

  content= """
    <!-- Icon -->
<tr>
  <td style="padding: 40px 40px 20px 40px; text-align: center;">
    <div style="display: inline-block; width: 80px; height: 80px; background-color: #e07a3f; border-radius: 50%; position: relative;">
      <svg width="50" height="50" viewBox="0 0 24 24" fill="none" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="#ffffff" stroke-width="2"/>
        <polyline points="9 22 9 12 15 12 15 22" stroke="#ffffff" stroke-width="2"/>
      </svg>
    </div>
  </td>
</tr>

<!-- Content -->
<tr>
  <td style="padding: 0 40px 40px 40px;">
    <h2 style="margin: 0 0 20px 0; color: #3d4f2f; font-size: 24px; font-weight: 600; text-align: center;">
      Welcome to Trailstory!
    </h2>
    
    <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
      Hi {{username}},
    </p>
    
    <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
      You're one step away from documenting your bikepacking adventures. Verify your email to start creating beautiful trip logs.
    </p>

    <!-- Button -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
      <tr>
        <td align="center">
          <a href="{{verification_url}}" style="display: inline-block; padding: 16px 32px; background-color: #e07a3f; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
            Verify Email Address
          </a>
        </td>
      </tr>
    </table>

    <p style="margin: 0 0 20px 0; color: #666; font-size: 14px; line-height: 1.5; text-align: center;">
      This link expires in 24 hours.
    </p>

    <!-- Divider -->

    <p style="margin: 20px 0 0 0; color: #999; font-size: 12px; line-height: 1.5;">
      Need help? Contact us at support@trailstory.com
    </p>
  </td>
</tr>
          """
  
  content = content.replace("{{username}}", username)
  content = content.replace("{{verification_url}}", verification_url)

  html_content = render_email("Welcome to Trailstory", content)
    
  resend.Emails.send({
        "from": "TrailStory <onboarding@resend.dev>",
        "to": email,
        "subject": "Welcome to Trailstory",
        "html": html_content
    })

def send_verify_email(email:str, username:str, token:str = None):
  
  verification_url = f"{config.client}/verify?token={token}"
  
  content= """
    <!-- Icon -->
<tr>
  <td style="padding: 40px 40px 20px 40px; text-align: center;">
    <div style="display: inline-block; width: 80px; height: 80px; background-color: #e07a3f; border-radius: 50%; position: relative;">
      <svg width="50" height="50" viewBox="0 0 24 24" fill="none" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="#ffffff" stroke-width="2"/>
        <polyline points="9 22 9 12 15 12 15 22" stroke="#ffffff" stroke-width="2"/>
      </svg>
    </div>
  </td>
</tr>

<!-- Content -->
<tr>
  <td style="padding: 0 40px 40px 40px;">
    
    <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
      Hi {{username}} ,
    </p>
    
    <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.5;">
     Click the button below to verify your email.
    </p>

    <!-- Button -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
      <tr>
        <td align="center">
          <a href="{{verification_url}}" style="display: inline-block; padding: 16px 32px; background-color: #e07a3f; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
            Verify Email Address
          </a>
        </td>
      </tr>
        <p style="margin: 0 0 20px 0; color: #666; font-size: 14px; line-height: 1.5;">
                Or copy and paste this link into your browser:
        </p>
              
        <p style="margin: 0 0 30px 0; color: #e07a3f; font-size: 14px; word-break: break-all;">
          {{reset_url}}
        </p>
    </table>

    <p style="margin: 0 0 20px 0; color: #666; font-size: 14px; line-height: 1.5; text-align: center;">
      This link expires in 24 hours.
    </p>

    <!-- Divider -->

    <p style="margin: 20px 0 0 0; color: #999; font-size: 12px; line-height: 1.5;">
      Need help? Contact us at support@trailstory.com
    </p>
  </td>
</tr>
          """
  
  content = content.replace("{{username}}", username)
  content = content.replace("{{verification_url}}", verification_url)
  
  html_content = render_email("Confirm your Trailstory account", content)
    
  resend.Emails.send({
        "from": "TrailStory <onboarding@resend.dev>",
        "to": email,
        "subject": "Welcome to Trailstory",
        "html": html_content
    })