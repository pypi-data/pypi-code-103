#!/usr/bin/env python3

from os import getenv


def get_env_debug_secret_hosts():
    debug = bool(getenv("DEBUG"))
    if not getenv("SECRET_KEY") and not debug:
        raise Exception("Won't allow you to use default secret key out of DEBUG.")
    secret_key = getenv("SECRET_KEY", "j%fj4*&9kkl3#a_1a)g%mhh*a#z5$hq-$45vuyl)2x)!_)fd7x")
    allowed_hosts = getenv("ALLOWED_HOSTS", "").split()
    return debug, secret_key, allowed_hosts


def get_env_databases(base_dir):
    try:
        POSTGRES_URL = getenv("DATABASE_URL")
        DB_TYPE, _, _, PG_USERNAME, PG_PASSWORD, PG_HOST, PG_PORT, PG_NAME = (
            POSTGRES_URL.replace("@", ":").replace("/", ":").split(":")
        )
    except (ValueError, AttributeError):
        DB_TYPE, PG_USERNAME, PG_PASSWORD, PG_HOST, PG_PORT, PG_NAME = [None] * 6
    return {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": base_dir / "db.sqlite3",}
        if not PG_NAME or getenv("PG_NAME")
        else {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            **{"NAME": PG_NAME, "USER": PG_USERNAME, "PASSWORD": PG_PASSWORD, "HOST": PG_HOST, "PORT": PG_PORT},
        }
    }


def get_env_email():
    return (
        getenv("EMAIL_HOST"),
        getenv("EMAIL_HOST_USER"),
        getenv("EMAIL_HOST_PASSWORD"),
        getenv("EMAIL_PORT"),
        bool(getenv("EMAIL_USE_TLS")),
    )
