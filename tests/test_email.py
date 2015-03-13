__author__ = 'Dirrk'

import unittest

from app.email.email import send_gmail as gmail
import app.settings as settings

settings.apply_settings()


class TestEmail(unittest.TestCase):
    def test_send_email(self):
        self.assertTrue(gmail("test", "testing", AccountUser=settings.EMAIL_DATA['ACCOUNT']['USER'],
                              AccountPass=settings.EMAIL_DATA['ACCOUNT']['PASS'],
                              to=settings.EMAIL_DATA['TO']))
