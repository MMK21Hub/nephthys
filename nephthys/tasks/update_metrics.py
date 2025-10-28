from prometheus_client import Gauge


nephthys_tickets_total = Gauge(
    "nephthys_tickets_total", "Total of all open and closed tickets"
)
nephthys_open_tickets = Gauge(
    "nephthys_open_tickets", "Tickets that are currently open"
)
nephthys_closed_tickets = Gauge(
    "nephthys_closed_tickets", "Tickets that have been resolved (closed)"
)
nephthys_average_hang_time_minutes = Gauge(
    "nephthys_average_hang_time_minutes",
    "Average time (in minutes) tickets remain open before becoming in progress",
)

# Previous 24 hours
nephthys_tickets_prev_24h = Gauge(
    "nephthys_tickets_prev_24h", "Total tickets from the past 24 hours"
)
nephthys_open_tickets_prev_24h = Gauge(
    "nephthys_open_tickets_prev_24h", "Open tickets from the past 24 hours"
)
nephthys_closed_tickets_prev_24h = Gauge(
    "nephthys_closed_tickets_prev_24h", "Closed tickets from the past 24 hours"
)
nephthys_average_hang_time_minutes_prev_24h = Gauge(
    "nephthys_average_hang_time_minutes_prev_24h",
    "Average time (in minutes) tickets from the past 24h remained open before becoming in progress",
)


def update_metrics():
    """Updates Nephthys-specific metrics with values from the DB"""
    # TODO
    pass
