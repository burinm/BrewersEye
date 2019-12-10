#!/usr/bin/env  python3

# Using the template from here:
# https://docs.python.org/3/library/email.examples.html#email-examples

import smtplib
from email.message import EmailMessage


def sendMessage(destination, subject, message):
    smtpserver = 'smtp.dreamhost.com'
    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = "alerts@stormpeak.net"
    msg['To'] = "Micheal.Burin@colorado.edu"

    s = smtplib.SMTP_SSL(host=smtpserver, timeout=1000)

    try:
        s.login('alerts@stormpeak.net', 'brewerseye')
        s.send_message(msg)
    except smtplib.SMTPHeloError:
        return {'error': False, 'msg': "The server didn't reply properly to the HELO greeting"}

    except smtplib.SMTPAuthenticationError:
        return {'error': False, 'msg': "Authentication failed to " + smtpserver}

    except smtplib.SMTPNotSupportedError:
        return {'error': False, 'msg': "The AUTH command is not supported by the server"}

    except smtplib.SMTPException:
        return {'error': False, 'msg': "No suitable authentication method was found"}

    s.quit()
