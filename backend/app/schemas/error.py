"""
Modulo: error.py
Descrizione: Schemas Pydantic per error reporting
Autore: Claude per Davide
Data: 2026-01-15
"""

from typing import Optional

from pydantic import BaseModel, Field


class ErrorReportRequest(BaseModel):
    """Schema per segnalazione errore da frontend"""

    error_code: str = Field(..., description="Codice errore (es: NETWORK_ERROR, AUTH_ERROR)")
    error_message: str = Field(..., description="Messaggio errore user-friendly")
    error_details: Optional[str] = Field(None, description="Dettagli tecnici errore")
    stack_trace: Optional[str] = Field(None, description="Stack trace completo")
    request_path: Optional[str] = Field(None, description="Percorso dove è avvenuto l'errore")
    user_agent: Optional[str] = Field(None, description="User agent browser")
    timestamp: Optional[str] = Field(None, description="Timestamp errore (ISO format)")


class ErrorReportResponse(BaseModel):
    """Schema per risposta segnalazione errore"""

    success: bool = Field(..., description="Se segnalazione è stata inviata")
    message: str = Field(..., description="Messaggio di conferma")
