#!/usr/bin/env  python3

""" sendmail.py - Send an html message with smtplib

    Used the template from here:
        https://docs.python.org/3/library/email.examples.html#email-examples
"""

import smtplib
from email.mime.text import MIMEText


def sendMessage(destination, subject, message):
    smtpserver = 'smtp.dreamhost.com'
    # https://docs.python.org/2/library/email-examples.html
    msg = MIMEText(message, 'html')

    msg['Subject'] = subject
    msg['From'] = "alerts@stormpeak.net"
    msg['To'] = "Micheal.Burin@colorado.edu"

    s = smtplib.SMTP_SSL(host=smtpserver, timeout=1000)

    try:
        s.login('alerts@stormpeak.net', 'brewerseye')
        s.sendmail(msg['From'], msg['To'], msg.as_string())

    except smtplib.SMTPHeloError:
        return {'error': False, 'msg': "The server didn't reply properly to the HELO greeting"}

    except smtplib.SMTPAuthenticationError:
        return {'error': False, 'msg': "Authentication failed to " + smtpserver}

    except smtplib.SMTPNotSupportedError:
        return {'error': False, 'msg': "The AUTH command is not supported by the server"}

    except smtplib.SMTPException:
        return {'error': False, 'msg': "No suitable authentication method was found"}

    s.quit()
