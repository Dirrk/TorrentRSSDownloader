__author__ = 'Dirrk'

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import app.plex.plex as plex
import app.settings as settings


def send_gmail(subject, html_message, **kwargs):
    account_user = kwargs.get('AccountUser', None)
    account_pwd = kwargs.get('AccountPass', None)
    account_host = kwargs.get('AccountHost', 'smtp.gmail.com')
    account_port = kwargs.get("AccountPort", 587)
    to = kwargs.get('to', account_user)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = account_user
    msg['To'] = to
    msg.attach(MIMEText(html_message, 'html'))

    try:

        server = smtplib.SMTP(account_host, account_port)
        server.ehlo()
        server.starttls()
        server.login(account_user, account_pwd)
        server.sendmail(account_user, to, msg.as_string())
        server.close()
        logging.info('Sent gmail using gmail: ' + str(subject))
        return True
    except Exception as e:
        logging.exception(e)
        logging.error("Failed to send using gmail")
        return False


def send_email_report(all_torrents, callback):
    rows_in_report = ["<html><table><tr><th>Subscription</th><th>Episode</th><th>Status</th></tr>"]
    for key in all_torrents:
        sub = callback('sub', all_torrents[key].subscriptionId)
        sub_header = key
        episode = all_torrents[key].episode
        status = all_torrents[key].status_to_string()
        if sub is not None:
            show = plex.ApiHelper().get_show_by_id(sub.plex_id)
            sub_header = show.title

        a_row = "<tr><td>" + sub_header + "</td><td>" + episode + "</td><td>" + status + "</td></tr>"
        rows_in_report.append(a_row)

    rows_in_report.append("</table></html>")
    email_data = {
        'AccountUser': settings.EMAIL_DATA['ACCOUNT']['USER'],
        'AccountPass': settings.EMAIL_DATA['ACCOUNT']['PASS'],
        'to': settings.EMAIL_DATA['TO']
    }
    send_gmail("Weekly Torrent Report", "\r\n".join(rows_in_report), **email_data)