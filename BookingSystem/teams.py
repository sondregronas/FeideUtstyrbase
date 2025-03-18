from datetime import datetime
from multiprocessing import Process

import flask
import markupsafe
import msteamsapi as ms
import pymsteams

import inventory
from __init__ import TEAMS_WEBHOOKS, TEAMS_WEBHOOKS_DEVIATIONS, DEBUG, TEAMS_MSG_WEBHOOK
from db import Settings
from sanitizer import APIException


########################
# INDIVIDUAL MESSAGING #
########################


def get_overdue_users(items: list) -> list[dict]:
    """Returns a list of dicts with {"name": str, "email": str, "items": list[str]}."""
    users = {}
    for item in items:
        if item.lender_email not in users:
            users[item.lender_email] = {
                "name": item.lender_name.split(" ")[0],
                "email": item.lender_email,
                "items": [],
            }
        users[item.lender_email]["items"].append(item.message_repr())
    return list(users.values())


def format_user_message(user: dict) -> str:
    """Return a formatted message for a user."""
    items_list = "\n".join(user["items"])
    return f"""\
<h1>Hei {user["name"]}!</h1>
Du står registrert med følgende utstyr som er på overtid:

{items_list}

<i>Vennligst lever utstyret tilbake så snart som mulig, eller ta kontakt med din kontaktlærer ved behov.
<br>Denne meldingen er automatisk generert og kan ikke besvares.</i>"""


def _message_users(users_pairs: list[dict]):  # pragma: no cover
    if not TEAMS_MSG_WEBHOOK:
        print("No Teams message webhook configured.")
        return

    webhook = ms.TeamsWebhook(TEAMS_MSG_WEBHOOK)

    for user in users_pairs:
        if not user["email"]:
            continue
        webhook.add_cards(ms.AdaptiveCard())
        webhook.payload["attachments"][-1]["message"] = format_user_message(user)
        webhook.payload["attachments"][-1]["recipient"] = user["email"]

    try:
        webhook.send()
    except Exception:
        print(f"Failed to send message to student, error with the webhook.")


def message_users(users: list[dict]) -> None:
    Process(target=_message_users, args=(users,)).start()


########################
# TEAMS CHANNEL REPORT #
########################


def get_overdue_items_pairs(items: list) -> dict:
    """Return a dictionary of overdue items grouped by lender association (in html representation)."""
    pairs = {
        item.lender_association_html: [
            item2.html_repr()
            for item2 in items
            if item2.lender_association_html == item.lender_association_html
        ]
        for item in items
    }
    return {key: pairs[key] for key in sorted(pairs) if pairs[key]}


def formatted_overdue_items(items: list) -> str:
    """Return formatted HTML string of overdue items."""
    if not items:
        return ""
    pairs = get_overdue_items_pairs(items)

    strings = [
        '<table bordercolor="black" border="1" style="width: 100%;">'
        + '<tr style="background-color: teal; color: white;">'
        + f'<th>&nbsp;Tilhørighet: {association or "Ansatt"}</th>'
        + "</tr>\n"
        + "\n".join([f"<tr><td>&nbsp;{item}</td></tr>" for item in pairs[association]])
        + "</table>"
        for association in pairs.keys()
    ]
    return (
        '<blockquote style="border-color: #FF0000;">'
        + "<br>".join(strings)
        + "</blockquote>"
        + "\n<small><i>Dersom du kjenner igjen utlåneren, vennligst få dem til å levere utstyret tilbake ASAP.</i></small>"
    )


def formatted_deviation(deviation: str) -> str:
    """Return formatted HTML string of new deviations."""
    if not deviation:
        raise APIException("Ingen avvik å rapportere.", 400)
    return (
        '<blockquote style="border-color: #FF0000;">'
        + str(markupsafe.escape(deviation))
        + "</blockquote>"
        + "<small><i><b>NB:</b> Avvik må oppfølges manuelt av dere mennesker, jeg kan kun varsle om nye avvik.</i></small>"
    )


def generate_card(title, text, color, webhook=None) -> pymsteams.connectorcard:
    """Generate a teams card."""
    card = pymsteams.connectorcard(webhook)
    card.title(title)
    card.color(color)
    card.text(text)
    return card


def last_sent_within_hour_treshold() -> float | int | str:
    """Return True if the last report was sent less than an hour ago."""
    last_sent = Settings.get("report_last_sent") or 0
    if last_sent and datetime.now().timestamp() - float(last_sent) < 3600:
        raise APIException(
            "Rapport ble ikke sendt: forrige rapport ble sendt for under en time siden.",
            400,
        )
    Settings.set("report_last_sent", str(datetime.now().timestamp()))
    return last_sent


def get_overdue_card(overdue_items: list) -> pymsteams.connectorcard:
    """Return a card with overdue items."""
    return generate_card(
        title="Utlån på overtid",
        text=formatted_overdue_items(overdue_items),
        color="FFA500",
    )


def get_deviation_card(deviation: str) -> pymsteams.connectorcard:
    """Return a card with new deviations."""
    title, text = deviation.split(":", 1)
    return generate_card(
        title=title, text=formatted_deviation(f"Melding: {text}"), color="FFA500"
    )


def _send_card(card):
    try:
        card.send()
    except pymsteams.TeamsWebhookException as e:
        # TODO: Update bulletin or send an email to the admin
        print(f"Failed to send card to webhook ({e})")
        pass


def send_card_to_hooks(
    card: pymsteams.connectorcard, webhooks: list[str]
) -> None:  # pragma: no cover
    """Send a card to all webhooks."""
    for webhook in webhooks:
        card.newhookurl(webhook)
        Process(target=_send_card, args=(card,)).start()


def send_deviation(deviation: str) -> flask.Response:  # pragma: no cover
    """
    Send a deviation to all webhooks in TEAMS_WEBHOOKS_DEVIATIONS.

    Args:
        deviation: The formatted deviation string.

    Returns:
        None (sends a card asynchronously).
    """
    deviation_webhooks = (
        TEAMS_WEBHOOKS_DEVIATIONS if TEAMS_WEBHOOKS_DEVIATIONS else TEAMS_WEBHOOKS
    )

    if not deviation_webhooks:
        raise APIException("Avvik ikke sendt: webhooks er ikke konfigurert", 400)

    if not deviation:
        raise APIException("Avvik ikke sendt: avviket er tomt", 400)

    card = get_deviation_card(deviation)
    send_card_to_hooks(card, deviation_webhooks)
    return flask.Response("Avvik sendt til alle konfigurerte teamskanaler!", 200)


def send_report() -> flask.Response:  # pragma: no cover
    """Send a report card to all webhooks in TEAMS_WEBHOOKS."""
    # Throw exception if last report was sent less than an hour ago
    if not Settings.get("send_reports") == "1":
        raise APIException("Rapport ikke sendt: rapporter er deaktivert", 400)

    if not DEBUG:
        last_sent_within_hour_treshold()

    if not TEAMS_WEBHOOKS:
        raise APIException("Rapport ikke sendt: webhooks er ikke konfigurert", 400)

    overdue_items = inventory.get_all_overdue()
    overdue_users = get_overdue_users(overdue_items)

    if not overdue_items:
        raise APIException("Rapport ikke sendt, ingen utlån på overtid", 400)

    if overdue_items:
        send_card_to_hooks(get_overdue_card(overdue_items), TEAMS_WEBHOOKS)
        message_users(overdue_users)

    # Return 200 OK, even if some webhooks failed (the process is async, so we can't catch exceptions)
    return flask.Response('Rapport ble sendt til alle brukere og kanaler!', 200)