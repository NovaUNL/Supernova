# Adapted from https://github.com/ecometrica/django-hashedfilenamestorage/
# Author: Ecometrica
# License: MIT

from errno import EEXIST
import hashlib
import os

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_str
from django.core.exceptions import ImproperlyConfigured


def HashedFilenameMetaStorage(storage_class):
    class HashedFilenameStorage(storage_class):
        def __init__(self, *args, **kwargs):
            # Try to tell storage_class not to uniquify filenames.
            # This class will be the one that uniquifies.
            try:
                new_kwargs = dict(kwargs, uniquify_names=False)
                super(HashedFilenameStorage, self).__init__(*args, **new_kwargs)
            except (TypeError, ImproperlyConfigured):
                super(HashedFilenameStorage, self).__init__(*args, **kwargs)

        def _get_content_name(self, name, content, chunk_size=None):
            dir_name, file_name = os.path.split(name)
            file_hash = self._compute_hash(content=content, chunk_size=chunk_size)
            hash_dir_name = file_hash[:2]
            file_name = file_hash[2:]
            return os.path.join(dir_name, hash_dir_name, file_name), file_hash

        def _compute_hash(self, content, chunk_size=None):
            if chunk_size is None:
                chunk_size = getattr(content, 'DEFAULT_CHUNK_SIZE', File.DEFAULT_CHUNK_SIZE)

            hasher = hashlib.sha1()
            cursor = content.tell()
            content.seek(0)
            try:
                while True:
                    data = content.read(chunk_size)
                    if not data:
                        break
                    if not isinstance(data, bytes):
                        data = data.encode('utf-8')
                    hasher.update(data)
                return hasher.hexdigest()
            finally:
                content.seek(cursor)

        def save(self, name, content, max_length=None):
            # Get the proper name for the file, as it will actually be saved.
            if name is None:
                name = content.name

            name, file_hash = self._save(name, content)
            return force_str(name), file_hash

        def _save(self, name, content, *args, **kwargs):
            name, file_hash = self._get_content_name(name=name, content=content)

            if self.exists(name):
                # File already exists, so we can safely do nothing
                # because their contents match.
                return name, file_hash

            try:
                return super(HashedFilenameStorage, self)._save(name, content, *args, **kwargs), file_hash
            except OSError as e:
                if e.errno == EEXIST:
                    # We have a safe storage layer and file exists.
                    pass
                else:
                    raise
            return name, file_hash

    HashedFilenameStorage.__name__ = 'HashedFilename' + storage_class.__name__
    return HashedFilenameStorage


HashedFilenameFileSystemStorage = HashedFilenameMetaStorage(storage_class=FileSystemStorage, )
