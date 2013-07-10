import datetime
import os
import time

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import mail_admins
from django.core.management.base import NoArgsCommand

from django_mailer.engine import LOCK_PATH


class Command(NoArgsCommand):
    """
    See logic at https://github.com/ptone/django-mailer-2/blob/master/django_mailer/engine.py
    it's possible for the mailer to get hung up and not recover, so let's check this file
    every X minutes to make sure it's not very old.
    """
    help = "Clean out cover images that never made it past the temp folder"

    def handle_noargs(self, **options):
        if not os.path.exists(LOCK_PATH):
            return
        threshold = time.mktime(
            (datetime.datetime.now() - datetime.timedelta(minutes=4)).timetuple())
        if os.path.getmtime(LOCK_PATH) < threshold:
            try:
                os.unlink(LOCK_PATH)
            except Exception:
                site = Site.objects.get_current()
                mail_admins("Mail sending is locked on %s" % site,
                            "Mail sending on this server appears to be stuck")
