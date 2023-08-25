from datetime import datetime

import flask
import markupsafe
import pymsteams
from dateutil.parser import parser

import audits
import inventory
from __init__ import TEAMS_WEBHOOKS
from db import Settings
from sanitizer import APIException


def update_last_sent() -> None:
    """Write the current date to 'data/last_sent.txt'."""
    Settings.set('report_last_sent', str(datetime.now().timestamp()))


def formatted_overdue_items(items: list) -> str:
    """Return formatted HTML string of overdue items."""
    if not items:
        return ''
    pairs = {item.lender_association_mail: [item2.mail_repr()
                                            for item2 in items
                                            if item2.lender_association_mail == item.lender_association_mail]
             for item in items}
    sorted_pairs = {key: pairs[key] for key in sorted(pairs) if pairs[key]}

    strings = [
        f'<table bordercolor="black" border="1"><tr style="background-color: teal; color: white;"><th><b>&nbsp;{key or "Ansatt"}</b></th></tr>\n' +
        '\n'.join([f'<tr><td>&nbsp;{item}</td></tr>' for item in sorted_pairs[key]]) +
        f'</table><br>'
        for key in sorted_pairs.keys()]
    return '\n'.join(strings) + \
           '\n<i>Dersom du kjenner igjen utlåneren, vennligst få dem til å levere utstyret tilbake ASAP.</i>'


def formatted_new_deviations(deviations: list) -> str:
    """Return formatted HTML string of new deviations."""
    if not deviations:
        return ''
    return '\n'.join([f'<li><b>{markupsafe.escape(deviation)}</b></li>' for deviation in deviations])


def send_report_to_hook(webhook: str = None):
    """Send a report to a webhook."""
    last_sent = Settings.get('report_last_sent') or 0
    if last_sent:
        if datetime.now().timestamp() - float(last_sent) < 3600:
            raise APIException('Rapport ble ikke sendt: forrige rapport ble sendt for under en time siden.', 400)

    overdue_items = [item for item in inventory.get_all_unavailable() if item.overdue]
    new_deviations = [audit['message'] for audit in audits.get_all()
                      if parser().parse(audit['timestamp']) > datetime.fromtimestamp(float(last_sent))
                      and audit['event'] == 'AVVIK']

    if overdue_items:
        report = pymsteams.connectorcard(webhook)
        report.title('Overskredet lån')
        report.text(formatted_overdue_items(overdue_items))
        report.send()
    if new_deviations:
        report = pymsteams.connectorcard(webhook)
        report.title('Nye avvik')
        report.text(formatted_new_deviations(new_deviations))
        report.send()

    update_last_sent()


def send_report() -> flask.Response:
    """Send a report card to all webhooks in TEAMS_WEBHOOKS."""
    if TEAMS_WEBHOOKS == ['']:
        raise APIException('Rapport ble ikke sendt: webhooks er ikke konfigurert', 400)
    for webhook in TEAMS_WEBHOOKS:
        try:
            send_report_to_hook(webhook)
            return flask.Response('Rapport sendt!', status=200)
        except pymsteams.TeamsWebhookException:
            raise APIException('Rapport ble ikke sendt: ugyldig webhook.', 400)
