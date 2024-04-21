from gui.abstract.widget import Widget


class System:
    """
    Управление программами
    """
    system_apps: list[Widget]
    user_apps: list[Widget]

    def __init__(self):
        """

        @rtype: object
        """
        self.system_apps = []
        self.user_apps = []

    def register_app(self, app: Widget):
        self.user_apps.append(app)
