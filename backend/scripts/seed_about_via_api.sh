#!/bin/bash
# Script per popolare la pagina About tramite l'API
# Richiede di essere loggati come admin

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🌱 Seeding About Page via API${NC}"
echo -e "${BLUE}============================================================${NC}"

# URL dell'API
API_URL="http://localhost:8000/api/v1/about/admin"

# Dati JSON
JSON_DATA='{
  "profile_name": "Davide Botto",
  "profile_title": "Senior AI & Privacy Consultant",
  "profile_description": "Aiuto le aziende a innovare in sicurezza, trasformando la compliance in un asset strategico.",
  "profile_image_url": null,
  "profile_badges": [
    "ISO 27001 LA",
    "CIPP/E",
    "AI Ethics"
  ],
  "is_published": true,
  "specialization_areas": [
    {
      "name": "AI Governance",
      "percentage": 95,
      "display_order": 0
    },
    {
      "name": "GDPR Compliance",
      "percentage": 98,
      "display_order": 1
    },
    {
      "name": "Cybersecurity Audit",
      "percentage": 90,
      "display_order": 2
    },
    {
      "name": "Risk Management",
      "percentage": 92,
      "display_order": 3
    }
  ],
  "competence_sections": [
    {
      "title": "AI Governance & Ethics",
      "icon": "BookOpen",
      "description": "Con l'\''avvento dell'\''AI Act europeo, la governance dei sistemi di intelligenza artificiale non è più opzionale. Offro supporto completo per la classificazione dei sistemi AI, la valutazione d'\''impatto (FRIA) e la definizione di policy etiche.",
      "features": [
        "Gap Analysis rispetto all'\''AI Act",
        "Sviluppo di AI Policy aziendali",
        "Valutazione dei rischi algoritmici",
        "Formazione etica per team di sviluppo",
        "Audit di sistemi AI ad alto rischio",
        "Documentazione tecnica per la conformità"
      ],
      "display_order": 0
    },
    {
      "title": "GDPR & Data Protection",
      "icon": "Shield",
      "description": "La protezione dei dati è il fondamento della fiducia digitale. Come DPO certificato, guido le organizzazioni attraverso le complessità del GDPR, garantendo che i dati siano trattati in modo lecito, corretto e trasparente.",
      "features": [
        "Assunzione del ruolo di Data Protection Officer (DPO) esterno",
        "Esecuzione di DPIA (Data Protection Impact Assessment)",
        "Gestione dei registri dei trattamenti e delle nomine",
        "Supporto in caso di Data Breach e rapporti con il Garante",
        "Formazione GDPR per dipendenti e management",
        "Audit di conformità e remediation plan"
      ],
      "display_order": 1
    },
    {
      "title": "Cybersecurity & NIS2",
      "icon": "Lock",
      "description": "La Direttiva NIS2 richiede alle organizzazioni di adottare misure tecniche e organizzative adeguate per gestire i rischi di sicurezza. Supporto le aziende nell'\''implementazione di framework di cybersecurity conformi e resilienza operativa.",
      "features": [
        "Gap Analysis rispetto alla Direttiva NIS2",
        "Implementazione di Security Operations Center (SOC)",
        "Business Continuity Planning e Disaster Recovery",
        "Penetration Testing e Vulnerability Assessment",
        "Security Awareness Training",
        "Incident Response Planning"
      ],
      "display_order": 2
    },
    {
      "title": "Consulenza Strategica",
      "icon": "TrendingUp",
      "description": "Oltre alla compliance normativa, offro supporto strategico per integrare AI e sicurezza informatica come leve competitive. Aiuto le aziende a costruire un ecosistema digitale sicuro, etico e scalabile.",
      "features": [
        "AI Strategy & Roadmap",
        "Digital Transformation Governance",
        "Vendor Risk Management",
        "Privacy by Design per nuovi prodotti",
        "Compliance Automation con AI",
        "Executive Advisory su AI & Privacy"
      ],
      "display_order": 3
    }
  ]
}'

echo -e "\n${BLUE}📤 Inviando dati all'API...${NC}"
echo -e "${BLUE}URL: ${API_URL}${NC}"
echo ""

# Nota: Questo script richiede che tu sia loggato come admin
# Se hai un token JWT, passalo così:
# -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Per ora chiediamo il token all'utente
read -p "Inserisci il tuo JWT token (o premi Invio per saltare): " JWT_TOKEN

if [ -z "$JWT_TOKEN" ]; then
    echo -e "${RED}❌ Token non fornito. Devi essere loggato come admin.${NC}"
    echo -e "${BLUE}💡 Vai su http://localhost:3000/login e fai login come admin${NC}"
    echo -e "${BLUE}💡 Poi usa il browser developer tools per copiare il token JWT${NC}"
    echo -e "${BLUE}💡 Oppure usa direttamente l'interfaccia admin: http://localhost:3000/admin/about${NC}"
    exit 1
fi

# Fai la richiesta PUT
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d "$JSON_DATA" \
  "$API_URL")

# Estrai status code e body
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo ""
echo -e "${BLUE}📥 Risposta ricevuta${NC}"
echo -e "${BLUE}Status Code: ${HTTP_CODE}${NC}"

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    echo -e "${GREEN}✅ SUCCESSO! Pagina About creata/aggiornata${NC}"
    echo -e "${GREEN}🌐 Vai su http://localhost:3000/about per vederla!${NC}"
    echo -e "${GREEN}⚙️  Vai su http://localhost:3000/admin/about per modificarla!${NC}"
else
    echo -e "${RED}❌ ERRORE: Richiesta fallita${NC}"
    echo -e "${RED}Response:${NC}"
    echo "$BODY"
fi

echo -e "\n${BLUE}============================================================${NC}"
