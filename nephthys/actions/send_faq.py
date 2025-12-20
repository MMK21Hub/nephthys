import logging
from typing import Any
from typing import Dict

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.macros.resolve import resolve
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket
from prisma.enums import TicketStatus
from prisma.models import Ticket
from prisma.models import User


async def send_faq_link_callback(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    action = body.get("actions", [])[0]
    if not action:
        logging.error("No action provided to send_faq_link_callback")
        return
    ticket_id = action.get("value")
    if not ticket_id:
        logging.error("No Slack action value provided in send_faq_link_callback")
        return
    ticket = await env.db.ticket.find_unique(where={"id": int(ticket_id)})
    if not ticket:
        logging.error(f"Invalid ticket ID ({ticket_id}) provided in Slack action value")
        return
    helper_slack_id = body["user"]["id"]
    helper = await env.db.user.find_unique(where={"slackId": helper_slack_id})
    if not helper:
        logging.error(
            f"User interacting with FAQ macro not found in database: {helper_slack_id}"
        )
        return
    if ticket.status == TicketStatus.CLOSED:
        logging.warning(
            f"Ignoring FAQ macro interaction on closed ticket (button clicked twice?) ticket_id={ticket.id}"
        )
        return
    await send_plain_faq_link_and_close(ticket, helper)


async def send_plain_faq_link_and_close(ticket: Ticket, helper: User):
    author = await env.db.user.find_unique(where={"id": ticket.openedById})
    if not author:
        logging.error(f"Failed to find ticket author in database: {ticket.openedById}")
        return
    user = await get_user_profile(author.slackId)
    await reply_to_ticket(
        text=env.transcript.faq_macro.replace("(user)", user.display_name()),
        ticket=ticket,
        client=env.slack_client,
    )
    await resolve(
        ts=ticket.msgTs,
        resolver=helper.slackId,
        client=env.slack_client,
        send_resolved_message=False,
    )
