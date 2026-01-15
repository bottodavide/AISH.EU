"""
Script di test per Invoice API
Testa creazione, PDF, XML, e gestione fatture elettroniche italiane
"""

import requests
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"


def test_login(email, password):
    """Login e ottieni JWT token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    print(f"\n🔑 LOGIN - {email}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Token ottenuto")
        return data["access_token"]
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_create_order(token):
    """Crea ordine di test (prerequisito per fattura)"""
    headers = {"Authorization": f"Bearer {token}"}

    # Prima ottieni un service_id
    services_response = requests.get(f"{BASE_URL}/services", headers=headers)
    if services_response.status_code != 200:
        print(f"❌ Error getting services: {services_response.text}")
        return None

    services = services_response.json()
    if not services:
        print("❌ No services found")
        return None

    service_id = services[0]["id"]

    # Crea ordine
    order_data = {
        "items": [{
            "service_id": service_id,
            "quantity": 1,
            "custom_price": 1500.00
        }],
        "notes": "Ordine di test per fatturazione"
    }

    response = requests.post(
        f"{BASE_URL}/orders",
        json=order_data,
        headers=headers
    )

    print(f"\n📦 CREATE ORDER")
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        order = response.json()
        print(f"✅ Order creato: {order['order_number']}")
        print(f"   Total: €{order['total']}")
        return order['id']
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_simulate_payment(token, order_id):
    """Simula pagamento ordine (per testing)"""
    headers = {"Authorization": f"Bearer {token}"}

    # In produzione questo sarebbe gestito da Stripe webhook
    # Per testing, dobbiamo manualmente creare un Payment con status COMPLETED

    # NOTA: Questo endpoint non esiste, quindi creeremo il payment direttamente nel DB
    # Per ora skippiamo e assumiamo che l'ordine sia già pagato
    print(f"\n💳 SIMULATE PAYMENT")
    print(f"⚠️  WARNING: Payment simulation not implemented")
    print(f"   In test environment, manually set Payment.status = COMPLETED in DB")
    print(f"   Or use Stripe test webhook to complete payment")
    return False


def test_create_invoice(token, order_id):
    """Crea fattura da ordine pagato"""
    headers = {"Authorization": f"Bearer {token}"}

    invoice_data = {
        "order_id": order_id,
        "issue_date": date.today().isoformat(),
        "due_date": None,
    }

    response = requests.post(
        f"{BASE_URL}/invoices",
        json=invoice_data,
        headers=headers
    )

    print(f"\n🧾 CREATE INVOICE")
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        invoice = response.json()
        print(f"✅ Invoice creata:")
        print(f"   Numero: {invoice['invoice_number']}")
        print(f"   Status: {invoice['status']}")
        print(f"   Cedente: {invoice['seller_name']}")
        print(f"   Cessionario: {invoice['buyer_name']}")
        print(f"   Subtotal: €{invoice['subtotal']}")
        print(f"   IVA: €{invoice['tax_amount']}")
        print(f"   Total: €{invoice['total']}")
        print(f"   Righe: {len(invoice['lines'])}")
        return invoice['id']
    else:
        print(f"❌ Error: {response.text}")
        if response.status_code == 400:
            print(f"   💡 Hint: Order deve essere pagato (Payment.status = COMPLETED)")
        return None


def test_list_invoices(token):
    """Lista fatture con filtri"""
    headers = {"Authorization": f"Bearer {token}"}

    # Lista tutte
    response = requests.get(
        f"{BASE_URL}/invoices",
        headers=headers
    )

    print(f"\n📋 LIST INVOICES")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        invoices = response.json()
        print(f"✅ Trovate {len(invoices)} fatture:")
        for inv in invoices:
            print(f"   - {inv['invoice_number']} | {inv['buyer_name']} | €{inv['total']} | {inv['status']}")
        return invoices
    else:
        print(f"❌ Error: {response.text}")
        return []


def test_get_invoice(token, invoice_id):
    """Ottiene dettaglio fattura"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/invoices/{invoice_id}",
        headers=headers
    )

    print(f"\n📝 GET INVOICE DETAIL")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        invoice = response.json()
        print(f"✅ Invoice {invoice['invoice_number']}:")
        print(f"   Status: {invoice['status']}")
        print(f"   SDI Status: {invoice['sdi_status']}")
        print(f"   Righe: {len(invoice['lines'])}")
        for line in invoice['lines']:
            print(f"      {line['line_number']}. {line['description'][:50]} - €{line['total']}")
        return invoice
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_generate_pdf(token, invoice_id):
    """Genera PDF fattura"""
    headers = {"Authorization": f"Bearer {token}"}

    request_data = {
        "include_payment_info": True,
        "include_qr_code": False,
        "language": "it"
    }

    response = requests.post(
        f"{BASE_URL}/invoices/{invoice_id}/generate-pdf",
        json=request_data,
        headers=headers
    )

    print(f"\n📄 GENERATE PDF")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        invoice = response.json()
        print(f"✅ PDF generato:")
        print(f"   Status: {invoice['status']}")
        print(f"   PDF File ID: {invoice['pdf_file_id']}")
        if invoice.get('pdf_url'):
            print(f"   PDF URL: {invoice['pdf_url']}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_generate_xml(token, invoice_id):
    """Genera XML FatturaPA"""
    headers = {"Authorization": f"Bearer {token}"}

    request_data = {
        "transmission_format": "FPR12",
        "validate_xsd": False
    }

    response = requests.post(
        f"{BASE_URL}/invoices/{invoice_id}/generate-xml",
        json=request_data,
        headers=headers
    )

    print(f"\n📑 GENERATE XML PA")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        invoice = response.json()
        print(f"✅ XML generato:")
        print(f"   Status: {invoice['status']}")
        print(f"   XML File ID: {invoice['xml_file_id']}")
        if invoice.get('xml_url'):
            print(f"   XML URL: {invoice['xml_url']}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_send_sdi(token, invoice_id):
    """Invia fattura a SDI (STUB)"""
    headers = {"Authorization": f"Bearer {token}"}

    request_data = {
        "send_copy_to_buyer": True,
        "buyer_pec_override": None
    }

    response = requests.post(
        f"{BASE_URL}/invoices/{invoice_id}/send-sdi",
        json=request_data,
        headers=headers
    )

    print(f"\n📧 SEND TO SDI (STUB)")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        invoice = response.json()
        print(f"✅ Fattura inviata (stub):")
        print(f"   Status: {invoice['status']}")
        print(f"   SDI Status: {invoice['sdi_status']}")
        print(f"   SDI Sent At: {invoice.get('sdi_sent_at')}")
        print(f"   ⚠️  NOTA: PEC sending non implementato, solo simulazione")
        return True
    else:
        print(f"❌ Error: {response.text}")
        # Expected: 403 Forbidden se non admin
        if response.status_code == 403:
            print(f"   💡 Hint: Endpoint richiede permessi admin")
        return False


def test_update_invoice_status(token, invoice_id):
    """Aggiorna status fattura (Admin only)"""
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {
        "status": "accepted",
        "sdi_status": "rc",
        "sdi_rejection_reason": None
    }

    response = requests.patch(
        f"{BASE_URL}/invoices/{invoice_id}",
        json=update_data,
        headers=headers
    )

    print(f"\n✏️  UPDATE INVOICE STATUS")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        invoice = response.json()
        print(f"✅ Invoice aggiornata:")
        print(f"   Status: {invoice['status']}")
        print(f"   SDI Status: {invoice['sdi_status']}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        # Expected: 403 Forbidden se non admin
        if response.status_code == 403:
            print(f"   💡 Hint: Endpoint richiede permessi admin")
        return False


def test_invoice_filters(token):
    """Testa filtri lista fatture"""
    headers = {"Authorization": f"Bearer {token}"}

    # Test filtro per anno
    response = requests.get(
        f"{BASE_URL}/invoices?year=2026&page=1&page_size=10",
        headers=headers
    )

    print(f"\n🔍 TEST FILTERS (year=2026)")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        invoices = response.json()
        print(f"✅ Trovate {len(invoices)} fatture per anno 2026")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def main():
    """Main test flow"""
    print("=" * 80)
    print("🧪 TESTING INVOICE API")
    print("=" * 80)

    # 1. Login come cliente
    token = test_login("mario.verdi@azienda.it", "Test123!")
    if not token:
        print("❌ Login failed, aborting tests")
        return

    # 2. Crea ordine
    order_id = test_create_order(token)
    if not order_id:
        print("❌ Order creation failed, aborting tests")
        return

    # 3. Simula pagamento
    # NOTA: In produzione questo avviene via Stripe webhook
    print(f"\n⚠️  MANUAL STEP REQUIRED:")
    print(f"   Per completare il test, devi manualmente:")
    print(f"   1. Aprire il database")
    print(f"   2. Creare un record Payment per order_id={order_id}")
    print(f"   3. Impostare Payment.status = 'COMPLETED'")
    print(f"   4. Rilanciare il test dalla creazione fattura")
    print(f"\n   Oppure usare Stripe test webhook per completare pagamento")
    print(f"\n   Per ora procediamo con i test che non richiedono ordine pagato...")

    # 4. Lista fatture esistenti
    test_list_invoices(token)

    # 5. Test filtri
    test_invoice_filters(token)

    # 6. Tenta creazione fattura (fallirà se order non pagato)
    print(f"\n⚠️  Il test seguente fallirà se l'ordine non è stato pagato:")
    invoice_id = test_create_invoice(token, order_id)

    if invoice_id:
        # 7. Dettaglio fattura
        test_get_invoice(token, invoice_id)

        # 8. Genera PDF
        test_generate_pdf(token, invoice_id)

        # 9. Genera XML
        test_generate_xml(token, invoice_id)

        # 10. Lista fatture aggiornata
        test_list_invoices(token)

        # 11. Invia SDI (richiede admin)
        test_send_sdi(token, invoice_id)

        # 12. Update status (richiede admin)
        test_update_invoice_status(token, invoice_id)

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETATO")
    print("=" * 80)
    print(f"\nNote:")
    print(f"- Alcuni test falliscono se ordine non pagato (expected)")
    print(f"- Alcuni endpoint richiedono permessi admin (expected 403)")
    print(f"- PDF/XML vengono salvati in uploads/invoices/YYYY/MM/")
    print(f"- File tracciati in files table con category=INVOICE")
    print(f"- SDI sending è stub (PEC non implementato)")
    print(f"\nPer test completo:")
    print(f"1. Crea ordine via API")
    print(f"2. Completa pagamento via Stripe webhook (o manual DB)")
    print(f"3. Crea fattura via POST /invoices")
    print(f"4. Genera PDF e XML")
    print(f"5. (TODO) Invia a SDI via PEC")


if __name__ == "__main__":
    main()
