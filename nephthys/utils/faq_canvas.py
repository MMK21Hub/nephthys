from dataclasses import dataclass
from html.parser import HTMLParser

from aiohttp import ClientSession
from slack_sdk.errors import SlackApiError

from nephthys.utils.env import env


@dataclass
class FAQQuestion:
    question: str
    id: str


class MissingScopeError(Exception):
    def __init__(self, slack_error: SlackApiError):
        self.slack_error = slack_error
        super().__init__(
            f"Missing required Slack scope: {slack_error.response['needed']}"
        )


async def get_canvas_html(canvas_id: str) -> str:
    WORKSPACE_ID = "T0266FRGM"
    http_client = ClientSession(
        headers={
            "Authorization": f"Bearer {env.slack_bot_token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
        }
    )  # TODO: persist?
    url = f"https://files.slack.com/files-pri/{WORKSPACE_ID}-{canvas_id}/canvas"
    response = await http_client.get(url)
    response.raise_for_status()
    text = await response.text()
    return text


class CanvasHTMLParser(HTMLParser):
    pass


async def get_faq_questions(canvas_id: str) -> list[FAQQuestion]:
    """Gets FAQ questions from the provided FAQ canvas."""
    try:
        response = await env.slack_client.canvases_sections_lookup(
            canvas_id=canvas_id, criteria={"section_types": ["h2"]}
        )
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise MissingScopeError(e) from e
        raise
    sections = response["sections"]
    print(sections)
    await get_canvas_html(canvas_id)
