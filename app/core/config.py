from pathlib import Path

from pydantic import BaseModel, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class AuthorizationConfig(BaseModel):
    algorithm: str
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    registration_token_expire_minutes: int
    changing_password_token_expire_minutes: int


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class EmailConfig(BaseModel):
    username: str
    password: str
    mail_from: str
    mail_from_name: str = "ЭСКРО"
    port: int
    server: str
    starttls: bool
    ssl_tls: bool
    use_credentials: bool


class FrontendConfig(BaseModel):
    base_url: str
    confirmation_register_url: str
    register_invitation_url: str
    changing_password_url: str
    subscription_confirmation_url: str


class AdminConfig(BaseModel):
    email: str
    username: str


class FileConfig(BaseModel):
    uploads_dir: Path = BASE_DIR / "uploads"
    allowed_image_types: set[str]
    max_file_size: int


class HeaderConfig(BaseModel):
    refresh_token_header: str


class SSLConfig(BaseModel):
    dir: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    run: RunConfig
    api: ApiPrefix
    auth: AuthorizationConfig
    db: DatabaseConfig
    email: EmailConfig
    frontend: FrontendConfig
    admin: AdminConfig
    file: FileConfig
    header: HeaderConfig
    ssl: SSLConfig

settings = Settings()
