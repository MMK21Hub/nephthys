import logging

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.events.app_home_opened import open_app_home
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.views.modals.edit_question_tag import edit_question_tag_modal


async def edit_question_tag_submit(ack: AsyncAck, body: dict, client: AsyncWebClient):
    """
    Callback for the edit question tag modal submission
    """
    await ack()
    user_id = body["user"]["id"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        logging.warning(f"Attempted to edit question tag by non-helper {user_id=}")
        await send_heartbeat(
            f"Attempted to edit question tag by non-helper user <@{user_id}>"
        )
        return

    tag_id = int(body["view"]["private_metadata"])
    label = body["view"]["state"]["values"]["tag_label"]["tag_label"]["value"]
    if not label:
        logging.warning(f"Attempted to submit empty tag label {user_id=} {tag_id=}")

    record = await env.db.questiontag.update(
        where={"id": int(tag_id)},
        data={"label": label},
    )
    if not record:
        logging.error(f"Failed to update question tag {tag_id=}")

    await open_app_home("question-tags", client, user_id)


async def edit_question_tag_open_modal(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """
    Open modal to edit a question tag
    """
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]
    tag_id = int(body["actions"][0]["value"])

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        logging.warning(f"Attempted to edit question tag by non-helper {user_id=}")
        await send_heartbeat(
            f"Attempted to open edit question tag modal by non-helper user <@{user_id}>"
        )
        return

    tag = await env.db.questiontag.find_unique(where={"id": tag_id})
    if not tag:
        logging.error(f"Attempted to edit non-existent question tag {tag_id=}")
        return

    view = edit_question_tag_modal(tag)
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)
