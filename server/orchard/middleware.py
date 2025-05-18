import jwt
import requests
from django.core.cache import cache
from rest_framework import authentication, exceptions

from users.models import User

CLERK_FRONTEND_API_URL = (
    "https://notable-sole-11.clerk.accounts.dev"
)


class ClerkJWTAuthentication(
    authentication.BaseAuthentication
):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith(
            "Bearer "
        ):
            return None

        token = auth_header.split(" ")[1]
        try:
            jwks = self.get_jwks()
            # print(jwks)

            public_keys = {
                key[
                    "kid"
                ]: jwt.algorithms.RSAAlgorithm.from_jwk(key)
                for key in jwks["keys"]
            }
            unverified_header = jwt.get_unverified_header(
                token
            )
            key = public_keys[unverified_header["kid"]]
            payload = jwt.decode(
                token,
                key=key,
                algorithms=["RS256"],
                options={"verify_signature": True},
            )

        except Exception as e:
            raise exceptions.AuthenticationFailed(
                f"Invalid Clerk JWT : {e}"
            )

        # sub (subject) - The user's unique identifier
        # iat (issued at) - When the token was issued
        # exp (expiration) - When the token expires
        # iss (issuer) - The Clerk instance that issued the token
        # nbf (not before) - When the token becomes valid

        clerk_id = payload["sub"]
        email = payload.get("email_address", None)
        # print(email)
        if email is None:
            raise exceptions.AuthenticationFailed(
                f"received payload without email bruh: {payload}"
            )
        user, _ = User.objects.get_or_create(
            username=clerk_id, defaults={"email": email}
        )
        return (user, None)

    def get_jwks(self):
        jwks_data = cache.get("jwks_data")
        if not jwks_data:
            response = requests.get(
                f"{CLERK_FRONTEND_API_URL}/.well-known/jwks.json"
            )
            if response.status_code == 200:
                jwks_data = response.json()
                cache.set(
                    "jwks_data", jwks_data
                )  # cache indefinitely -.- weeeeeeuuuu
            else:
                raise exceptions.AuthenticationFailed(
                    "Failed to fetch JWKS."
                )

        return jwks_data
