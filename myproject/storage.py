import os
from django.core.files.storage import FileSystemStorage

class NoLockFileSystemStorage(FileSystemStorage):
    """
    A custom storage backend that disables file locking by 
    bypassing the base _save method which calls fcntl.flock.
    """
    def _save(self, name, content):
        # We manually save the file without calling any locks
        full_path = self.path(name)
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(full_path, 'wb+') as destination:
            for chunk in content.chunks():
                destination.write(chunk)
        return name
