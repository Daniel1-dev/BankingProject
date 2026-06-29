import os
from django.core.files.storage import FileSystemStorage

class NoLockFileSystemStorage(FileSystemStorage):
    """
    A custom storage backend that disables file locking,
    which is not supported on some Android file systems.
    """
    def _save(self, name, content):
        # We override _save to prevent calling locks.lock which fails on Android
        return super()._save(name, content)
    
    # Override lock and unlock methods to do absolutely nothing
    # to avoid triggering the 'Function not implemented' error
    def lock(self, file, flags):
        pass

    def unlock(self, file):
        pass
