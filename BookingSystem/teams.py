from datetime import datetime
from multiprocessing import Process

import flask
import markupsafe
import pymsteams

import audits
import inventory
from __init__ import TEAMS_WEBHOOKS, TEAMS_WEBHOOKS_DEVIATIONS
from db import Settings
from sanitizer import APIException


def get_overdue_items_pairs(items: list) -> dict:
    """Return a dictionary of overdue items grouped by lender association (in html representation)."""
    pairs = {item.lender_association_html: [item2.html_repr()
                                            for item2 in items
                                            if item2.lender_association_html == item.lender_association_html]
             for item in items}
    return {key: pairs[key] for key in sorted(pairs) if pairs[key]}


def formatted_overdue_items(items: list) -> str:
    """Return formatted HTML string of overdue items."""
    if not items:
        return ''
    pairs = get_overdue_items_pairs(items)

    strings = [
        '<table bordercolor="black" border="1" style="width: 100%;">' +
        '<tr style="background-color: teal; color: white;">' +
        f'<th>&nbsp;Tilhørighet: {association or "Ansatt"}</th>' +
        f'</tr>\n' +
        '\n'.join([f'<tr><td>&nbsp;{item}</td></tr>' for item in pairs[association]]) +
        f'</table>'
        for association in pairs.keys()]
    return '<blockquote style="border-color: #FF0000;">' + \
           '<br>'.join(strings) + \
           '</blockquote>' + \
           '\n<small><i>Dersom du kjenner igjen utlåneren, vennligst få dem til å levere utstyret tilbake ASAP.</i></small>'


def formatted_new_deviations(deviations: list) -> str:
    """Return formatted HTML string of new deviations."""
    if not deviations:
        return ''
    return '<blockquote style="border-color: #FF0000;">' + \
           '<br>'.join([f'{markupsafe.escape(deviation)}' for deviation in deviations]) + \
           '</blockquote>' + \
           '<small><i><b>NB:</b> Avvik må registreres manuelt i notatblokken (inntil videre), jeg kan kun varsle om nye avvik.</i></small>'


def generate_card(title, text, color, webhook=None) -> pymsteams.connectorcard:
    """Generate a teams card."""
    card = pymsteams.connectorcard(webhook)
    card.title(title)
    card.color(color)
    card.text(text)
    return card


def last_sent_within_hour_treshold() -> float | int | str:
    """Return True if the last report was sent less than an hour ago."""
    last_sent = Settings.get('report_last_sent') or 0
    if last_sent and datetime.now().timestamp() - float(last_sent) < 3600:
        raise APIException('Rapport ble ikke sendt: forrige rapport ble sendt for under en time siden.', 400)
    Settings.set('report_last_sent', str(datetime.now().timestamp()))
    return last_sent


def get_overdue_card(overdue_items: list) -> pymsteams.connectorcard:
    """Return a card with overdue items."""
    return generate_card(title='Utlån på overtid',
                         text=formatted_overdue_items(overdue_items),
                         color='FFA500')


def get_deviation_card(new_deviations: list) -> pymsteams.connectorcard:
    """Return a card with new deviations."""
    return generate_card(title='Nye avvik som krever oppfølging',
                         text=formatted_new_deviations(new_deviations),
                         color='FFA500')


def send_card_to_hooks(card: pymsteams.connectorcard, webhooks: list[str]) -> None:
    """Send a card to all webhooks."""
    for webhook in webhooks:
        card.newhookurl(webhook)
        Process(target=card.send).start()


def send_report() -> flask.Response:
    """Send a report card to all webhooks in TEAMS_WEBHOOKS."""
    last_sent = last_sent_within_hour_treshold()

    if TEAMS_WEBHOOKS == ['']:
        raise APIException('Rapport ikke sendt: webhooks er ikke konfigurert', 400)
    deviation_webhooks = TEAMS_WEBHOOKS_DEVIATIONS if TEAMS_WEBHOOKS_DEVIATIONS != [''] else TEAMS_WEBHOOKS

    overdue_items = inventory.get_all_overdue()
    new_deviations = audits.get_new_deviations(since=last_sent)

    if not overdue_items and not new_deviations:
        raise APIException('Rapport ikke sendt: ingen nye avvik eller utlån på overtid', 400)

    if overdue_items:
        send_card_to_hooks(get_overdue_card(overdue_items), TEAMS_WEBHOOKS)

    if new_deviations:
        send_card_to_hooks(get_deviation_card(new_deviations), deviation_webhooks)

    # Return 200 OK, even if some webhooks failed (the process is async, so we can't catch exceptions)
    return flask.Response('Rapport ble sendt til alle konfigurerte teamskanaler!', 200)
