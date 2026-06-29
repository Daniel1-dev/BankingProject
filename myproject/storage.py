from django.core.files.storage import FileSystemStorage
from django.core.files import locks
from unittest.mock import MagicMock

# Monkey-patch the locks module globally within this process
# to return immediately without calling underlying system functions.
locks.lock = MagicMock()
locks.unlock = MagicMock()

class NoLockFileSystemStorage(FileSystemStorage):
    """
    A custom storage backend that disables file locking.
    By patching the 'locks' module, we prevent the Django core
    from attempting to execute system-level locks.
    """
    pass
