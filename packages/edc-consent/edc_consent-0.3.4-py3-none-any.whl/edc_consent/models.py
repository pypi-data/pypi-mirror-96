import sys

from django.conf import settings

if settings.APP_NAME == "edc_consent" and "makemigrations" not in sys.argv:
    from .tests import models  # noqa
