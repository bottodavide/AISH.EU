"""
Script di test per Files API
Testa upload, download, thumbnails e gestione file
"""

import io
import requests
from PIL import Image

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


def create_test_image():
    """Crea immagine di test in memoria"""
    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def create_test_pdf():
    """Crea PDF di test (semplice)"""
    # PDF minimo valido
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000315 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
408
%%EOF"""
    return io.BytesIO(pdf_content)


def test_upload_image(token):
    """Test upload immagine"""
    headers = {"Authorization": f"Bearer {token}"}

    # Crea immagine di test
    img_bytes = create_test_image()

    files = {
        "file": ("test_image.jpg", img_bytes, "image/jpeg")
    }
    data = {
        "category": "image",
        "description": "Immagine di test",
        "is_public": False
    }

    response = requests.post(
        f"{BASE_URL}/files/upload",
        files=files,
        data=data,
        headers=headers
    )

    print(f"\n📤 UPLOAD IMAGE")
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        file = response.json()
        print(f"✅ File caricato:")
        print(f"   ID: {file['file_id']}")
        print(f"   Nome: {file['filename']}")
        print(f"   Size: {file['file_size']} bytes")
        print(f"   MIME: {file['mime_type']}")
        print(f"   URL: {file['url']}")
        if file.get('thumbnail_url'):
            print(f"   Thumbnail: {file['thumbnail_url']}")
        return file['file_id']
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_upload_pdf(token):
    """Test upload PDF"""
    headers = {"Authorization": f"Bearer {token}"}

    # Crea PDF di test
    pdf_bytes = create_test_pdf()

    files = {
        "file": ("test_document.pdf", pdf_bytes, "application/pdf")
    }
    data = {
        "category": "document",
        "description": "Documento PDF di test",
        "is_public": False
    }

    response = requests.post(
        f"{BASE_URL}/files/upload",
        files=files,
        data=data,
        headers=headers
    )

    print(f"\n📄 UPLOAD PDF")
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        file = response.json()
        print(f"✅ File caricato:")
        print(f"   ID: {file['file_id']}")
        print(f"   Nome: {file['filename']}")
        print(f"   Size: {file['file_size']} bytes")
        return file['file_id']
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_list_files(token):
    """Test lista file"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/files", headers=headers)

    print(f"\n📋 LIST FILES")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        files = response.json()
        print(f"✅ Trovati {len(files)} file:")
        for file in files:
            print(f"   - {file['filename']} ({file['category']}) - {file['file_size']} bytes")
    else:
        print(f"❌ Error: {response.text}")


def test_get_file_metadata(token, file_id):
    """Test get metadata file"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/files/{file_id}", headers=headers)

    print(f"\n📝 GET FILE METADATA")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        file = response.json()
        print(f"✅ File metadata:")
        print(f"   Nome: {file['filename']}")
        print(f"   Categoria: {file['category']}")
        print(f"   Size: {file['size_human']}")
        print(f"   Hash: {file['sha256_hash'][:16]}...")
        print(f"   Downloads: {file['download_count']}")
        print(f"   Pubblico: {file['is_public']}")
    else:
        print(f"❌ Error: {response.text}")


def test_download_file(token, file_id):
    """Test download file"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/files/{file_id}/download", headers=headers)

    print(f"\n⬇️  DOWNLOAD FILE")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ File scaricato: {len(response.content)} bytes")
        print(f"   Content-Type: {response.headers.get('content-type')}")
    else:
        print(f"❌ Error: {response.text}")


def test_get_thumbnail(token, file_id):
    """Test get thumbnail"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/files/{file_id}/thumbnail", headers=headers)

    print(f"\n🖼️  GET THUMBNAIL")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Thumbnail scaricata: {len(response.content)} bytes")
    else:
        print(f"⚠️  Thumbnail non disponibile (normale per PDF)")


def test_update_file(token, file_id):
    """Test aggiornamento metadata"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "description": "Descrizione aggiornata tramite API",
        "is_public": True
    }
    response = requests.patch(f"{BASE_URL}/files/{file_id}", json=data, headers=headers)

    print(f"\n✏️  UPDATE FILE METADATA")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        file = response.json()
        print(f"✅ File aggiornato:")
        print(f"   Descrizione: {file['description']}")
        print(f"   Pubblico: {file['is_public']}")
    else:
        print(f"❌ Error: {response.text}")


def test_delete_file(token, file_id):
    """Test soft delete file"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/files/{file_id}", headers=headers)

    print(f"\n🗑️  DELETE FILE (soft)")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Error: {response.text}")


def main():
    """Main test flow"""
    print("=" * 80)
    print("🧪 TESTING FILES API")
    print("=" * 80)

    # 1. Login
    token = test_login("mario.verdi@azienda.it", "Test123!")
    if not token:
        print("❌ Login failed")
        return

    # 2. Upload immagine
    image_id = test_upload_image(token)

    # 3. Upload PDF
    pdf_id = test_upload_pdf(token)

    # 4. Lista file
    test_list_files(token)

    # 5. Metadata file
    if image_id:
        test_get_file_metadata(token, image_id)

    # 6. Download file
    if image_id:
        test_download_file(token, image_id)

    # 7. Get thumbnail
    if image_id:
        test_get_thumbnail(token, image_id)

    # 8. Update metadata
    if pdf_id:
        test_update_file(token, pdf_id)

    # 9. Delete file (soft)
    if pdf_id:
        test_delete_file(token, pdf_id)

    # 10. Lista file dopo delete
    test_list_files(token)

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETATO")
    print("=" * 80)
    print(f"\nControlla directory uploads/ per verificare file salvati")


if __name__ == "__main__":
    main()
