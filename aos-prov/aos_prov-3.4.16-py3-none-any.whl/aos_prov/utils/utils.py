#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#

import random
import string

CONTENT_ENCRYPTION_ALGORITHM = "aes256_cbc"


def generate_random_password() -> str:
    """ Generate random password from letters and digits

        Raises:
            UserCredentialsError: If credentials files are not found
        Returns:
            String: Random string password
    """
    dictionary = string.ascii_letters + string.digits
    password_length = random.randint(10, 15)
    return ''.join(random.choice(dictionary) for _ in range(password_length))
