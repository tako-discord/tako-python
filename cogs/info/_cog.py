from .ping import Ping
from .stats import Stats
from .announcements import Announcements

subclasses = Ping, Stats, Announcements


class Info(*subclasses):
    """
    Get some infos like the ping or some stats
    """
