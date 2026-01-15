"""
Script di test per Email Service con MS Graph API
Testa invio email con templates Jinja2
"""

import sys
from datetime import datetime

# Aggiungi backend al path
sys.path.insert(0, "/Users/davidebotto/aistrategyhub/backend")

from app.services.email_service import (
    send_welcome_email,
    send_email_verification,
    send_password_reset_email,
    send_order_confirmation_email,
    send_invoice_ready_email,
    is_email_enabled,
    get_available_templates,
)

from app.services.ms_graph import ms_graph_service


def test_email_configuration():
    """Verifica configurazione email"""
    print("\n" + "=" * 80)
    print("🔧 EMAIL CONFIGURATION CHECK")
    print("=" * 80)

    enabled = is_email_enabled()
    print(f"\n📧 Email Service: {'✅ ENABLED' if enabled else '❌ DISABLED'}")

    if not enabled:
        print("\n⚠️  MS Graph NOT configured!")
        print("\nPer abilitare email, configura nel file .env:")
        print("  MS_GRAPH_TENANT_ID=<your-tenant-id>")
        print("  MS_GRAPH_CLIENT_ID=<your-client-id>")
        print("  MS_GRAPH_CLIENT_SECRET=<your-client-secret>")
        print("  MS_GRAPH_SENDER_EMAIL=noreply@aistrategyhub.eu")
        print("\nSetup Azure AD:")
        print("  1. Vai su https://portal.azure.com")
        print("  2. Azure Active Directory > App registrations > New registration")
        print("  3. Ottieni Tenant ID, Client ID")
        print("  4. Certificates & secrets > New client secret")
        print("  5. API permissions > Add: Mail.Send (Application)")
        print("  6. Grant admin consent")
        return False

    print(f"\n✅ Sender: {ms_graph_service.sender_name} <{ms_graph_service.sender_email}>")
    print(f"✅ Tenant ID: {ms_graph_service.tenant_id[:8]}...")
    print(f"✅ Client ID: {ms_graph_service.client_id[:8]}...")

    # Template disponibili
    templates = get_available_templates()
    print(f"\n📄 Available Templates ({len(templates)}):")
    for tmpl in templates:
        print(f"   - {tmpl}")

    return True


def test_welcome_email(recipient_email: str):
    """Test email di benvenuto"""
    print("\n" + "=" * 80)
    print("📧 TEST: Welcome Email")
    print("=" * 80)

    result = send_welcome_email(
        user_email=recipient_email,
        user_name="Mario Rossi",
        verification_link="https://aistrategyhub.eu/verify-email?token=abc123def456",
    )

    if result:
        print(f"\n✅ Welcome email SENT to {recipient_email}")
    else:
        print(f"\n❌ Welcome email FAILED to send to {recipient_email}")

    return result


def test_verification_email(recipient_email: str):
    """Test email verifica"""
    print("\n" + "=" * 80)
    print("📧 TEST: Email Verification")
    print("=" * 80)

    result = send_email_verification(
        user_email=recipient_email,
        user_name="Mario Rossi",
        verification_link="https://aistrategyhub.eu/verify-email?token=xyz789ghi012",
    )

    if result:
        print(f"\n✅ Verification email SENT to {recipient_email}")
    else:
        print(f"\n❌ Verification email FAILED to send to {recipient_email}")

    return result


def test_password_reset_email(recipient_email: str):
    """Test email reset password"""
    print("\n" + "=" * 80)
    print("📧 TEST: Password Reset")
    print("=" * 80)

    result = send_password_reset_email(
        user_email=recipient_email,
        user_name="Mario Rossi",
        reset_link="https://aistrategyhub.eu/reset-password?token=reset123token456",
    )

    if result:
        print(f"\n✅ Password reset email SENT to {recipient_email}")
    else:
        print(f"\n❌ Password reset email FAILED to send to {recipient_email}")

    return result


def test_order_confirmation_email(recipient_email: str):
    """Test email conferma ordine"""
    print("\n" + "=" * 80)
    print("📧 TEST: Order Confirmation")
    print("=" * 80)

    order_items = [
        {
            "description": "Consulenza AI Act Compliance (pacchetto completo)",
            "quantity": 1,
            "total": "2500.00",
        },
        {
            "description": "Toolkit AI Strategy (download immediato)",
            "quantity": 1,
            "total": "497.00",
        },
    ]

    result = send_order_confirmation_email(
        user_email=recipient_email,
        user_name="Mario Rossi",
        order_number="ORD-2026-00042",
        order_date=datetime.now().strftime("%d/%m/%Y"),
        order_items=order_items,
        order_subtotal="2997.00",
        order_tax="659.34",
        order_total="3656.34",
        order_url="https://aistrategyhub.eu/orders/ORD-2026-00042",
        dashboard_url="https://aistrategyhub.eu/dashboard",
    )

    if result:
        print(f"\n✅ Order confirmation email SENT to {recipient_email}")
    else:
        print(f"\n❌ Order confirmation email FAILED to send to {recipient_email}")

    return result


def test_invoice_ready_email(recipient_email: str):
    """Test email fattura disponibile"""
    print("\n" + "=" * 80)
    print("📧 TEST: Invoice Ready")
    print("=" * 80)

    result = send_invoice_ready_email(
        user_email=recipient_email,
        user_name="Mario Rossi",
        invoice_number="2026/00015",
        invoice_date=datetime.now().strftime("%d/%m/%Y"),
        invoice_subtotal="2997.00",
        invoice_tax="659.34",
        invoice_total="3656.34",
        invoice_pdf_url="https://aistrategyhub.eu/api/v1/invoices/uuid-123/download",
        dashboard_url="https://aistrategyhub.eu/dashboard/invoices",
        has_pec=True,
    )

    if result:
        print(f"\n✅ Invoice ready email SENT to {recipient_email}")
    else:
        print(f"\n❌ Invoice ready email FAILED to send to {recipient_email}")

    return result


def main():
    """Main test flow"""
    print("\n" + "=" * 80)
    print("🧪 EMAIL SERVICE TEST SUITE")
    print("=" * 80)

    # 1. Verifica configurazione
    if not test_email_configuration():
        print("\n❌ Email service not configured - aborting tests")
        return

    # 2. Chiedi email di test
    print("\n" + "=" * 80)
    print("📬 Enter test recipient email")
    print("=" * 80)
    recipient = input("\nEmail address: ").strip()

    if not recipient or "@" not in recipient:
        print("❌ Invalid email address")
        return

    print(f"\n✅ Using recipient: {recipient}")
    print("\n⚠️  ATTENZIONE: Verrai inviate email reali a questo indirizzo!")
    confirm = input("\nProcedere? (y/n): ").strip().lower()

    if confirm != "y":
        print("\n❌ Test aborted by user")
        return

    # 3. Run tests
    results = {}

    results["welcome"] = test_welcome_email(recipient)
    results["verification"] = test_verification_email(recipient)
    results["password_reset"] = test_password_reset_email(recipient)
    results["order_confirmation"] = test_order_confirmation_email(recipient)
    results["invoice_ready"] = test_invoice_ready_email(recipient)

    # 4. Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    print("\nResults by template:")
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")

    if passed == total:
        print("\n🎉 All tests PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED")

    print("\n" + "=" * 80)
    print("💡 NEXT STEPS")
    print("=" * 80)
    print("\n1. Controlla la casella email del destinatario")
    print("2. Verifica che le email siano ben formattate")
    print("3. Testa i link nei template (non funzioneranno - sono placeholders)")
    print("4. Integra email service negli endpoint API:")
    print("   - POST /auth/register → send_welcome_email()")
    print("   - POST /auth/request-password-reset → send_password_reset_email()")
    print("   - POST /orders (after payment) → send_order_confirmation_email()")
    print("   - POST /invoices/{id}/generate-pdf → send_invoice_ready_email()")


if __name__ == "__main__":
    main()
