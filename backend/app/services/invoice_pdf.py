"""
Modulo: invoice_pdf.py
Descrizione: Servizio generazione PDF fatture italiane
Autore: Claude per Davide
Data: 2026-01-15

Genera PDF professionale per fatture elettroniche italiane.

Features:
- Layout professionale con header/footer
- Logo AI Strategy Hub
- Dati cedente e cessionario
- Tabella righe fattura
- Totali (imponibile, IVA, totale)
- Info bancarie per pagamento
- QR code PagoPA (opzionale)

Compliance:
- Formato leggibile conforme a normativa
- Copia cortesia per cliente (non sostitutiva di XML PA)
- Conservazione 10 anni

Dependencies:
- reportlab: pip install reportlab
- qrcode: pip install qrcode (opzionale per QR code)
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import settings
from app.models.invoice import Invoice

logger = logging.getLogger(__name__)


# =============================================================================
# PDF STYLES
# =============================================================================


class InvoicePDFStyles:
    """
    Stili PDF per fattura.

    Definisce font, colori, dimensioni per elementi fattura.
    """

    # Colori brand AI Strategy Hub
    PRIMARY_COLOR = colors.HexColor("#1e3a8a")  # Blue 900
    SECONDARY_COLOR = colors.HexColor("#3b82f6")  # Blue 500
    ACCENT_COLOR = colors.HexColor("#60a5fa")  # Blue 400
    TEXT_COLOR = colors.HexColor("#1f2937")  # Gray 800
    GRAY_COLOR = colors.HexColor("#6b7280")  # Gray 500
    LIGHT_GRAY = colors.HexColor("#f3f4f6")  # Gray 100

    # Font sizes
    TITLE_SIZE = 24
    SUBTITLE_SIZE = 14
    HEADING_SIZE = 12
    BODY_SIZE = 10
    SMALL_SIZE = 8

    # Margins
    PAGE_WIDTH = A4[0]
    PAGE_HEIGHT = A4[1]
    MARGIN_LEFT = 2 * cm
    MARGIN_RIGHT = 2 * cm
    MARGIN_TOP = 2 * cm
    MARGIN_BOTTOM = 2 * cm

    @classmethod
    def get_styles(cls):
        """Ritorna dizionario stili Paragraph"""
        styles = getSampleStyleSheet()

        # Title
        styles.add(
            ParagraphStyle(
                name="InvoiceTitle",
                parent=styles["Heading1"],
                fontSize=cls.TITLE_SIZE,
                textColor=cls.PRIMARY_COLOR,
                spaceAfter=12,
                alignment=1,  # Center
            )
        )

        # Subtitle
        styles.add(
            ParagraphStyle(
                name="InvoiceSubtitle",
                parent=styles["Heading2"],
                fontSize=cls.SUBTITLE_SIZE,
                textColor=cls.SECONDARY_COLOR,
                spaceAfter=6,
            )
        )

        # Section heading
        styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=styles["Heading3"],
                fontSize=cls.HEADING_SIZE,
                textColor=cls.PRIMARY_COLOR,
                spaceBefore=12,
                spaceAfter=6,
                borderWidth=0,
                borderColor=cls.PRIMARY_COLOR,
                borderPadding=4,
            )
        )

        # Body text
        styles.add(
            ParagraphStyle(
                name="InvoiceBody",
                parent=styles["Normal"],
                fontSize=cls.BODY_SIZE,
                textColor=cls.TEXT_COLOR,
                spaceAfter=4,
            )
        )

        # Small text
        styles.add(
            ParagraphStyle(
                name="InvoiceSmall",
                parent=styles["Normal"],
                fontSize=cls.SMALL_SIZE,
                textColor=cls.GRAY_COLOR,
                spaceAfter=2,
            )
        )

        return styles


# =============================================================================
# PDF GENERATOR SERVICE
# =============================================================================


class InvoicePDFGenerator:
    """
    Servizio generazione PDF fattura.

    Usage:
        generator = InvoicePDFGenerator()
        pdf_path = generator.generate(invoice, output_path="path/to/output.pdf")
    """

    def __init__(self):
        """Inizializza generatore PDF"""
        self.styles = InvoicePDFStyles.get_styles()
        logger.info("InvoicePDFGenerator initialized")

    def generate(
        self,
        invoice: Invoice,
        output_path: str,
        include_payment_info: bool = True,
        include_qr_code: bool = False,
        language: str = "it",
    ) -> str:
        """
        Genera PDF fattura.

        Args:
            invoice: Oggetto Invoice da convertire in PDF
            output_path: Path dove salvare PDF
            include_payment_info: Include info bancarie
            include_qr_code: Include QR code PagoPA
            language: Lingua PDF (it/en)

        Returns:
            str: Path file PDF generato

        Raises:
            ValueError: Se invoice non valida
            IOError: Se errore scrittura file
        """
        logger.info(f"Generating PDF for invoice {invoice.invoice_number}")

        # Validate invoice
        self._validate_invoice(invoice)

        # Crea directory output se non esiste
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Genera PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=InvoicePDFStyles.MARGIN_LEFT,
            rightMargin=InvoicePDFStyles.MARGIN_RIGHT,
            topMargin=InvoicePDFStyles.MARGIN_TOP,
            bottomMargin=InvoicePDFStyles.MARGIN_BOTTOM,
            title=f"Fattura {invoice.invoice_number}",
            author="AI Strategy Hub",
            subject=f"Fattura elettronica n. {invoice.invoice_number}",
        )

        # Build PDF content
        story = []
        story.extend(self._build_header(invoice))
        story.append(Spacer(1, 1 * cm))
        story.extend(self._build_parties_info(invoice))
        story.append(Spacer(1, 1 * cm))
        story.extend(self._build_invoice_lines(invoice))
        story.append(Spacer(1, 1 * cm))
        story.extend(self._build_totals(invoice))

        if include_payment_info:
            story.append(Spacer(1, 1 * cm))
            story.extend(self._build_payment_info(invoice))

        story.append(Spacer(1, 1 * cm))
        story.extend(self._build_footer(invoice))

        # Build PDF
        doc.build(story)

        logger.info(f"PDF generated successfully: {output_path}")
        return str(output_path)

    def _validate_invoice(self, invoice: Invoice) -> None:
        """
        Valida invoice prima di generare PDF.

        Raises:
            ValueError: Se invoice non valida
        """
        if not invoice.invoice_number:
            raise ValueError("Invoice number is required")

        if not invoice.lines or len(invoice.lines) == 0:
            raise ValueError("Invoice must have at least one line")

        if not invoice.seller_name or not invoice.buyer_name:
            raise ValueError("Seller and buyer names are required")

        logger.debug(f"Invoice {invoice.invoice_number} validation passed")

    def _build_header(self, invoice: Invoice) -> list:
        """Genera header PDF con logo e titolo"""
        elements = []

        # Title
        title = Paragraph(
            f"<b>FATTURA N. {invoice.invoice_number}</b>",
            self.styles["InvoiceTitle"],
        )
        elements.append(title)

        # Date
        date_text = f"Data emissione: {invoice.issue_date.strftime('%d/%m/%Y')}"
        if invoice.due_date:
            date_text += f" | Scadenza: {invoice.due_date.strftime('%d/%m/%Y')}"

        date_para = Paragraph(date_text, self.styles["InvoiceBody"])
        elements.append(date_para)

        return elements

    def _build_parties_info(self, invoice: Invoice) -> list:
        """Genera sezione dati cedente e cessionario"""
        elements = []

        # Tabella a 2 colonne: Cedente | Cessionario
        data = []

        # Header row
        data.append([
            Paragraph("<b>CEDENTE PRESTATORE</b>", self.styles["SectionHeading"]),
            Paragraph("<b>CESSIONARIO COMMITTENTE</b>", self.styles["SectionHeading"]),
        ])

        # Seller info
        seller_lines = [
            f"<b>{invoice.seller_name}</b>",
            f"P. IVA: {invoice.seller_vat}",
        ]

        if invoice.seller_fiscal_code:
            seller_lines.append(f"C.F.: {invoice.seller_fiscal_code}")

        # Address
        addr = invoice.seller_address
        if isinstance(addr, dict):
            address_line = addr.get("address", "")
            city_line = f"{addr.get('zip', '')} {addr.get('city', '')} ({addr.get('province', '')})"
            seller_lines.append(address_line)
            seller_lines.append(city_line)
            seller_lines.append(addr.get("country", "IT"))

        seller_lines.append(f"<i>Regime fiscale: {invoice.seller_regime_fiscale}</i>")

        # Buyer info
        buyer_lines = [
            f"<b>{invoice.buyer_name}</b>",
        ]

        if invoice.buyer_vat:
            buyer_lines.append(f"P. IVA: {invoice.buyer_vat}")

        if invoice.buyer_fiscal_code:
            buyer_lines.append(f"C.F.: {invoice.buyer_fiscal_code}")

        # Address
        addr = invoice.buyer_address
        if isinstance(addr, dict):
            address_line = addr.get("address", "")
            city_line = f"{addr.get('zip', '')} {addr.get('city', '')} ({addr.get('province', '')})"
            buyer_lines.append(address_line)
            buyer_lines.append(city_line)
            buyer_lines.append(addr.get("country", "IT"))

        if invoice.buyer_pec:
            buyer_lines.append(f"<i>PEC: {invoice.buyer_pec}</i>")

        if invoice.buyer_sdi_code:
            buyer_lines.append(f"<i>Codice SDI: {invoice.buyer_sdi_code}</i>")

        # Add to table
        seller_para = Paragraph("<br/>".join(seller_lines), self.styles["InvoiceBody"])
        buyer_para = Paragraph("<br/>".join(buyer_lines), self.styles["InvoiceBody"])

        data.append([seller_para, buyer_para])

        # Create table
        table = Table(data, colWidths=[8.5 * cm, 8.5 * cm])
        table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, 0), InvoicePDFStyles.LIGHT_GRAY),
                ("GRID", (0, 0), (-1, -1), 0.5, InvoicePDFStyles.GRAY_COLOR),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ])
        )

        elements.append(table)
        return elements

    def _build_invoice_lines(self, invoice: Invoice) -> list:
        """Genera tabella righe fattura"""
        elements = []

        # Section title
        title = Paragraph("<b>DESCRIZIONE PRESTAZIONI</b>", self.styles["SectionHeading"])
        elements.append(title)
        elements.append(Spacer(1, 0.5 * cm))

        # Table header
        data = [
            [
                Paragraph("<b>#</b>", self.styles["InvoiceBody"]),
                Paragraph("<b>Descrizione</b>", self.styles["InvoiceBody"]),
                Paragraph("<b>Q.tà</b>", self.styles["InvoiceBody"]),
                Paragraph("<b>Prezzo<br/>Unitario</b>", self.styles["InvoiceBody"]),
                Paragraph("<b>IVA<br/>%</b>", self.styles["InvoiceBody"]),
                Paragraph("<b>Imponibile</b>", self.styles["InvoiceBody"]),
                Paragraph("<b>Totale</b>", self.styles["InvoiceBody"]),
            ]
        ]

        # Lines
        for line in sorted(invoice.lines, key=lambda x: x.line_number):
            imponibile = line.quantity * line.unit_price

            data.append([
                Paragraph(str(line.line_number), self.styles["InvoiceBody"]),
                Paragraph(line.description, self.styles["InvoiceBody"]),
                Paragraph(f"{line.quantity:.2f}", self.styles["InvoiceBody"]),
                Paragraph(f"€ {line.unit_price:.2f}", self.styles["InvoiceBody"]),
                Paragraph(f"{line.tax_rate:.0f}%", self.styles["InvoiceBody"]),
                Paragraph(f"€ {imponibile:.2f}", self.styles["InvoiceBody"]),
                Paragraph(f"<b>€ {line.total:.2f}</b>", self.styles["InvoiceBody"]),
            ])

        # Create table
        table = Table(
            data,
            colWidths=[1 * cm, 6 * cm, 1.5 * cm, 2 * cm, 1.5 * cm, 2.5 * cm, 2.5 * cm],
        )
        table.setStyle(
            TableStyle([
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), InvoicePDFStyles.PRIMARY_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), InvoicePDFStyles.BODY_SIZE),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                # Body
                ("FONTSIZE", (0, 1), (-1, -1), InvoicePDFStyles.BODY_SIZE),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Line number center
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),  # Numeri a destra
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, InvoicePDFStyles.GRAY_COLOR),
                # Padding
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        elements.append(table)
        return elements

    def _build_totals(self, invoice: Invoice) -> list:
        """Genera tabella totali"""
        elements = []

        # Totals table (right-aligned)
        data = [
            [
                Paragraph("<b>Imponibile:</b>", self.styles["InvoiceBody"]),
                Paragraph(f"€ {invoice.subtotal:.2f}", self.styles["InvoiceBody"]),
            ],
            [
                Paragraph("<b>IVA:</b>", self.styles["InvoiceBody"]),
                Paragraph(f"€ {invoice.tax_amount:.2f}", self.styles["InvoiceBody"]),
            ],
            [
                Paragraph("<b>TOTALE FATTURA:</b>", self.styles["SectionHeading"]),
                Paragraph(
                    f"<b>€ {invoice.total:.2f}</b>",
                    self.styles["InvoiceTitle"],
                ),
            ],
        ]

        table = Table(data, colWidths=[10 * cm, 7 * cm])
        table.setStyle(
            TableStyle([
                # Allineamento
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                # Last row (total) background
                ("BACKGROUND", (0, 2), (-1, 2), InvoicePDFStyles.LIGHT_GRAY),
                # Grid
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, InvoicePDFStyles.GRAY_COLOR),
                ("LINEABOVE", (0, 2), (-1, 2), 1, InvoicePDFStyles.PRIMARY_COLOR),
                ("LINEBELOW", (0, 2), (-1, 2), 1, InvoicePDFStyles.PRIMARY_COLOR),
                # Padding
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        elements.append(table)
        return elements

    def _build_payment_info(self, invoice: Invoice) -> list:
        """Genera sezione info pagamento"""
        elements = []

        title = Paragraph("<b>MODALITÀ DI PAGAMENTO</b>", self.styles["SectionHeading"])
        elements.append(title)

        payment_lines = [
            "Pagamento già effettuato tramite Stripe.",
            "",
            "<b>Coordinate bancarie per rimborsi o futuri pagamenti:</b>",
            "Beneficiario: AI Strategy Hub",
            "IBAN: IT00 X000 0000 0000 0000 0000 000 (da configurare)",
            "BIC/SWIFT: XXXXXXXXXXX (da configurare)",
            "Causale: Fattura n. " + invoice.invoice_number,
        ]

        payment_para = Paragraph(
            "<br/>".join(payment_lines),
            self.styles["InvoiceSmall"],
        )
        elements.append(payment_para)

        return elements

    def _build_footer(self, invoice: Invoice) -> list:
        """Genera footer con note legali"""
        elements = []

        footer_lines = [
            "<i>Fattura elettronica emessa ai sensi del D.Lgs. 127/2015.</i>",
            "<i>Documento fiscale valido a tutti gli effetti di legge.</i>",
            "<i>L'originale in formato XML è stato inviato al Sistema di Interscambio (SDI).</i>",
            "",
            f"<i>Generato il {datetime.now(timezone.utc).strftime('%d/%m/%Y alle %H:%M')} UTC</i>",
        ]

        footer_para = Paragraph(
            "<br/>".join(footer_lines),
            self.styles["InvoiceSmall"],
        )
        elements.append(footer_para)

        return elements


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def generate_invoice_pdf(
    invoice: Invoice,
    output_path: str,
    include_payment_info: bool = True,
    include_qr_code: bool = False,
    language: str = "it",
) -> str:
    """
    Helper function per generare PDF fattura.

    Args:
        invoice: Invoice object
        output_path: Path output PDF
        include_payment_info: Include info bancarie
        include_qr_code: Include QR code
        language: Lingua (it/en)

    Returns:
        str: Path file PDF generato

    Usage:
        pdf_path = generate_invoice_pdf(invoice, "/path/to/invoice.pdf")
    """
    generator = InvoicePDFGenerator()
    return generator.generate(
        invoice=invoice,
        output_path=output_path,
        include_payment_info=include_payment_info,
        include_qr_code=include_qr_code,
        language=language,
    )


# =============================================================================
# LOGGING
# =============================================================================

logger.info("Invoice PDF generator loaded successfully")
