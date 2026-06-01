from nephthys.database.enums import TicketStatus
from nephthys.database.tables import Ticket
from nephthys.utils.env import env


async def update_channel_topic():
    """
    Update the BTS channel topic to include the latest ticket stats.

    Should only be called if the chanel topic is managed by the bot.
    """
    if not env.transcript.bts_channel_topic:
        raise ValueError("bts_channel_topic is not present in the transcript")

    open_tickets = await Ticket.count().where(Ticket.status == TicketStatus.OPEN)
    in_progress_tickets = await Ticket.count().where(
        Ticket.status == TicketStatus.IN_PROGRESS
    )
    unresolved_tickets = open_tickets + in_progress_tickets

    await env.slack_client.conversations_setTopic(
        channel=env.slack_bts_channel,
        topic=env.transcript.bts_channel_topic.replace(
            "(open_tickets)", str(open_tickets)
        )
        .replace("(in_progress_tickets)", str(in_progress_tickets))
        .replace("(unresolved_tickets)", str(unresolved_tickets)),
    )
