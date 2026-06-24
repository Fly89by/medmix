import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("medmix.notifications")


async def send_email_notification(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> bool:
    """Send email notification. Falls back to logging if SMTP not configured."""
    if not settings.smtp_host or not settings.smtp_from_email:
        logger.info(f"[EMAIL SIMULATION] To: {to_email} | Subject: {subject} | Body: {body[:100]}...")
        return True

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email

        msg.attach(MIMEText(body, "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, [to_email], msg.as_string())

        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.warning(f"Failed to send email to {to_email}: {e}")
        return False


async def notify_quote_created(
    quote_number: str,
    customer_name: str,
    customer_email: Optional[str],
    total_price: float,
    product: str,
):
    """Send notification when a quote is created."""
    if not customer_email:
        return

    subject = f"عرض سعر جديد {quote_number} - MED.MIX OS"
    body = f"""
عزيزي {customer_name}،

نشكرك على ثقتك بنا. يسرنا إرفاق عرض السعر الخاص بك:

رقم العرض: {quote_number}
المنتج: {product}
الإجمالي: {total_price:,.2f} ر.س

يمكنك التواصل معنا لأي استفسار.

مع تحيات،
فريق MED.MIX OS
"""
    html_body = f"""
<div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <div style="background: linear-gradient(135deg, #1e3a5f, #2563eb); padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
    <h1 style="color: white; margin: 0; font-size: 20px;">MED.MIX OS</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">عرض سعر جديد</p>
  </div>
  <div style="background: #f8fafc; padding: 24px; border: 1px solid #e2e8f0; border-radius: 0 0 12px 12px;">
    <p>عزيزي <strong>{customer_name}</strong>،</p>
    <p>نشكرك على ثقتك بنا. يسرنا إرفاق عرض السعر الخاص بك:</p>
    <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">رقم العرض</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">{quote_number}</td></tr>
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">المنتج</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{product}</td></tr>
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">الإجمالي</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #2563eb;">{total_price:,.2f} ر.س</td></tr>
    </table>
    <p style="color: #64748b; font-size: 12px;">يمكنك التواصل معنا لأي استفسار.</p>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 16px 0;" />
    <p style="color: #94a3b8; font-size: 11px; text-align: center;">MED.MIX OS © {__import__('datetime').datetime.now().year}</p>
  </div>
</div>
"""

    await send_email_notification(customer_email, subject, body, html_body)
