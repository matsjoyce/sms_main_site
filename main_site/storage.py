import os
import sys
import mimetypes
import datetime
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from google.appengine.api.blobstore import create_gs_key
import cloudstorage as gcs

__author__ = "ckopanos@redmob.gr, me@rchrd.net"
__license__ = "GNU GENERAL PUBLIC LICENSE"


class GoogleCloudStorage(Storage):
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.GOOGLE_CLOUD_STORAGE_BUCKET
        self.location = location
        if base_url is None:
            base_url = settings.GOOGLE_CLOUD_STORAGE_URL
        self.base_url = base_url

    def process_filename(self, name):
        return os.path.normpath(self.location + "/" + name)

    def _open(self, name, mode='r'):
        filename = self.process_filename(name)

        # rb is not supported
        if mode == 'rb':
            mode = 'r'

        if mode == 'w':
            type, encoding = mimetypes.guess_type(name)
            cache_control = settings.GOOGLE_CLOUD_STORAGE_DEFAULT_CACHE_CONTROL
            gcs_file = gcs.open(filename, mode=mode, content_type=type,
                                options={'x-goog-acl': 'public-read',
                                         'cache-control': cache_control})
        else:
            gcs_file = gcs.open(filename, mode=mode)

        return gcs_file

    def _save(self, name, content):
        filename = self.process_filename(name)
        type, encoding = mimetypes.guess_type(name)
        cache_control = settings.GOOGLE_CLOUD_STORAGE_DEFAULT_CACHE_CONTROL

        # Files are stored with public-read permissions.
        # Check out the google acl options if you need to alter this.
        gss_file = gcs.open(filename, mode='w', content_type=type,
                            options={'x-goog-acl': 'public-read',
                                     'cache-control': cache_control})
        try:
            content.open()
        except:
            pass
        gss_file.write(content.read())
        try:
            content.close()
        except:
            pass
        gss_file.close()
        return name

    def delete(self, name):
        filename = self.process_filename(name)
        try:
            gcs.delete(filename)
        except gcs.NotFoundError:
            pass

    def exists(self, name):
        try:
            self.statFile(name)
            return True
        except gcs.NotFoundError:
            return False

    def listdir(self, path=None):
        directories, files = [], []
        bucketContents = gcs.listbucket(self.location, prefix=path)
        subPath = os.path.join(self.location, path, "")
        for entry in bucketContents:
            filePath = entry.filename.replace(subPath, '', 1)
            head, tail = os.path.split(filePath)
            if head == "":
                head = None
            if not head and tail:
                files.append(tail)
            if head:
                if not head.startswith("/"):
                    head = "/" + head
                dir = head.split("/")[1]
                if not dir in directories:
                    directories.append(dir)
        return directories, files

    def size(self, name):
        stats = self.statFile(name)
        return stats.st_size

    def accessed_time(self, name):
        raise NotImplementedError

    def created_time(self, name):
        stats = self.statFile(name)
        return datetime.datetime.fromtimestamp(stats.st_ctime)

    def modified_time(self, name):
        return self.created_time(name)

    def url(self, name):
        if not sys.on_production:
            # we need this in order to display images, links to files, etc
            # from the local appengine server
            filename = "/gs" + self.location + "/" + name
            key = create_gs_key(filename)
            local_base_url = getattr(settings, "GOOGLE_CLOUD_STORAGE_DEV_URL",
                                     "http://localhost:8000/blobstore/blob/")
            return local_base_url + key + "?display=inline"
        return self.base_url + self.location + "/" + name

    def statFile(self, name):
        filename = self.process_filename(name)
        return gcs.stat(filename)

    def isfile(self, name):
        return self.exists(name)

    def isdir(self, name):
        if not name:
            return True

        bucketContents = gcs.listbucket(self.location, prefix=os.path.join(name, ""), max_keys=1)
        contents = list(bucketContents)
        return bool(contents)

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        old_file_name = self.process_filename(old_file_name)
        new_file_name = self.process_filename(new_file_name)
        gcs.copy2(old_file_name, new_file_name)
        gcs.delete(old_file_name)

    def makedirs(self, name):
        self.save(name + "/.folder", ContentFile(""))

    def rmtree(self, path):
        directories, files = [], []
        bucketContents = gcs.listbucket(self.location, prefix=path)
        for entry in bucketContents:
            gcs.delete(entry)
