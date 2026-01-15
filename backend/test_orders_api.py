"""
Script di test per Orders API
Testa i principali endpoints degli ordini
"""

import requests
import json

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
        print(f"✅ Token ottenuto: {data['access_token'][:50]}...")
        return data["access_token"]
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_create_quote_request(token, service_id):
    """Test creazione richiesta preventivo"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "service_id": service_id,
        "contact_name": "Mario Verdi",
        "contact_email": "mario.verdi@azienda.it",
        "contact_phone": "+39 333 1234567",
        "company_name": "Verdi S.r.l.",
        "message": "Vorrei un preventivo per implementare AI Act compliance nella mia azienda"
    }

    response = requests.post(
        f"{BASE_URL}/quote-requests",
        json=data,
        headers=headers
    )

    print(f"\n📋 CREATE QUOTE REQUEST")
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        quote = response.json()
        print(f"✅ Quote Request creata: {quote['request_number']}")
        print(f"   Service ID: {quote['service_id']}")
        print(f"   Status: {quote['status']}")
        return quote["id"]
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_list_quote_requests(token):
    """Test lista richieste preventivo"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/quote-requests", headers=headers)

    print(f"\n📜 LIST QUOTE REQUESTS")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        quotes = response.json()
        print(f"✅ Trovate {len(quotes)} richieste")
        for quote in quotes:
            print(f"   - {quote['request_number']}: {quote['status']}")
    else:
        print(f"❌ Error: {response.text}")


def test_create_order(token, service_id):
    """Test creazione ordine"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "items": [
            {
                "service_id": service_id,
                "quantity": 1,
                "custom_price": 1500.00  # Prezzo custom per servizi CUSTOM_QUOTE
            }
        ],
        "notes": "Ordine di test"
    }

    response = requests.post(
        f"{BASE_URL}/orders",
        json=data,
        headers=headers
    )

    print(f"\n🛒 CREATE ORDER")
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        order = response.json()
        print(f"✅ Ordine creato: {order['order_number']}")
        print(f"   Subtotal: €{order['subtotal']}")
        print(f"   IVA (22%): €{order['tax_amount']}")
        print(f"   Total: €{order['total']}")
        print(f"   Items: {len(order['items'])}")
        return order["id"]
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_list_orders(token):
    """Test lista ordini"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/orders", headers=headers)

    print(f"\n📦 LIST ORDERS")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"✅ Trovati {len(orders)} ordini")
        for order in orders:
            print(f"   - {order['order_number']}: €{order['total']} ({order['status']})")
    else:
        print(f"❌ Error: {response.text}")


def test_get_order(token, order_id):
    """Test dettaglio ordine"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)

    print(f"\n📄 GET ORDER DETAIL")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Ordine: {order['order_number']}")
        print(f"   Status: {order['status']}")
        print(f"   Total: €{order['total']}")
        print(f"   Items:")
        for item in order['items']:
            print(f"      - {item['service_name']}: €{item['unit_price']} x{item['quantity']}")
    else:
        print(f"❌ Error: {response.text}")


def get_services(token):
    """Recupera lista servizi per ottenere ID"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(f"{BASE_URL}/services", headers=headers)
    if response.status_code == 200:
        data = response.json()

        # Services endpoint returns dict with 'services' key
        if isinstance(data, dict) and 'services' in data:
            services = data['services']
        elif isinstance(data, dict) and 'items' in data:
            services = data['items']
        else:
            services = data

        if services and isinstance(services, list) and len(services) > 0:
            return services[0]["id"]
    else:
        print(f"❌ Services endpoint error {response.status_code}: {response.text}")
    return None


def main():
    """Main test flow"""
    print("=" * 80)
    print("🧪 TESTING ORDERS API")
    print("=" * 80)

    # 1. Login
    token = test_login("mario.verdi@azienda.it", "Test123!")
    if not token:
        print("❌ Login failed")
        return

    # 2. Get service ID
    print("\n📊 Getting service ID...")
    service_id = get_services(token)
    if not service_id:
        # Fallback: use hardcoded service ID from seed
        print("⚠️  Services endpoint not working, using hardcoded ID from seed")
        service_id = "aade80da-badd-4cfc-95d6-ff2b04367f42"  # AI Act Compliance from seed
    print(f"✅ Service ID: {service_id}")

    # 3. Test Quote Requests
    quote_id = test_create_quote_request(token, service_id)
    test_list_quote_requests(token)

    # 4. Test Orders
    order_id = test_create_order(token, service_id)
    if order_id:
        test_list_orders(token)
        test_get_order(token, order_id)

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETATO")
    print("=" * 80)


if __name__ == "__main__":
    main()
