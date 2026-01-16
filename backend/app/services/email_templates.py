"""
Email Templates
Descrizione: Template HTML per le email transazionali e newsletter
Autore: Claude per Davide
Data: 2026-01-16
"""

from typing import Optional
from datetime import datetime


def blog_post_newsletter_template(
    post_title: str,
    post_excerpt: str,
    post_content: str,
    post_url: str,
    author_name: str,
    category_name: Optional[str] = None,
    featured_image: Optional[str] = None,
    published_at: Optional[datetime] = None,
) -> tuple[str, str]:
    """
    Template email per newsletter articolo blog

    Returns:
        tuple[str, str]: (html_body, plain_text_body)
    """

    # Formatta data pubblicazione
    date_str = ""
    if published_at:
        date_str = published_at.strftime("%d %B %Y")

    # Limita excerpt a 200 caratteri
    excerpt_short = post_excerpt[:200] + "..." if len(post_excerpt) > 200 else post_excerpt

    # HTML Email
    html_body = f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">
                                AI Strategy Hub
                            </h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 14px; opacity: 0.9;">
                                Insights su AI, Privacy e Cybersecurity
                            </p>
                        </td>
                    </tr>

                    <!-- Featured Image -->
                    {f'''
                    <tr>
                        <td style="padding: 0;">
                            <img src="{featured_image}" alt="{post_title}" style="width: 100%; height: auto; display: block; max-height: 300px; object-fit: cover;">
                        </td>
                    </tr>
                    ''' if featured_image else ''}

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <!-- Meta info -->
                            <div style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #e5e7eb;">
                                {f'<span style="display: inline-block; background-color: #667eea; color: #ffffff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-right: 10px;">{category_name}</span>' if category_name else ''}
                                {f'<span style="color: #6b7280; font-size: 14px;">{date_str}</span>' if date_str else ''}
                                <span style="color: #6b7280; font-size: 14px; margin-left: 10px;">di {author_name}</span>
                            </div>

                            <!-- Title -->
                            <h2 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; line-height: 1.3;">
                                {post_title}
                            </h2>

                            <!-- Excerpt -->
                            <p style="margin: 0 0 30px 0; color: #6b7280; font-size: 16px; line-height: 1.6;">
                                {excerpt_short}
                            </p>

                            <!-- CTA Button -->
                            <table cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="center" style="border-radius: 6px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                                        <a href="{post_url}" style="display: inline-block; padding: 14px 32px; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 16px;">
                                            Leggi l'articolo completo →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 15px 0; color: #6b7280; font-size: 14px; text-align: center;">
                                Ricevi questa email perché sei iscritto alla newsletter di AI Strategy Hub
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px; text-align: center;">
                                <a href="https://aistrategyhub.eu/newsletter/unsubscribe" style="color: #667eea; text-decoration: none;">Disiscriviti</a> ·
                                <a href="https://aistrategyhub.eu" style="color: #667eea; text-decoration: none;">Visita il sito</a> ·
                                <a href="https://aistrategyhub.eu/privacy" style="color: #667eea; text-decoration: none;">Privacy Policy</a>
                            </p>
                            <p style="margin: 20px 0 0 0; color: #9ca3af; font-size: 12px; text-align: center;">
                                © {datetime.now().year} AI Strategy Hub. Tutti i diritti riservati.
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    # Plain text fallback
    plain_text_body = f"""
{post_title}
{'-' * len(post_title)}

{category_name if category_name else ''} · {date_str if date_str else ''} · di {author_name}

{excerpt_short}

Leggi l'articolo completo: {post_url}

---

Ricevi questa email perché sei iscritto alla newsletter di AI Strategy Hub
Disiscriviti: https://aistrategyhub.eu/newsletter/unsubscribe
Visita il sito: https://aistrategyhub.eu

© {datetime.now().year} AI Strategy Hub. Tutti i diritti riservati.
"""

    return html_body, plain_text_body


def newsletter_test_template(subscriber_email: str) -> tuple[str, str]:
    """
    Template di test per verificare l'invio newsletter

    Returns:
        tuple[str, str]: (html_body, plain_text_body)
    """

    html_body = f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Newsletter</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; padding: 40px;">
                    <tr>
                        <td>
                            <h1 style="color: #333; margin-bottom: 20px;">Test Newsletter</h1>
                            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                                Ciao!<br><br>
                                Questo è un test per verificare che il sistema di invio newsletter funzioni correttamente.<br><br>
                                Email destinatario: <strong>{subscriber_email}</strong><br><br>
                                Se ricevi questa email, significa che il sistema funziona! 🎉
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    plain_text_body = f"""
Test Newsletter

Ciao!

Questo è un test per verificare che il sistema di invio newsletter funzioni correttamente.

Email destinatario: {subscriber_email}

Se ricevi questa email, significa che il sistema funziona!

---
AI Strategy Hub
"""

    return html_body, plain_text_body
