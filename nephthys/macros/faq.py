from nephthys.macros.types import Macro
from nephthys.utils.env import env


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
                            "action_id": "send_faq_answer",
                            "value": f"{ticket.id}",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Send normal FAQ link",
                            },
                            "action_id": "send_faq_link",
                            "value": f"{ticket.id}",
                        },
                    ],
                },
            ],
        )
