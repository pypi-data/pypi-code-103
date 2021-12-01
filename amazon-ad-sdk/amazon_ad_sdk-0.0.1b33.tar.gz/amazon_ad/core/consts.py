# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)

ACCOUNT_TYPES = ["agency", "vendor", "seller"]

REGIONS_ENDPOINTS = {
    "NA": {
        "AUTHORIZATION": "https://www.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.com/auth/o2/token",
        "API": "https://advertising-api.amazon.com",
    },
    "EU": {
        "AUTHORIZATION": "https://eu.account.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.co.uk/auth/o2/token",
        "API": "https://advertising-api-eu.amazon.com",
    },
    "FE": {
        "AUTHORIZATION": "https://apac.account.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.co.jp/auth/o2/token",
        "API": "https://advertising-api-fe.amazon.com",
    },
    "SANDBOX": {
        "AUTHORIZATION": "https://www.amazon.com/ap/oa",
        "TOKEN": "https://api.amazon.com/auth/o2/token",
        "API": "https://advertising-api-test.amazon.com",
    }
}

COUNTRIES_REGION = (
    ('US', 'NA'),
    ('CA', 'NA'),
    ('UK', 'EU'),
    ('DE', 'EU'),
    ('FR', 'EU'),
    ('IT', 'EU'),
    ('ES', 'EU'),
    ('AE', 'EU'),
    ('JP', 'FE'),
    ('AU', 'FE'),
    ('SANDBOX', 'SANDBOX'),
)

