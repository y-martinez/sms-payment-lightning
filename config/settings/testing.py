import os
from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(os.path.dirname(__name__))


class Testing(Common):
    DEBUG = True
    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    INSTALLED_APPS += ("django_nose",)
    TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
    NOSE_ARGS = [
        ROOT_DIR,
        "-s",
        "--nologcapture",
        "--with-coverage",
        "--cover-package=api",
        "--cover-package=app",
        "--verbosity=2",
    ]

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    LND_REST = {
        "ENDPOINT": "https://example.com:9876",
        "MACAROON": "TEXT",
        "CERT": "tls.cert",
    }

    # Blockcypher Settings
    BLOCKCYPHER = {
        "TOKEN": "TOKEN",
        "COIN": "btc"
    }