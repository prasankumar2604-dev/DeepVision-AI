"""
====================================================
DeepVision AI — Secure Email Dispatcher
SMTP Delivery Engine with Luxury HTML Templates
====================================================
"""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_smtp_config() -> dict:
    """Retrieves current SMTP configuration from environment variables."""
    host = os.environ.get("SMTP_HOST", "").strip()
    port_str = os.environ.get("SMTP_PORT", "587").strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 587

    user = os.environ.get("SMTP_USERNAME", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    use_ssl = os.environ.get("SMTP_USE_SSL", "false").lower() in ("true", "1", "yes") or port == 465
    sender = os.environ.get("MAIL_FROM", "").strip() or user or "DeepVision AI <noreply@deepvision.ai>"

    return {
        "host": host,
        "port": port,
        "username": user,
        "password": password,
        "use_tls": use_tls,
        "use_ssl": use_ssl,
        "from_addr": sender,
    }


def is_smtp_configured() -> bool:
    """Returns True if minimum required SMTP settings are populated."""
    cfg = get_smtp_config()
    return bool(cfg["host"] and cfg["username"] and cfg["password"])


def missing_smtp_variables() -> list[str]:
    """Returns a list of missing required SMTP environment variable names."""
    cfg = get_smtp_config()
    missing = []
    if not cfg["host"]:
        missing.append("SMTP_HOST")
    if not cfg["username"]:
        missing.append("SMTP_USERNAME")
    if not cfg["password"]:
        missing.append("SMTP_PASSWORD")
    return missing


def send_email(to_email: str, subject: str, html_body: str, text_body: str) -> tuple[bool, str]:
    """
    Dispatches an email via SMTP.
    If SMTP credentials are not configured, prints the message and security codes
    to the terminal console for local developer testing, and returns status with
    an explanation of missing environment variables.
    """
    cfg = get_smtp_config()

    if not is_smtp_configured():
        missing_vars = ", ".join(missing_smtp_variables())
        print("\n" + "=" * 70)
        print("⚠️  [DeepVision AI Mailer — SMTP Not Configured]")
        print(f"Missing required environment variables: {missing_vars}")
        print("To enable live email delivery, please configure them in your .env file.")
        print("-" * 70)
        print(f"📧 Destination : {to_email}")
        print(f"📌 Subject     : {subject}")
        print("📜 Plain-Text Message:")
        print(text_body.strip())
        print("=" * 70 + "\n")
        return False, f"SMTP credentials not configured (missing: {missing_vars}). Check server console for code in local development."

    # Construct MIME Message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg["from_addr"]
    msg["To"] = to_email

    part_text = MIMEText(text_body, "plain", "utf-8")
    part_html = MIMEText(html_body, "html", "utf-8")
    msg.attach(part_text)
    msg.attach(part_html)

    try:
        if cfg["use_ssl"]:
            server = smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=15)
        else:
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=15)
            if cfg["use_tls"]:
                server.starttls()

        server.login(cfg["username"], cfg["password"])
        server.sendmail(cfg["from_addr"], [to_email], msg.as_string())
        server.quit()

        print(f"✅ [DeepVision AI Mailer] Email sent successfully to {to_email} (Subject: {subject})")
        return True, "Email sent successfully."

    except Exception as exc:
        err_msg = str(exc)
        print(f"❌ [DeepVision AI Mailer Error] Failed sending to {to_email}: {err_msg}")
        return False, f"SMTP delivery failed: {err_msg}"


# ---------------------------------------------------------------------------
# High-End Luxury HTML Email Templates
# ---------------------------------------------------------------------------

def _build_luxury_email_layout(title: str, preheader: str, content_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #111214;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #F3F0E8;
    }}
    .email-container {{
      max-width: 580px;
      margin: 40px auto;
      background: #202124;
      border: 1px solid #3A3A3A;
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
    }}
    .header {{
      background: linear-gradient(135deg, #1A1B1E 0%, #292929 100%);
      border-bottom: 1px solid rgba(201, 164, 92, 0.28);
      padding: 32px 24px;
      text-align: center;
    }}
    .emblem {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: linear-gradient(135deg, #C9A45C 0%, #E6C982 50%, #C9A45C 100%);
      display: inline-block;
      margin-bottom: 12px;
      line-height: 48px;
      font-size: 22px;
      color: #111214;
      font-weight: bold;
    }}
    .brand-title {{
      font-size: 22px;
      font-weight: 700;
      color: #F3F0E8;
      margin: 0;
      letter-spacing: -0.02em;
    }}
    .brand-title span {{
      color: #E6C982;
    }}
    .brand-sub {{
      font-size: 12px;
      color: #B6B6B6;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-top: 4px;
    }}
    .content {{
      padding: 36px 32px;
      font-size: 15px;
      line-height: 1.6;
      color: #B6B6B6;
    }}
    .content h2 {{
      color: #F3F0E8;
      font-size: 20px;
      margin-top: 0;
      margin-bottom: 16px;
    }}
    .otp-box {{
      background: #17181A;
      border: 1px solid rgba(201, 164, 92, 0.4);
      border-radius: 14px;
      padding: 22px;
      text-align: center;
      margin: 28px 0;
      box-shadow: 0 0 24px rgba(201, 164, 92, 0.08);
    }}
    .otp-code {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 38px;
      letter-spacing: 0.25em;
      font-weight: 800;
      color: #E6C982;
      display: block;
      margin-left: 0.25em;
    }}
    .otp-sub {{
      font-size: 12px;
      color: #858585;
      margin-top: 8px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .action-btn {{
      display: inline-block;
      background: linear-gradient(135deg, #C9A45C 0%, #E6C982 50%, #C9A45C 100%);
      color: #111214 !important;
      text-decoration: none;
      font-weight: 700;
      font-size: 15px;
      padding: 14px 32px;
      border-radius: 10px;
      margin: 20px 0;
      text-align: center;
    }}
    .security-notice {{
      background: #191A1D;
      border-left: 3px solid #E6C982;
      padding: 12px 16px;
      border-radius: 0 8px 8px 0;
      font-size: 13px;
      color: #858585;
      margin-top: 24px;
    }}
    .footer {{
      border-top: 1px solid #2A2B2E;
      padding: 20px 24px;
      text-align: center;
      font-size: 12px;
      color: #858585;
      background: #191A1D;
    }}
  </style>
</head>
<body>
  <div style="display:none;font-size:1px;color:#111214;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
    {preheader}
  </div>
  <div class="email-container">
    <div class="header">
      <div class="emblem">DV</div>
      <h1 class="brand-title">DeepVision <span>AI</span></h1>
      <div class="brand-sub">Neural Image Forensics Platform</div>
    </div>
    <div class="content">
      {content_html}
    </div>
    <div class="footer">
      DeepVision AI &bull; Neural Forensics Security Team<br>
      This is an automated system notification. Please do not reply directly to this email.
    </div>
  </div>
</body>
</html>"""


def send_signup_otp_email(to_email: str, otp: str) -> tuple[bool, str]:
    """Sends account activation verification OTP email."""
    subject = f"{otp} is your DeepVision AI verification code"
    preheader = f"Verify your email address with one-time code {otp}."

    content_html = f"""
      <h2>Verify Your Email Address</h2>
      <p>Thank you for signing up for <strong>DeepVision AI</strong>. To complete your account activation and confirm your email ownership, enter the verification code below:</p>
      
      <div class="otp-box">
        <span class="otp-code">{otp}</span>
        <div class="otp-sub">One-Time Verification Code (Valid for 5 minutes)</div>
      </div>
      
      <div class="security-notice">
        <strong>Security Notice:</strong> This code is valid for <strong>5 minutes</strong> and allows a maximum of 5 attempts. Never share this code with anyone. DeepVision AI staff will never ask for your code.
      </div>
    """

    text_body = f"""DeepVision AI — Email Verification

Your one-time email verification code is: {otp}

This code expires in 5 minutes.
Enter this code in the DeepVision AI verification screen to activate your account.

If you did not request this account registration, please ignore this email.
"""

    return send_email(to_email, subject, _build_luxury_email_layout("DeepVision AI — Verify Email", preheader, content_html), text_body)


def send_login_otp_email(to_email: str, otp: str) -> tuple[bool, str]:
    """Sends two-factor login verification OTP email."""
    subject = f"{otp} is your DeepVision AI login authorization code"
    preheader = f"Authorize your DeepVision AI sign-in with 2FA code {otp}."

    content_html = f"""
      <h2>Two-Factor Sign-In Authorization</h2>
      <p>A sign-in attempt was initiated for your <strong>DeepVision AI</strong> account. To complete authentication, please enter the one-time authorization code below:</p>
      
      <div class="otp-box">
        <span class="otp-code">{otp}</span>
        <div class="otp-sub">Login Authorization Code (Valid for 5 minutes)</div>
      </div>
      
      <div class="security-notice">
        <strong>Security Notice:</strong> If you did not initiate this login attempt, someone may know your password. We strongly advise resetting your password immediately after checking your account activity.
      </div>
    """

    text_body = f"""DeepVision AI — Two-Factor Login Authorization

Your one-time sign-in authorization code is: {otp}

This code expires in 5 minutes and is single-use.
If you did not attempt to sign in, please secure your account immediately.
"""

    return send_email(to_email, subject, _build_luxury_email_layout("DeepVision AI — Sign-In Authorization", preheader, content_html), text_body)


def send_password_reset_email(to_email: str, reset_url: str) -> tuple[bool, str]:
    """Sends secure password reset link email."""
    subject = "DeepVision AI — Password Reset Request"
    preheader = "Instructions for resetting your DeepVision AI account password."

    content_html = f"""
      <h2>Password Reset Request</h2>
      <p>We received a request to reset the password for your <strong>DeepVision AI</strong> account. Click the button below to choose a new, strong password:</p>
      
      <div style="text-align: center; margin: 30px 0;">
        <a href="{reset_url}" class="action-btn" target="_blank" rel="noopener noreferrer">Reset Your Password</a>
      </div>
      
      <p style="font-size: 13px; color: #858585;">
        Alternatively, copy and paste this link into your browser:<br>
        <a href="{reset_url}" style="color: #E6C982; word-break: break-all;">{reset_url}</a>
      </p>
      
      <div class="security-notice">
        <strong>Important:</strong> This password reset link is valid for <strong>15 minutes</strong> and can only be used once. If you did not request a password reset, you can safely ignore this email.
      </div>
    """

    text_body = f"""DeepVision AI — Password Reset Request

We received a request to reset the password for your DeepVision AI account.
To set a new password, open the link below in your browser:

{reset_url}

This link is valid for 15 minutes and can only be used once.
If you did not request a password reset, you can safely ignore this email.
"""

    return send_email(to_email, subject, _build_luxury_email_layout("DeepVision AI — Password Reset", preheader, content_html), text_body)
