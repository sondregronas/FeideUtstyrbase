import os
import smtplib
import sqlite3
from datetime import datetime

import flask

import inventory
from __init__ import DATABASE, logger
from sanitizer import APIException

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT')) if os.getenv('SMTP_PORT') else 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM = os.getenv('SMTP_FROM')


def get_all_emails() -> list[str]:
    """Return a list of all emails in the database."""
    con = sqlite3.connect(DATABASE)
    emails = [row[0] for row in con.execute('SELECT email FROM emails ORDER BY email')]
    con.close()
    return emails


def get_last_sent() -> str | bool:
    """Return the date of the last sent email."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    sql = 'SELECT timestamp FROM email_report_info ORDER BY timestamp DESC LIMIT 1'
    cur.execute(sql)
    row = cur.fetchone()
    con.close()
    if row:
        return row[0]
    return False


def update_last_sent() -> None:
    """Write the current date to 'data/last_sent.txt'."""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    # noinspection SqlWithoutWhere
    sql = 'DELETE FROM email_report_info'
    cur.execute(sql)
    sql = 'INSERT INTO email_report_info (timestamp) VALUES (:timestamp)'
    cur.execute(sql, {'timestamp': datetime.now().timestamp()})
    con.commit()
    con.close()


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
    pairs = {item.lender_association_mail: [item2.mail_repr()
                                            for item2 in items
                                            if item2.lender_association_mail == item.lender_association_mail]
             for item in items}
    sorted_pairs = {key: pairs[key] for key in sorted(pairs) if pairs[key]}
    w = '<td width="10" style="width: 10px;"></td>'
    wh = '<th width="10" style="width: 10px; line-height: 1px;"></th>'
    h = '<tr><td height="10" style="height: 10px; line-height: 1px;"></td></tr>'
    strings = [f'<table class="association"><tr>{wh}<th><b>{key or "Ansatt"}</b></th>{wh}</tr>{h}\n' +
               '\n'.join([f'<tr>{w}<td>{item}</td>{w}</tr>'
                          for item in sorted_pairs[key]]) +
               f'{h}</table><br><br>'
               for key in sorted_pairs.keys()]

    return '\n'.join(strings)


def send_report() -> flask.Response:
    """Send an e-mail to all emails in the database.

    Force is for debugging only.
    """
    # If the last sent email was sent within the past hour, raise an exception
    if get_last_sent():
        if datetime.now().timestamp() - float(get_last_sent()) < 3600:
            raise APIException('Rapport ble ikke sendt: forrige rapport ble sendt for under en time siden.', 400)

    items = [item for item in inventory.get_all_unavailable() if item.overdue]
    if not items:
        update_last_sent()
        raise APIException('Rapport ble ikke sendt: finner ikke overskredet utstyr.', 400)

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
table {{width: 80%;border-collapse: collapse;border: 1px solid #ddd;}}
table th {{text-align: left; background-color: #333;color: white; height: 30px; vertical-align: middle;}}
</style>

<h1>Rapport for utlånt utstyr</h1>
<p>Hei!
<br>Her er en rapport for utlånt utstyr som er på overtid:</p>
<br>

{formatted_overdue_items()}

<p>Dersom du kjenner igjen utlåneren, vennligst få dem til å levere utstyret tilbake ASAP.</p>

<p>Med vennlig hilsen,
<br>{SMTP_FROM}</p>
""".encode('utf-8')
            server.sendmail(SMTP_USERNAME, recipients, message)
    # TODO: Handle exceptions properly
    except Exception as e:
        logger.warning(f'Failed to send email: {e}')
        raise APIException('Klarte ikke sende rapport, prøv igjen eller kontakt en administrator.', 500)
    update_last_sent()
    return flask.Response('Rapport sendt!', status=200)
