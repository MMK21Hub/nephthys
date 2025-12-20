import logging

from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


async def send_plain_faq_link_and_close(ticket, helper):
    author = await env.db.user.find_unique(where={"id": ticket.openedById})
    if not author:
        # TODO: ??
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


class FAQ(Macro):
    name = "faq"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro reminding people to check the FAQ.
        """
        await env.slack_client.chat_postEphemeral(
            channel=env.slack_help_channel,
            thread_ts=ticket.msgTs,
            user=helper.slackId,
            text="Select a FAQ section to embed",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Select a question from the FAQ to embed in the ticket reply, or link to the FAQ without embedding a question.",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "static_select",
                            "action_id": "faq_question_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select a question",
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Getting Started",
                                    },
                                    "value": "getting_started",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Account Management",
                                    },
                                    "value": "account_management",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Billing and Payments",
                                    },
                                    "value": "billing_payments",
                                },
                            ],
                        }
                    ],
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Send FAQ answer",
                            },
                            "style": "primary",
                            "value": "send_faq_answer",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Send normal FAQ link",
                            },
                            "value": "send_faq_link",
                        },
                    ],
                },
            ],
        )
