import os
import smtplib
import sqlite3
from datetime import datetime

import flask

import inventory
from __init__ import DATABASE, logger

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT')) if os.getenv('SMTP_PORT') else 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM = os.getenv('SMTP_FROM')


def get_all_emails() -> list[str]:
    """Return a list of all emails in the database."""
    con = sqlite3.connect(DATABASE)
    emails = [row[0] for row in con.execute('SELECT email FROM emails ORDER BY email ASC')]
    con.close()
    return emails


def get_last_sent() -> str | bool:
    """Return the date of the last sent email."""
    if not os.path.exists('data/last_sent.txt'):
        return False
    with open('data/last_sent.txt', 'r') as file:
        return file.read()


def update_last_sent() -> None:
    """Write the current date to 'data/last_sent.txt'."""
    with open('data/last_sent.txt', 'w+') as file:
        file.write(str(datetime.now().timestamp()))


def formatted_overdue_items() -> str:
    """
    Returns a string formatted like this from all overdue items:
    <table class="association">
        <tr>
            <th>Association (i.e. 1IM (Navn))</th>
        </tr>
        <tr>
            <td>Item 1 (i.e. Navn: ID, ItemName (Category, dd.mm.yyyy)</td>
        </tr>
        <tr>
            <td>Item 2</td>
        </tr>
    </table>
    <br><br>
    """
    items = [item for item in inventory.get_all_unavailable() if item.overdue]
    pairs = {item.lender_association: [item2
                                       for item2 in items
                                       if item2.lender_association == item.lender_association]
             for item in items}
    sorted_pairs = {key: pairs[key] for key in sorted(pairs) if pairs[key]}
    strings = [f'<table class="association"><tr><th>{key}</th></tr>\n' +
               '\n'.join([f'<tr><td>{item}</td></tr>'
                          for item in sorted_pairs[key]]) +
               '</table><br><br>'
               for key in sorted_pairs.keys()]

    return '\n'.join(strings)


def send_report() -> flask.Response:
    """Send an email to all emails in the database."""
    items = [item for item in inventory.get_all_unavailable() if item.overdue]
    if not items:
        return flask.Response('Ikke sendt (intet å rapportere!)', status=400)

    title = f'[UtstyrServer] Rapport for overskredet utstyr {datetime.now().strftime("%d.%m.%Y")}'
    recipients = get_all_emails()

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            message = f"""\
From: {SMTP_FROM} <{SMTP_USERNAME}>
To: {', '.join(recipients)}
Subject: {title}
Content-Type: text/html; charset=utf-8

<style>
table {{width: 80%;border-collapse: collapse;border: 1px solid #ddd;padding: 8px;}}
table th {{padding: 12px;text-align: left;background-color: #333;color: white;}}
table tr:nth-child(even) {{background-color: #f2f2f2;}}
</style>

<h1>Rapport for utlånt utstyr</h1>
<p>Hei!
<br>Her er en rapport for utlånt utstyr som er på overtid:</p>
<br>

{formatted_overdue_items()}

<p>Dersom du kjenner igjen utlåneren, vennligst få dem til å levere utstyret tilbake ASAP.</p>

<p>Med vennlig hilsen,
<br>UtstyrServer</p>
""".encode('utf-8')
            server.sendmail(SMTP_USERNAME, recipients, message)
    except Exception as e:
        logger.warning(f'Failed to send email: {e}')
        return flask.Response('Klarte ikke sende rapport, prøv igjen eller kontakt en administrator.', status=500)
    update_last_sent()
    return flask.Response('Rapport sendt!', status=200)
