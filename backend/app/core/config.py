"""
Modulo: config.py
Descrizione: Configurazione centrale dell'applicazione con Pydantic Settings
Autore: Claude per Davide
Data: 2026-01-15
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurazione centrale dell'applicazione.
    Carica valori da variabili ambiente o file .env
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # =========================================================================
    # GENERAL
    # =========================================================================
    PROJECT_NAME: str = "AI Strategy Hub"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = Field(min_length=32)

    # =========================================================================
    # DATABASE - PostgreSQL
    # =========================================================================
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "aistrategyhub"
    POSTGRES_USER: str = "aistrategyhub"
    POSTGRES_PASSWORD: str

    # Costruito dai valori sopra o override completo
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: Optional[str], info) -> str:
        """Costruisce DATABASE_URL se non fornito"""
        if v:
            return v

        # Accedi ai valori dei campi precedenti tramite info.data
        data = info.data
        return (
            f"postgresql://{data.get('POSTGRES_USER')}:{data.get('POSTGRES_PASSWORD')}"
            f"@{data.get('POSTGRES_HOST')}:{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
        )

    # =========================================================================
    # CACHE - Redis
    # =========================================================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: Optional[str], info) -> str:
        """Costruisce REDIS_URL se non fornito"""
        if v:
            return v

        data = info.data
        password = data.get("REDIS_PASSWORD")
        auth = f":{password}@" if password else ""
        return f"redis://{auth}{data.get('REDIS_HOST')}:{data.get('REDIS_PORT')}/0"

    SESSION_TTL_SECONDS: int = 604800  # 7 giorni

    # =========================================================================
    # JWT AUTHENTICATION
    # =========================================================================
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =========================================================================
    # MICROSOFT GRAPH API (Email)
    # =========================================================================
    MS_GRAPH_TENANT_ID: Optional[str] = None
    MS_GRAPH_CLIENT_ID: Optional[str] = None
    MS_GRAPH_CLIENT_SECRET: Optional[str] = None
    MS_GRAPH_SENDER_EMAIL: str = "noreply@aistrategyhub.eu"
    MS_GRAPH_SENDER_NAME: str = "AI Strategy Hub"

    # =========================================================================
    # STRIPE PAYMENTS
    # =========================================================================
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_CURRENCY: str = "eur"
    STRIPE_SUCCESS_URL: str = "https://aistrategyhub.eu/checkout/success"
    STRIPE_CANCEL_URL: str = "https://aistrategyhub.eu/checkout/cancel"

    # =========================================================================
    # CLAUDE API (Anthropic)
    # =========================================================================
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_TEMPERATURE: float = 0.7

    # RAG Settings
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K_RESULTS: int = 5

    # =========================================================================
    # FATTURAZIONE ELETTRONICA (SDI)
    # =========================================================================
    SELLER_NAME: str = "AI Strategy Hub"
    SELLER_VAT: Optional[str] = None  # Partita IVA
    SELLER_FISCAL_CODE: Optional[str] = None
    SELLER_ADDRESS: str = ""
    SELLER_CITY: str = ""
    SELLER_ZIP: str = ""
    SELLER_PROVINCE: str = ""
    SELLER_COUNTRY: str = "IT"
    SELLER_REGIME_FISCALE: str = "RF01"  # Ordinario

    SDI_PEC_EMAIL: Optional[str] = None
    SDI_PEC_PASSWORD: Optional[str] = None

    INVOICE_PREFIX: str = ""
    INVOICE_YEAR_FORMAT: str = "%Y"

    # =========================================================================
    # FRONTEND (Next.js)
    # =========================================================================
    FRONTEND_URL: str = "http://localhost:3000"

    # =========================================================================
    # SECURITY
    # =========================================================================
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://aistrategyhub.eu"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins da stringa o lista"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # MFA
    MFA_ISSUER_NAME: str = "AI Strategy Hub"
    MFA_BACKUP_CODES_COUNT: int = 10

    # =========================================================================
    # EMAIL TEMPLATES
    # =========================================================================
    EMAIL_FROM_NAME: str = "AI Strategy Hub"
    EMAIL_SUPPORT_ADDRESS: str = "support@aistrategyhub.eu"
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 1

    # =========================================================================
    # FILE STORAGE
    # =========================================================================
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "doc", "txt", "md", "png", "jpg", "jpeg", "gif", "webp"]

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        """Parse allowed extensions da stringa o lista"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    # =========================================================================
    # LOGGING
    # =========================================================================
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"  # json | text
    LOG_DIR: str = "/app/logs"

    # =========================================================================
    # BACKUP
    # =========================================================================
    BACKUP_DIR: str = "/backups"
    BACKUP_RETENTION_DAYS: int = 7

    # =========================================================================
    # PRODUCTION ONLY
    # =========================================================================
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
    DOMAIN: Optional[str] = None
    SENTRY_DSN: Optional[str] = None

    # =========================================================================
    # Computed Properties
    # =========================================================================

    @property
    def is_production(self) -> bool:
        """Check se siamo in ambiente production"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check se siamo in ambiente development"""
        return self.ENVIRONMENT == "development"


# Singleton instance
settings = Settings()


# Logging configurazione caricata
if __name__ == "__main__":
    print("=" * 80)
    print("AI Strategy Hub - Configuration Loaded")
    print("=" * 80)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Redis: {settings.REDIS_URL}")
    print(f"Frontend URL: {settings.FRONTEND_URL}")
    print("=" * 80)
