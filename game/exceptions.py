class GameBlockedException(Exception):
    """Exception for game sessions that are blocked"""

    def __init__(self, message=None):
        if message is None:
            message = "Game session is currently blocked."
        super().__init__(message)
