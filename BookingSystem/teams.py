from datetime import datetime
from multiprocessing import Process

import flask
import markupsafe
import pymsteams

import inventory
from __init__ import TEAMS_WEBHOOKS, TEAMS_WEBHOOKS_DEVIATIONS, DEBUG
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
        '</tr>\n' +
        '\n'.join([f'<tr><td>&nbsp;{item}</td></tr>' for item in pairs[association]]) +
        '</table>'
        for association in pairs.keys()]
    return '<blockquote style="border-color: #FF0000;">' + \
           '<br>'.join(strings) + \
           '</blockquote>' + \
           '\n<small><i>Dersom du kjenner igjen utlåneren, vennligst få dem til å levere utstyret tilbake ASAP.</i></small>'


def formatted_deviation(deviation: str) -> str:
    """Return formatted HTML string of new deviations."""
    if not deviation:
        raise APIException('Ingen avvik å rapportere.', 400)
    return '<blockquote style="border-color: #FF0000;">' + \
           str(markupsafe.escape(deviation)) + \
           '</blockquote>' + \
           '<small><i><b>NB:</b> Avvik må oppfølges manuelt av dere mennesker, jeg kan kun varsle om nye avvik.</i></small>'


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


def get_deviation_card(deviation: str) -> pymsteams.connectorcard:
    """Return a card with new deviations."""
    title, text = deviation.split(':', 1)
    return generate_card(title=title,
                         text=formatted_deviation(f'Melding: {text}'),
                         color='FFA500')


def send_card_to_hooks(card: pymsteams.connectorcard, webhooks: list[str]) -> None:  # pragma: no cover
    """Send a card to all webhooks."""
    for webhook in webhooks:
        card.newhookurl(webhook)
        Process(target=card.send).start()


def send_deviation(deviation: str) -> flask.Response:  # pragma: no cover
    """
    Send a deviation to all webhooks in TEAMS_WEBHOOKS_DEVIATIONS.

    Args:
        deviation: The formatted deviation string.

    Returns:
        None (sends a card asynchronously).
    """
    deviation_webhooks = TEAMS_WEBHOOKS_DEVIATIONS if TEAMS_WEBHOOKS_DEVIATIONS else TEAMS_WEBHOOKS

    if not deviation_webhooks:
        raise APIException('Avvik ikke sendt: webhooks er ikke konfigurert', 400)

    if not deviation:
        raise APIException('Avvik ikke sendt: avviket er tomt', 400)

    card = get_deviation_card(deviation)
    send_card_to_hooks(card, deviation_webhooks)
    return flask.Response('Avvik sendt til alle konfigurerte teamskanaler!', 200)


def send_report() -> flask.Response:  # pragma: no cover
    """Send a report card to all webhooks in TEAMS_WEBHOOKS."""
    # Throw exception if last report was sent less than an hour ago
    if not DEBUG:
        last_sent_within_hour_treshold()

    if not TEAMS_WEBHOOKS:
        raise APIException('Rapport ikke sendt: webhooks er ikke konfigurert', 400)

    overdue_items = inventory.get_all_overdue()

    if not overdue_items:
        raise APIException('Rapport ikke sendt, ingen utlån på overtid', 400)

    if overdue_items:
        send_card_to_hooks(get_overdue_card(overdue_items), TEAMS_WEBHOOKS)

    # Return 200 OK, even if some webhooks failed (the process is async, so we can't catch exceptions)
    return flask.Response('Rapport ble sendt til alle konfigurerte teamskanaler!', 200)
