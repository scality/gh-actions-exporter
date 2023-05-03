import jwt
import time
import os

class JWTGenerator:
    def __init__(self) -> None:
        self.private_pem: str = os.environ.get("PRIVATE_PEM", "")
        self.app_id: int = int(os.environ.get("APP_ID", ""))
        self.signing_key = jwt.jwk_from_pem(self.private_pem.encode())

    def generate_jwt(self) -> bytes:
        payload: dict = {
            # Issued at time
            'iat': int(time.time()),
            # JWT expiration time (10 minutes maximum)
            'exp': int(time.time()) + 600,
            # GitHub App's identifier
            'iss': self.app_id
        }

        # Create JWT
        jwt_instance = jwt.JWT()
        encoded_jwt: bytes = jwt_instance.encode(payload, self.signing_key, alg='RS256')
        return encoded_jwt
