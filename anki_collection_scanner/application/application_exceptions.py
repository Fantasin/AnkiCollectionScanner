class SyncError(Exception):
    """Raises when collection sync failes during orchestration"""
    def __init__(self, stage, message):
        self.stage = stage
        self.message = message
        super().__init__(f"Collection sync failed")