"""
Modulo: contact.py
Descrizione: Schema per contact form
Autore: Claude per Davide
Data: 2026-01-16
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactFormRequest(BaseModel):
    """Richiesta contact form"""

    name: str = Field(..., min_length=1, max_length=200, description="Nome e cognome")
    email: EmailStr = Field(..., description="Email aziendale")
    company: str | None = Field(None, max_length=255, description="Azienda")
    role: str | None = Field(None, max_length=255, description="Ruolo aziendale")
    subject: str = Field(..., min_length=1, max_length=500, description="Oggetto")
    message: str = Field(..., min_length=1, max_length=5000, description="Messaggio")

    @field_validator("email")
    @classmethod
    def validate_business_email(cls, v: str) -> str:
        """
        Valida che sia un'email aziendale, non consumer.

        Blocca provider generici come Gmail, Yahoo, Hotmail, etc.
        """
        generic_providers = [
            'gmail.com',
            'yahoo.com',
            'yahoo.it',
            'hotmail.com',
            'hotmail.it',
            'outlook.com',
            'outlook.it',
            'live.com',
            'live.it',
            'icloud.com',
            'me.com',
            'libero.it',
            'virgilio.it',
            'tiscali.it',
            'alice.it',
            'tin.it',
            'fastwebnet.it',
            'protonmail.com',
            'aol.com',
        ]

        email_domain = v.split('@')[1].lower() if '@' in v else ''

        if email_domain in generic_providers:
            raise ValueError(
                f"Per favore utilizza un'email aziendale. "
                f"Provider consumer come {email_domain} non sono ammessi."
            )

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mario Rossi",
                "email": "mario@esempio.it",
                "company": "Acme S.r.l.",
                "role": "CEO",
                "subject": "Richiesta informazioni su servizi AI",
                "message": "Vorrei avere maggiori informazioni sui vostri servizi di consulenza AI compliance...",
            }
        }


class ContactFormResponse(BaseModel):
    """Risposta contact form"""

    success: bool = Field(..., description="Se invio è riuscito")
    message: str = Field(..., description="Messaggio conferma")
    reference_id: str | None = Field(None, description="ID riferimento ticket")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Richiesta inviata con successo. Ti contatteremo al più presto.",
                "reference_id": "CONT-2026-001234",
            }
        }
