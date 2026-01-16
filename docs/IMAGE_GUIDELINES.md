# Linee Guida Immagini - AI Strategy Hub

Documento di riferimento per amministratori ed editor che gestiscono contenuti multimediali sulla piattaforma.

---

## 📋 Indice

1. [Immagini Blog](#immagini-blog)
2. [Immagini Servizi](#immagini-servizi)
3. [Immagini CMS Pagine](#immagini-cms-pagine)
4. [Best Practices Generali](#best-practices-generali)
5. [Strumenti Consigliati](#strumenti-consigliati)

---

## 📰 Immagini Blog

### Featured Image (Immagine in Evidenza)

**Scopo:** Immagine principale dell'articolo visualizzata nelle anteprime e nella pagina dettaglio

**Specifiche Tecniche:**
- **Dimensioni:** 1200 x 630 px
- **Ratio:** 16:9
- **Formati ammessi:** JPG, PNG, WebP
- **Peso massimo:** 500 KB
- **Risoluzione consigliata:** 72 DPI (web)

**Note:**
- Ottimizza sempre l'immagine per il web prima del caricamento
- Usa WebP quando possibile per migliore compressione
- Assicurati che l'immagine sia rappresentativa del contenuto
- Evita testo piccolo nell'immagine (può essere illeggibile su mobile)

### Immagini Inline (Nel Contenuto)

**Scopo:** Immagini all'interno del corpo dell'articolo

**Specifiche Tecniche:**
- **Larghezza massima:** 1200 px
- **Altezza:** Proporzionale (no distorsioni)
- **Formati ammessi:** JPG, PNG, WebP, GIF
- **Peso massimo:** 300 KB per immagine
- **Risoluzione consigliata:** 72 DPI (web)

**Note:**
- Usa immagini orizzontali (landscape) quando possibile
- Aggiungi sempre un testo alternativo (alt text) per l'accessibilità
- Per screenshot, considera PNG per testo nitido
- Per foto, usa JPG o WebP

---

## 🛠️ Immagini Servizi

### Service Hero Image

**Scopo:** Immagine principale del servizio

**Specifiche Tecniche:**
- **Dimensioni:** 1200 x 800 px
- **Ratio:** 3:2
- **Formati ammessi:** JPG, PNG, WebP
- **Peso massimo:** 400 KB
- **Risoluzione consigliata:** 72 DPI (web)

**Note:**
- Usa immagini professionali e di alta qualità
- Evita stock photo troppo generiche
- L'immagine deve rappresentare il servizio offerto

### Service Icons

**Scopo:** Icone per features e deliverables

**Specifiche Tecniche:**
- **Dimensioni:** 64 x 64 px o 128 x 128 px
- **Ratio:** 1:1 (quadrato)
- **Formati ammessi:** SVG (preferito), PNG
- **Peso massimo:** 50 KB
- **Sfondo:** Trasparente

**Note:**
- SVG è preferito per scalabilità
- Usa icone coerenti con il brand
- Mantieni stile uniforme tra tutte le icone

---

## 📄 Immagini CMS Pagine

### Hero Section

**Scopo:** Immagine principale della pagina (About, Chi Siamo, etc.)

**Specifiche Tecniche:**
- **Dimensioni:** 1920 x 1080 px
- **Ratio:** 16:9
- **Formati ammessi:** JPG, PNG, WebP
- **Peso massimo:** 600 KB
- **Risoluzione consigliata:** 72 DPI (web)

**Note:**
- Full-width responsive
- Considera versione mobile separata (800x600px)
- Evita elementi importanti ai bordi (safe area)

### Content Images

**Scopo:** Immagini generiche nel contenuto delle pagine

**Specifiche Tecniche:**
- **Larghezza massima:** 1200 px
- **Altezza:** Variabile (proporzionale)
- **Formati ammessi:** JPG, PNG, WebP
- **Peso massimo:** 400 KB
- **Risoluzione consigliata:** 72 DPI (web)

---

## ✅ Best Practices Generali

### 1. Ottimizzazione

- **Comprimi sempre** le immagini prima dell'upload
- Usa formati moderni (WebP) quando possibile
- Rimuovi metadati EXIF non necessari
- Test su connessioni lente (3G)

### 2. Naming Convention

Usa nomi file descrittivi e SEO-friendly:

```
✅ CORRETTO:
- ai-compliance-audit-2024.jpg
- cybersecurity-nis2-checklist.png
- gdpr-workflow-diagram.webp

❌ SCORRETTO:
- IMG_1234.jpg
- screenshot.png
- image-final-final-v2.jpg
```

### 3. Accessibilità

- **Alt Text:** Sempre presente e descrittivo
- **Contrasto:** Verifica la leggibilità del testo su immagini
- **Dimensione testo:** Non inserire testo troppo piccolo

### 4. Performance

**Obiettivi Target:**
- Pagina blog completa: < 2 MB totali
- Singola immagine featured: < 500 KB
- Singola immagine inline: < 300 KB
- Tempo caricamento immagini: < 2 secondi

### 5. Copyright e Licensing

- Usa solo immagini con licenza appropriata
- Se usi stock photo, verifica la licenza
- Cita la fonte quando richiesto
- Preferisci immagini originali quando possibile

### 6. Responsive Design

Considera versioni multiple per dispositivi diversi:
- Desktop: Full resolution
- Tablet: 800-1000px width
- Mobile: 600-800px width

---

## 🛠️ Strumenti Consigliati

### Compressione Immagini

**Online (Gratuiti):**
- [TinyPNG](https://tinypng.com) - JPG e PNG
- [Squoosh](https://squoosh.app) - Tutti i formati, include WebP
- [ImageOptim](https://imageoptim.com) - Mac app

**Da Command Line:**
```bash
# Converti in WebP
cwebp input.jpg -q 80 -o output.webp

# Ottimizza JPG
jpegoptim --max=85 input.jpg

# Ottimizza PNG
optipng -o7 input.png
```

### Ridimensionamento

**Online:**
- [ResizeImage.net](https://resizeimage.net)
- [Bulk Resize Photos](https://bulkresizephotos.com)

**Photoshop / GIMP:**
- Usa "Save for Web" con qualità 80-85%
- Attiva ottimizzazione progressiva per JPG

### Conversione Formati

**CloudConvert:**
- [cloudconvert.com](https://cloudconvert.com)
- Supporta batch conversion
- Include WebP

### Verifica Dimensioni e Peso

**Online:**
- [Google PageSpeed Insights](https://pagespeed.web.dev)
- Identifica immagini da ottimizzare

**Browser DevTools:**
```javascript
// Console del browser per vedere peso immagini
document.querySelectorAll('img').forEach(img => {
  console.log(img.src, img.naturalWidth + 'x' + img.naturalHeight);
});
```

---

## 📊 Checklist Pre-Upload

Prima di caricare un'immagine, verifica:

- [ ] Dimensioni corrette per il tipo di immagine
- [ ] Formato file appropriato (preferibilmente WebP)
- [ ] Peso sotto il limite massimo
- [ ] Nome file descrittivo e SEO-friendly
- [ ] Immagine compressa/ottimizzata
- [ ] Qualità visiva accettabile dopo compressione
- [ ] Alt text preparato (descrittivo e conciso)
- [ ] Copyright e licenza verificati

---

## 🆘 Troubleshooting

### Immagine Troppo Grande

**Problema:** File supera il limite di peso

**Soluzione:**
1. Riduci qualità JPEG (target: 80-85%)
2. Converti in WebP
3. Ridimensiona se troppo grande
4. Rimuovi metadati EXIF

### Immagine Sfocata

**Problema:** Immagine appare sfocata sul sito

**Soluzione:**
1. Verifica dimensioni originali (non troppo piccole)
2. Usa formato corretto (PNG per grafica, JPG per foto)
3. Non upscalare immagini piccole
4. Mantieni ratio aspect originale

### Caricamento Lento

**Problema:** Immagini caricano troppo lentamente

**Soluzione:**
1. Riduci peso file (< 300 KB)
2. Usa lazy loading (già implementato)
3. Considera WebP invece di JPG
4. Verifica CDN configuration

---

## 📞 Supporto

Per problemi tecnici o domande:
- **Email:** tech@aistrategyhub.eu
- **Documentazione:** `/docs`
- **Ticket System:** [link-al-sistema]

---

**Ultima revisione:** 2026-01-16
**Versione documento:** 1.0
**Autore:** AI Strategy Hub Technical Team
