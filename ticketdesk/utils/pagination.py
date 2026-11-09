from fastapi import Query


class Page:
    def __init__(
        self,
        limit: int = Query(25, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ):
        self.limit = limit
        self.offset = offset
