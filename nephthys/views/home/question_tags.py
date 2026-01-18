from blockkit import Header
from blockkit import Home
from blockkit import Section

from nephthys.views.home.components.header import get_header_components
from prisma.models import User


async def get_question_tags_view(user: User | None) -> dict:
    header = get_header_components(user, "question-tags")
    # is_admin = bool(user and user.admin)
    # is_helper = bool(user and user.helper)
    # tags = await env.db.questiontag.find_many(include={"tickets": True})

    view = Home()
    for component in header:
        view.add_block(component)
    view = (
        view.add_block(Header(":rac_info: Manage Question Tags"))
        .add_block(
            Section(
                "question tags let you label and track recurring questions and issues"
            )
        )
        .add_block(Section(" "))
        .add_block(Section("hiii"))
    )

    return view.build()
