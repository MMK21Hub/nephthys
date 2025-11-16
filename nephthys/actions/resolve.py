import logging
from datetime import datetime

from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.delete_thread import add_thread_to_delete_queue
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.permissions import can_resolve
from nephthys.utils.ticket_methods import delete_message
from nephthys.utils.ticket_methods import reply_to_ticket
from prisma.enums import TicketStatus
from prisma.models import Ticket


async def update_user_facing_message(ticket: Ticket):
    ts = ticket.faqMsgTs
    channel = env.slack_help_channel
    if not ts:
        logging.warning(f"FAQ message is not stored for resolved ticket {ticket.msgTs}")
        return

    faq_msg_matches = (
        await env.slack_client.conversations_history(
            channel=channel,
            latest=ts,
            inclusive=True,
            limit=1,
        )
    )["messages"]
    if not faq_msg_matches:
        logging.warning(
            f"Could not find FAQ message {ts} for resolved ticket (parent msg {ticket.msgTs})"
        )
        return

    faq_message = faq_msg_matches[0]
    for i, block in enumerate(faq_message["blocks"]):
        if block["type"] != "actions":
            continue
        for j, element in enumerate(block["elements"]):
            if element["type"] == "button" and element["action_id"] == "mark_resolved":
                faq_message["blocks"][i]["elements"][j]["text"]["text"] = (
                    "Marked as resolved"
                )
                faq_message["blocks"][i]["elements"][j]["style"] = "default"

    await env.slack_client.chat_update(
        channel=channel,
        ts=ts,
        blocks=faq_message["blocks"],
    )


async def resolve(
    ts: str,
    resolver: str,
    client: AsyncWebClient,
    stale: bool = False,
    add_reaction: bool = True,
    send_resolved_message: bool = True,
):
    resolving_user = await env.db.user.find_unique(where={"slackId": resolver})
    if not resolving_user:
        await send_heartbeat(
            f"User {resolver} attempted to resolve ticket with ts {ts} but isn't in the database.",
            messages=[f"Ticket TS: {ts}", f"Resolver ID: {resolver}"],
        )
        return

    allowed = await can_resolve(resolving_user.slackId, resolving_user.id, ts)
    if not allowed:
        await send_heartbeat(
            f"User {resolver} attempted to resolve ticket with ts {ts} without permission.",
            messages=[f"Ticket TS: {ts}", f"Resolver ID: {resolver}"],
        )
        return
    ticket = await env.db.ticket.find_first(
        where={"msgTs": ts, "NOT": [{"status": TicketStatus.CLOSED}]}
    )
    if not ticket:
        return

    if not resolving_user.helper and ticket.assignedTo:
        new_resolving_user = await env.db.user.find_unique(
            where={"id": ticket.assignedTo.id}
        )
        if new_resolving_user:
            resolving_user = new_resolving_user

    now = datetime.now()

    tkt = await env.db.ticket.update(
        where={"msgTs": ts},
        data={
            "status": TicketStatus.CLOSED,
            "closedBy": {"connect": {"id": resolving_user.id}},
            "closedAt": now,
        },
    )
    if not tkt:
        await send_heartbeat(
            f"Failed to resolve ticket with ts {ts} by {resolver}. Ticket not found.",
            messages=[f"Ticket TS: {ts}", f"Resolver ID: {resolver}"],
        )
        return

    if send_resolved_message:
        await reply_to_ticket(
            ticket=tkt,
            client=client,
            text=env.transcript.ticket_resolve.format(user_id=resolver)
            if not stale
            else env.transcript.ticket_resolve_stale.format(user_id=resolver),
        )
    if add_reaction:
        await client.reactions_add(
            channel=env.slack_help_channel,
            name="white_check_mark",
            timestamp=ts,
        )

    await client.reactions_remove(
        channel=env.slack_help_channel,
        name="thinking_face",
        timestamp=ts,
    )

    await update_user_facing_message(tkt)

    if await env.workspace_admin_available():
        await add_thread_to_delete_queue(
            channel_id=env.slack_ticket_channel, thread_ts=tkt.ticketTs
        )
    else:
        await delete_message(
            channel_id=env.slack_ticket_channel, message_ts=tkt.ticketTs
        )
