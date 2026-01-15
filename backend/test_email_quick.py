"""
Quick email test script - non-interactive
"""

import sys
sys.path.insert(0, "/Users/davidebotto/aistrategyhub/backend")

from app.services.email_service import (
    send_welcome_email,
    is_email_enabled,
)
from app.services.ms_graph import ms_graph_service

def main():
    print("\n" + "=" * 80)
    print("🔧 QUICK EMAIL CONFIGURATION TEST")
    print("=" * 80)

    # Check configuration
    print(f"\n📧 Email Service Enabled: {is_email_enabled()}")

    if not is_email_enabled():
        print("\n❌ MS Graph NOT configured!")
        return False

    print(f"✅ Sender: {ms_graph_service.sender_name} <{ms_graph_service.sender_email}>")
    print(f"✅ Tenant ID: {ms_graph_service.tenant_id[:20]}...")
    print(f"✅ Client ID: {ms_graph_service.client_id[:20]}...")
    print(f"✅ Client Secret: {ms_graph_service.client_secret[:10]}...")

    print("\n" + "=" * 80)
    print("🧪 TESTING EMAIL SEND")
    print("=" * 80)

    # Test email to a specific address
    test_email = "botto.davide@gmail.com"  # Test email

    print(f"\n📧 Sending test email to: {test_email}")
    print("   Template: welcome.html")
    print("   Subject: Benvenuto su AI Strategy Hub!")

    result = send_welcome_email(
        user_email=test_email,
        user_name="Davide Botto",
        verification_link="https://aistrategyhub.eu/verify-email?token=test123abc",
    )

    if result:
        print(f"\n✅ EMAIL SENT SUCCESSFULLY!")
        print(f"\n📬 Check inbox: {test_email}")
        print("\nIf you don't see it:")
        print("  1. Check SPAM/Junk folder")
        print("  2. Wait 1-2 minutes (email delivery can be delayed)")
        print("  3. Verify Azure AD admin consent was granted")
        return True
    else:
        print(f"\n❌ EMAIL FAILED TO SEND")
        print("\nPossible causes:")
        print("  1. Admin consent not granted in Azure AD")
        print("  2. Invalid credentials")
        print("  3. Mail.Send permission not configured")
        print("  4. Network/firewall issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
