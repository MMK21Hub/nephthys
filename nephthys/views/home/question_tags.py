from datetime import datetime
from datetime import timedelta
from datetime import UTC

from blockkit import Button
from blockkit import Divider
from blockkit import Header
from blockkit import Home
from blockkit import Section

from nephthys.utils.env import env
from nephthys.views.home.components.header import get_header_components
from prisma.enums import TicketStatus
from prisma.models import QuestionTag
from prisma.models import User


def get_tickets_count_text(tag: QuestionTag) -> str:
    if not tag.tickets:
        return "No tickets tagged yet"
    total = len(tag.tickets)
    total_str = f"{total} total tickets" if total != 1 else "1 total ticket"
    unresolved_tickets = len(
        [t for t in tag.tickets if not t.status == TicketStatus.CLOSED]
    )
    unresolved_tickets_str = (
        f"{unresolved_tickets} unresolved tickets"
        if unresolved_tickets != 1
        else "1 unresolved ticket"
    )
    tickets_from_past_day = len(
        [t for t in tag.tickets if t.createdAt >= datetime.now(UTC) - timedelta(days=1)]
    )
    tickets_from_past_day_str = (
        f"{tickets_from_past_day} questions in past 24h"
        if tickets_from_past_day != 1
        else "1 question in past 24h"
    )
    return f"{unresolved_tickets_str}, {tickets_from_past_day_str}, {total_str}"


async def get_question_tags_view(user: User | None) -> dict:
    header = get_header_components(user, "question-tags")
    is_helper = bool(user and user.helper)
    tags = await env.db.questiontag.find_many(include={"tickets": True})

    view = Home()
    for component in header:
        view.add_block(component)
    view = (
        view.add_block(Header(":rac_info: Manage Question Tags"))
        .add_block(
            Section(
                "question tags let us label and track recurring questions and issues!"
            )
        )
        .add_block(Section(" "))
    )
    for tag in sorted(tags, key=lambda t: len(t.tickets or []), reverse=True):
        button = (
            Button("Edit", action_id="edit-question-tag", value=str(tag.id))
            if is_helper
            else None
        )
        section = Section(
            f"*{tag.label}*\n"  #
            f"{get_tickets_count_text(tag)}"
        ).accessory(button)
        view.add_block(Divider())
        view.add_block(section)

    return view.build()
