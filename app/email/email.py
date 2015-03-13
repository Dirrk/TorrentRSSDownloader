__author__ = 'Dirrk'

import logging
import smtplib


def send_gmail(subject, html_message, **kwargs):
    account_user = kwargs.get('AccountUser', None)
    account_pwd = kwargs.get('AccountPass', None)
    account_host = kwargs.get('AccountHost', 'smtp.gmail.com')
    account_port = kwargs.get("AccountPort", 587)
    to = [kwargs.get('to', account_user)]

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (account_user, ", ".join(to), subject, html_message)
    try:

        server = smtplib.SMTP(account_host, account_port)
        server.ehlo()
        server.starttls()
        server.login(account_user, account_pwd)
        server.sendmail(account_user, to, message)
        server.close()
        logging.info('Sent email using gmail: ' + str(subject))
        return True
    except Exception as e:
        logging.exception(e)
        logging.error("Failed to send using gmail")
        return False