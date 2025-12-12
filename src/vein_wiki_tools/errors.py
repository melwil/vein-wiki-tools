class VeinError(Exception):
    """
    Base Error
    """

    def __init__(
        self,
        detail: str,
        *args: object,
    ) -> None:
        self.detail = detail
        self.args = args

    def __str__(self) -> str:
        return self.detail % self.args
