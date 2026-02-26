
class SnapshotRepositoryError(Exception):
    """Base class for snapshot repository errors"""
    pass

class SnapshotNotFoundError(SnapshotRepositoryError):
    """Raises when repository file is missing"""
    def __init__(self, path):
        super().__init__(f"Snapshot not found on path: {path}")
        self.path = path

class SnapshotCorruptedError(SnapshotRepositoryError):
    def __init__(self, path):
        super().__init__(f"Snapshot file is corrupted: {path}")
        self.path = path