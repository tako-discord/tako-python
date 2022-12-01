from .sync import Sync
from .extension import Extension
from .manage_announcements import ManageAnnouncements

subclasses = Extension, ManageAnnouncements, Sync


class Owner(*subclasses):
    """
    These are commands only executable by the bot owner
    """
