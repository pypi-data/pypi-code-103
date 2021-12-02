import os
from typing import Type


def get_env_var(key: str, default=None, throw_if_missing=False, dtype: Type = str):
    if key not in os.environ:
        if throw_if_missing:
            raise ValueError('Missing environment variable: ', key)
        else:
            return default

    return dtype(os.getenv(key))


# General ##############################################################################################################
DEBUG: bool = get_env_var('VATIS_ASR_CLIENT_DEBUG', default='False') == 'True'

# SocketIO Client ######################################################################################################
RECONNECTION_ATTEMPTS: int = get_env_var('VATIS_ASR_CLIENT_RECONNECTION_ATTEMPTS', default=6, dtype=int)
REQUEST_TIMEOUT: float = get_env_var('VATIS_ASR_CLIENT_REQUEST_TIMEOUT_SECONDS', default=15, dtype=float)
RECONNECTION_DELAY: float = get_env_var('VATIS_ASR_CLIENT_RECONNECTION_DELAY_SECONDS', default=5)
CONNECTION_TIMEOUT: float = get_env_var('VATIS_ASR_CLIENT_CONNECTION_TIMEOUT_SECONDS', default=10, dtype=float)

# Connection config ####################################################################################################
AUTHENTICATION_PROVIDER_URL: str = get_env_var('VATIS_ASR_CLIENT_AUTHENTICATION_PROVIDER_URL', default='https://vatis.tech/api/v1/asr-client/auth')

# Security #############################################################################################################
API_KEY: str = get_env_var('VATIS_ASR_CLIENT_API_KEY', throw_if_missing=True)

# Log ##################################################################################################################
LOGS_FILE: str = get_env_var('VATIS_ASR_CLIENT_LOGS_FILE', default='logs/app.logs', dtype=str)
LOGS_FILE_ENABLED: bool = get_env_var('VATIS_ASR_CLIENT_ENABLE_LOGS_FILE', default='False') == 'True'
