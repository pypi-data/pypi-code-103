import time
from typing import Optional

from fastapi import Header, HTTPException
from jose import JWTError, jwt
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from leximpact_socio_fisca_simu_etat.cache import Cache
from leximpact_socio_fisca_simu_etat.config import Configuration
from leximpact_socio_fisca_simu_etat.logger import logger

config = Configuration()
cache = Cache()


def check_abuse(email):
    # TODO : Use https://github.com/brandur/redis-cell for generic cell rate algorithm (GCRA)
    # which provides a rolling time window and doesn't depend on a background drip process.
    if not cache.is_available():
        if config.get("ALLOW_REDIS_TO_FAIL", fail_on_missing=False) != "YES":
            logger.fatal(
                "No redis, please use ALLOW_REDIS_TO_FAIL=YES if not in production."
            )
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cache not available",
            )
        else:
            logger.warning("REDIS not available but ALLOW_REDIS_TO_FAIL=YES")

    if cache.is_available() and cache.is_abusing(
        email, config.get("API_MAX_CALL_PER_MINUTE_PER_USER")
    ):
        logger.warning(f"Too many calls for {email}")
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )


# JWT TOKEN
# Thanks to https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
# And https://developers.redhat.com/blog/2020/01/29/api-login-and-jwt-token-generation-using-keycloak#set_up_a_client
# to get a string like this run:
# openssl rand -hex 32
def check_token(token, secret_key):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "JWT Token"},
    )

    if not token:
        logger.warning("credentials_exception : no token")
        raise credentials_exception
    payload = {"token": token}
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        logger.info(f"We received a connection token : {payload}")
        email: str = payload.get("user").get("email")
        if email is None:
            logger.warning("credentials_exception : empty email", payload)
            raise credentials_exception
        iat = payload.get("iat")
        exp = payload.get("exp")
        if exp is None or iat is None:
            logger.warning(
                "credentials_exception : Missing date (iat or exp)",
                payload,
            )
            raise credentials_exception
        issued_at = int(iat)
        expire_at = int(exp)
        timestamp = int(time.time())
        if not ((issued_at - 300) <= timestamp <= expire_at):
            logger.warning(
                f"credentials_exception : Token date invalid {issued_at} < {timestamp=} < {expire_at=}",
                payload,
            )
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"credentials_exception : JWTError ({e}) for {payload}")
        raise credentials_exception
    except AttributeError as e:
        logger.warning(f"credentials_exception : AttributeError ({e}) for {payload}")
        raise credentials_exception
    check_abuse(email)
    # Save the access in a file
    with open("../historique_des_acces.csv", "a") as file_object:
        file_object.write(f"{email};{int(time.time())}\n")
    return email


async def get_token_header(jwt_token: Optional[str] = Header(None)):
    check_token(jwt_token, config.get("JWT_SECRET_KEY"))
