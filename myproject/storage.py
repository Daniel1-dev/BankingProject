import os
from django.core.files.storage import FileSystemStorage
from django.core.files import locks

class NoLockFileSystemStorage(FileSystemStorage):
    """
    A custom storage backend that disables file locking,
    which is not supported on some Android file systems.
    """
    def _save(self, name, content):
        # We override _save to prevent calling locks.lock which fails on Android
        return super()._save(name, content)

    def _open(self, name, mode='rb'):
        return super()._open(name, mode)
    
    def lock_file(self, fd, flags):
        # Disable locking entirely by doing nothing
        pass
        
    def unlock_file(self, fd):
        # Disable unlocking entirely by doing nothing
        pass
