from prometheus_client import Gauge

from nephthys.utils.env import env

base_url = env.base_url

OVERALL_UP = Gauge(
    "nephthys_overall_up", "Whether Nephthys is healthy overall or not", ["base_url"]
)
SLACK_UP = Gauge("nephthys_slack_up", "Whether Slack is reachable or not", ["base_url"])
DATABASE_UP = Gauge(
    "nephthys_database_up", "Whether the database is reachable or not", ["base_url"]
)


async def update_metrics():
    """Updates the ticket-related metrics.

    Updates metrics for the support channel, e.g. number of open tickets,
    time to resolution, etc. Note that other metrics like HTTP request
    statistics and performance timers are updated elsewhere.
    """
    pass
    # stats = await calculate_overall_stats()
    # OVERALL_UP.labels(base_url).set(1)
