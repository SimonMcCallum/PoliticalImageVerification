from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    party_id: str | None = None
    role: str | None = None
    default_statement_position: str | None = None
    has_user_promoter_statement: bool = False


class MFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str
