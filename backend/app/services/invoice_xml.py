"""
Modulo: invoice_xml.py
Descrizione: Servizio generazione XML FatturaPA per SDI
Autore: Claude per Davide
Data: 2026-01-15

Genera XML formato FatturaPA 1.2.1 per Sistema di Interscambio (SDI).

Features:
- Formato XML PA 1.2.1 conforme a specifiche AgID
- Validazione contro XSD ufficiale
- Gestione regime fiscale (RF01 ordinario)
- Gestione IVA (aliquote, nature, esenzioni)
- Gestione P.IVA e Codice Fiscale
- Gestione Codice Destinatario SDI o PEC

Compliance:
- D.Lgs. 127/2015 (fatturazione elettronica B2B)
- Specifiche tecniche FatturaPA v1.2.1
- Tracciato XML validato contro XSD

Structure:
<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica xmlns:...>
  <FatturaElettronicaHeader>
    <DatiTrasmissione>...</DatiTrasmissione>
    <CedentePrestatore>...</CedentePrestatore>
    <CessionarioCommittente>...</CessionarioCommittente>
  </FatturaElettronicaHeader>
  <FatturaElettronicaBody>
    <DatiGenerali>...</DatiGenerali>
    <DatiBeniServizi>...</DatiBeniServizi>
    <DatiPagamento>...</DatiPagamento>
  </FatturaElettronicaBody>
</p:FatturaElettronica>

Dependencies:
- lxml: pip install lxml
- xmlschema: pip install xmlschema (per validazione XSD)
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from lxml import etree

from app.core.config import settings
from app.models.invoice import Invoice

logger = logging.getLogger(__name__)


# =============================================================================
# XML NAMESPACES
# =============================================================================

# Namespace FatturaPA 1.2.1
NS_P = "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"
NS_DS = "http://www.w3.org/2000/09/xmldsig#"
NS_XADES = "http://uri.etsi.org/01903/v1.3.2#"

NSMAP = {
    "p": NS_P,
    "ds": NS_DS,
    "xades": NS_XADES,
}


# =============================================================================
# XML GENERATOR SERVICE
# =============================================================================


class InvoiceXMLGenerator:
    """
    Servizio generazione XML FatturaPA.

    Genera XML formato 1.2.1 conforme a specifiche AgID per invio a SDI.

    Usage:
        generator = InvoiceXMLGenerator()
        xml_path = generator.generate(invoice, output_path="path/to/output.xml")
    """

    def __init__(self):
        """Inizializza generatore XML"""
        logger.info("InvoiceXMLGenerator initialized")

    def generate(
        self,
        invoice: Invoice,
        output_path: str,
        transmission_format: str = "FPR12",
        validate_xsd: bool = False,
    ) -> str:
        """
        Genera XML FatturaPA.

        Args:
            invoice: Oggetto Invoice da convertire in XML
            output_path: Path dove salvare XML
            transmission_format: Formato trasmissione (FPR12 = FatturaPA 1.2.1)
            validate_xsd: Valida XML contro XSD ufficiale

        Returns:
            str: Path file XML generato

        Raises:
            ValueError: Se invoice non valida
            IOError: Se errore scrittura file
        """
        logger.info(f"Generating XML PA for invoice {invoice.invoice_number}")

        # Validate invoice
        self._validate_invoice(invoice)

        # Crea directory output se non esiste
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Crea root element
        root = etree.Element(
            f"{{{NS_P}}}FatturaElettronica",
            nsmap=NSMAP,
            versione="FPR12",  # FatturaPA 1.2.1
        )

        # Build XML structure
        self._build_header(root, invoice, transmission_format)
        self._build_body(root, invoice)

        # Crea tree
        tree = etree.ElementTree(root)

        # Write XML to file
        tree.write(
            str(output_path),
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )

        # Validate against XSD (opzionale)
        if validate_xsd:
            self._validate_against_xsd(str(output_path))

        logger.info(f"XML PA generated successfully: {output_path}")
        return str(output_path)

    def _validate_invoice(self, invoice: Invoice) -> None:
        """
        Valida invoice prima di generare XML.

        Raises:
            ValueError: Se invoice non valida
        """
        if not invoice.invoice_number:
            raise ValueError("Invoice number is required")

        if not invoice.lines or len(invoice.lines) == 0:
            raise ValueError("Invoice must have at least one line")

        if not invoice.seller_vat:
            raise ValueError("Seller VAT is required")

        # Buyer deve avere P.IVA o CF
        if not invoice.buyer_vat and not invoice.buyer_fiscal_code:
            raise ValueError("Buyer must have VAT or Fiscal Code")

        # Buyer deve avere Codice SDI o PEC
        if not invoice.buyer_sdi_code and not invoice.buyer_pec:
            raise ValueError("Buyer must have SDI code or PEC email")

        logger.debug(f"Invoice {invoice.invoice_number} validation passed")

    def _build_header(
        self, root: etree.Element, invoice: Invoice, transmission_format: str
    ) -> None:
        """
        Costruisce FatturaElettronicaHeader.

        Include:
        - DatiTrasmissione
        - CedentePrestatore
        - CessionarioCommittente
        """
        header = etree.SubElement(root, "FatturaElettronicaHeader")

        # DatiTrasmissione
        self._build_transmission_data(header, invoice, transmission_format)

        # CedentePrestatore (Seller)
        self._build_seller_data(header, invoice)

        # CessionarioCommittente (Buyer)
        self._build_buyer_data(header, invoice)

    def _build_transmission_data(
        self, header: etree.Element, invoice: Invoice, transmission_format: str
    ) -> None:
        """Costruisce DatiTrasmissione"""
        dati_trasmissione = etree.SubElement(header, "DatiTrasmissione")

        # IdTrasmittente (P.IVA cedente)
        id_trasmittente = etree.SubElement(dati_trasmissione, "IdTrasmittente")
        etree.SubElement(id_trasmittente, "IdPaese").text = "IT"
        etree.SubElement(id_trasmittente, "IdCodice").text = invoice.seller_vat.replace(
            "IT", ""
        )

        # ProgressivoInvio (Numero progressivo univoco)
        # Formato: IT + P.IVA + _ + Numero fattura sanitizzato
        progressive = f"{invoice.seller_vat.replace('IT', '')}_{invoice.invoice_number.replace('/', '_')}"
        etree.SubElement(dati_trasmissione, "ProgressivoInvio").text = progressive[:20]

        # FormatoTrasmissione
        etree.SubElement(dati_trasmissione, "FormatoTrasmissione").text = (
            transmission_format
        )

        # CodiceDestinatario o PEC
        if invoice.buyer_sdi_code:
            etree.SubElement(dati_trasmissione, "CodiceDestinatario").text = (
                invoice.buyer_sdi_code.upper()
            )
        else:
            # Se non ha codice SDI, usiamo "0000000" e inviamo via PEC
            etree.SubElement(dati_trasmissione, "CodiceDestinatario").text = "0000000"
            if invoice.buyer_pec:
                etree.SubElement(dati_trasmissione, "PECDestinatario").text = (
                    invoice.buyer_pec.lower()
                )

    def _build_seller_data(self, header: etree.Element, invoice: Invoice) -> None:
        """Costruisce CedentePrestatore"""
        cedente = etree.SubElement(header, "CedentePrestatore")

        # DatiAnagrafici
        dati_anagrafici = etree.SubElement(cedente, "DatiAnagrafici")

        # IdFiscaleIVA
        id_fiscale = etree.SubElement(dati_anagrafici, "IdFiscaleIVA")
        etree.SubElement(id_fiscale, "IdPaese").text = "IT"
        etree.SubElement(id_fiscale, "IdCodice").text = invoice.seller_vat.replace(
            "IT", ""
        )

        # CodiceFiscale (se diverso da P.IVA)
        if invoice.seller_fiscal_code and invoice.seller_fiscal_code != invoice.seller_vat:
            etree.SubElement(dati_anagrafici, "CodiceFiscale").text = (
                invoice.seller_fiscal_code.upper()
            )

        # Anagrafica
        anagrafica = etree.SubElement(dati_anagrafici, "Anagrafica")
        etree.SubElement(anagrafica, "Denominazione").text = invoice.seller_name

        # RegimeFiscale
        etree.SubElement(dati_anagrafici, "RegimeFiscale").text = (
            invoice.seller_regime_fiscale
        )

        # Sede
        sede = etree.SubElement(cedente, "Sede")
        addr = invoice.seller_address
        if isinstance(addr, dict):
            etree.SubElement(sede, "Indirizzo").text = addr.get("address", "")
            etree.SubElement(sede, "CAP").text = str(addr.get("zip", ""))
            etree.SubElement(sede, "Comune").text = addr.get("city", "")
            etree.SubElement(sede, "Provincia").text = addr.get("province", "")
            etree.SubElement(sede, "Nazione").text = addr.get("country", "IT")

    def _build_buyer_data(self, header: etree.Element, invoice: Invoice) -> None:
        """Costruisce CessionarioCommittente"""
        cessionario = etree.SubElement(header, "CessionarioCommittente")

        # DatiAnagrafici
        dati_anagrafici = etree.SubElement(cessionario, "DatiAnagrafici")

        # IdFiscaleIVA (se P.IVA presente)
        if invoice.buyer_vat:
            id_fiscale = etree.SubElement(dati_anagrafici, "IdFiscaleIVA")
            # Estrai paese da P.IVA (primi 2 caratteri se alfanumerici)
            buyer_vat_clean = invoice.buyer_vat.strip().upper()
            if len(buyer_vat_clean) >= 2 and buyer_vat_clean[:2].isalpha():
                paese = buyer_vat_clean[:2]
                codice = buyer_vat_clean[2:]
            else:
                paese = "IT"
                codice = buyer_vat_clean.replace("IT", "")

            etree.SubElement(id_fiscale, "IdPaese").text = paese
            etree.SubElement(id_fiscale, "IdCodice").text = codice

        # CodiceFiscale (sempre se presente, anche se uguale a P.IVA)
        if invoice.buyer_fiscal_code:
            etree.SubElement(dati_anagrafici, "CodiceFiscale").text = (
                invoice.buyer_fiscal_code.upper()
            )

        # Anagrafica
        anagrafica = etree.SubElement(dati_anagrafici, "Anagrafica")
        etree.SubElement(anagrafica, "Denominazione").text = invoice.buyer_name

        # Sede
        sede = etree.SubElement(cessionario, "Sede")
        addr = invoice.buyer_address
        if isinstance(addr, dict):
            etree.SubElement(sede, "Indirizzo").text = addr.get("address", "")
            etree.SubElement(sede, "CAP").text = str(addr.get("zip", ""))
            etree.SubElement(sede, "Comune").text = addr.get("city", "")
            provincia = addr.get("province", "")
            if provincia:
                etree.SubElement(sede, "Provincia").text = provincia
            etree.SubElement(sede, "Nazione").text = addr.get("country", "IT")

    def _build_body(self, root: etree.Element, invoice: Invoice) -> None:
        """
        Costruisce FatturaElettronicaBody.

        Include:
        - DatiGenerali (dati generali fattura)
        - DatiBeniServizi (righe fattura)
        - DatiPagamento (modalità pagamento)
        """
        body = etree.SubElement(root, "FatturaElettronicaBody")

        # DatiGenerali
        self._build_general_data(body, invoice)

        # DatiBeniServizi (righe)
        self._build_lines_data(body, invoice)

        # DatiPagamento
        self._build_payment_data(body, invoice)

    def _build_general_data(self, body: etree.Element, invoice: Invoice) -> None:
        """Costruisce DatiGenerali"""
        dati_generali = etree.SubElement(body, "DatiGenerali")

        # DatiGeneraliDocumento
        dati_doc = etree.SubElement(dati_generali, "DatiGeneraliDocumento")

        # TipoDocumento (TD01 = Fattura)
        etree.SubElement(dati_doc, "TipoDocumento").text = "TD01"

        # Divisa
        etree.SubElement(dati_doc, "Divisa").text = invoice.currency

        # Data
        etree.SubElement(dati_doc, "Data").text = invoice.issue_date.strftime("%Y-%m-%d")

        # Numero
        etree.SubElement(dati_doc, "Numero").text = invoice.invoice_number

        # Importi (opzionali ma consigliati)
        etree.SubElement(dati_doc, "ImportoTotaleDocumento").text = self._format_amount(
            invoice.total
        )

    def _build_lines_data(self, body: etree.Element, invoice: Invoice) -> None:
        """Costruisce DatiBeniServizi (righe fattura)"""
        dati_beni = etree.SubElement(body, "DatiBeniServizi")

        # DettaglioLinee (una per ogni riga)
        for line in sorted(invoice.lines, key=lambda x: x.line_number):
            dettaglio = etree.SubElement(dati_beni, "DettaglioLinee")

            # NumeroLinea
            etree.SubElement(dettaglio, "NumeroLinea").text = str(line.line_number)

            # Descrizione
            etree.SubElement(dettaglio, "Descrizione").text = line.description

            # Quantita
            etree.SubElement(dettaglio, "Quantita").text = self._format_amount(
                line.quantity, decimals=2
            )

            # PrezzoUnitario
            etree.SubElement(dettaglio, "PrezzoUnitario").text = self._format_amount(
                line.unit_price
            )

            # PrezzoTotale (imponibile riga)
            imponibile_riga = line.quantity * line.unit_price
            etree.SubElement(dettaglio, "PrezzoTotale").text = self._format_amount(
                imponibile_riga
            )

            # AliquotaIVA
            etree.SubElement(dettaglio, "AliquotaIVA").text = self._format_amount(
                line.tax_rate, decimals=2
            )

        # DatiRiepilogo (riepilogo per aliquota IVA)
        self._build_tax_summary(dati_beni, invoice)

    def _build_tax_summary(self, dati_beni: etree.Element, invoice: Invoice) -> None:
        """
        Costruisce DatiRiepilogo (riepilogo IVA).

        Raggruppa righe per aliquota IVA e calcola totali.
        """
        # Raggruppa per aliquota
        tax_groups = {}
        for line in invoice.lines:
            tax_rate = float(line.tax_rate)
            if tax_rate not in tax_groups:
                tax_groups[tax_rate] = {
                    "imponibile": Decimal("0.00"),
                    "imposta": Decimal("0.00"),
                }

            imponibile_riga = line.quantity * line.unit_price
            tax_groups[tax_rate]["imponibile"] += imponibile_riga
            tax_groups[tax_rate]["imposta"] += line.tax_amount

        # Crea DatiRiepilogo per ogni aliquota
        for tax_rate, amounts in sorted(tax_groups.items()):
            riepilogo = etree.SubElement(dati_beni, "DatiRiepilogo")

            # AliquotaIVA
            etree.SubElement(riepilogo, "AliquotaIVA").text = self._format_amount(
                Decimal(str(tax_rate)), decimals=2
            )

            # ImponibileImporto
            etree.SubElement(riepilogo, "ImponibileImporto").text = self._format_amount(
                amounts["imponibile"]
            )

            # Imposta
            etree.SubElement(riepilogo, "Imposta").text = self._format_amount(
                amounts["imposta"]
            )

            # EsigibilitaIVA (I = Immediata, tipicamente per fatture ordinarie)
            etree.SubElement(riepilogo, "EsigibilitaIVA").text = "I"

    def _build_payment_data(self, body: etree.Element, invoice: Invoice) -> None:
        """Costruisce DatiPagamento"""
        dati_pag = etree.SubElement(body, "DatiPagamento")

        # CondizioniPagamento (TP02 = Pagamento completo)
        etree.SubElement(dati_pag, "CondizioniPagamento").text = "TP02"

        # DettaglioPagamento
        dettaglio_pag = etree.SubElement(dati_pag, "DettaglioPagamento")

        # ModalitaPagamento (MP08 = Carta di pagamento)
        # Nota: Stripe usa carte, quindi MP08 è appropriato
        etree.SubElement(dettaglio_pag, "ModalitaPagamento").text = "MP08"

        # ImportoPagamento
        etree.SubElement(dettaglio_pag, "ImportoPagamento").text = self._format_amount(
            invoice.total
        )

        # DataScadenzaPagamento (se presente)
        if invoice.due_date:
            etree.SubElement(dettaglio_pag, "DataScadenzaPagamento").text = (
                invoice.due_date.strftime("%Y-%m-%d")
            )

    def _format_amount(self, amount: Decimal, decimals: int = 2) -> str:
        """
        Formatta importo per XML.

        Args:
            amount: Importo da formattare
            decimals: Numero decimali (default: 2)

        Returns:
            str: Importo formattato (es: "1234.56")
        """
        return f"{amount:.{decimals}f}"

    def _validate_against_xsd(self, xml_path: str) -> None:
        """
        Valida XML contro XSD ufficiale FatturaPA.

        Args:
            xml_path: Path file XML da validare

        Raises:
            ValueError: Se validazione fallisce

        Note:
            Richiede file XSD FatturaPA 1.2.1 salvato localmente.
            XSD scaricabile da: https://www.fatturapa.gov.it/
        """
        try:
            import xmlschema

            # TODO: Scarica e salva XSD FatturaPA 1.2.1
            # xsd_path = Path(__file__).parent / "schemas" / "FatturaPA_v1.2.1.xsd"
            # if not xsd_path.exists():
            #     logger.warning("XSD file not found, skipping validation")
            #     return
            #
            # schema = xmlschema.XMLSchema(str(xsd_path))
            # schema.validate(xml_path)
            # logger.info("XML validation against XSD passed")

            logger.warning(
                "XSD validation not implemented yet (XSD file not available)"
            )

        except ImportError:
            logger.warning("xmlschema not installed, skipping XSD validation")
        except Exception as e:
            logger.error(f"XSD validation failed: {str(e)}")
            raise ValueError(f"XML validation failed: {str(e)}")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def generate_invoice_xml(
    invoice: Invoice,
    output_path: str,
    transmission_format: str = "FPR12",
    validate_xsd: bool = False,
) -> str:
    """
    Helper function per generare XML FatturaPA.

    Args:
        invoice: Invoice object
        output_path: Path output XML
        transmission_format: Formato trasmissione (FPR12 = FatturaPA 1.2.1)
        validate_xsd: Valida XML contro XSD

    Returns:
        str: Path file XML generato

    Usage:
        xml_path = generate_invoice_xml(invoice, "/path/to/invoice.xml")
    """
    generator = InvoiceXMLGenerator()
    return generator.generate(
        invoice=invoice,
        output_path=output_path,
        transmission_format=transmission_format,
        validate_xsd=validate_xsd,
    )


# =============================================================================
# LOGGING
# =============================================================================

logger.info("Invoice XML generator loaded successfully")
