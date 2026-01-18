from blockkit import Input
from blockkit import Modal
from blockkit import PlainTextInput

from prisma.models import QuestionTag


def edit_question_tag_modal(tag: QuestionTag):
    modal = (
        Modal("edit question tag")
        .callback_id("edit-question-tag")
        .private_metadata(str(tag.id))
        .add_block(
            Input("Edit label")
            .element(PlainTextInput(action_id="tag_label", initial_value=tag.label))
            .block_id("tag_label")
        )
        .close("cancel")
        .submit("save changes")
    )

    return modal.build()
