#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    syncer.py
    ~~~~~~~~~

    sync helper

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import glob
import os

from .compatibility import TemporaryDirectory

from .exceptions import SyncError
from .fileutils import wget


class SyncedData(object):
    """
    Synced data.

    Directory with sync data is guaranted to exist only as long as this
    object does.
    """
    def __init__(self, directory):
        self.directory = os.path.abspath(directory)

    def get_path(self):
        return self.directory


class TmpSyncedData(SyncedData):
    """
    Synced data that lives in a temporary directory.
    """

    def __init__(self, directory, tmpdirobj):
        super(TmpSyncedData, self).__init__(directory)
        self.tmpdirobj = tmpdirobj


class Syncer(object):
    """
    Class used to sync data with remote source.
    """

    def __init__(self, persistent_datadir):
        self.persistent_datadir = persistent_datadir

    def sync(self, db_uri, repository_config):
        """
        Synchronize local directory with remote source.

        Args:
            db_uri: URI for synchronization with remote source.
            repository_config: repository config.

        Returns:
            SyncedData object that gives access to the directory with data.
        """
        raise NotImplementedError


class TGZSyncer(Syncer):
    """
    Class used to download and unpack tarballs.
    """

    def sync(self, db_uri, repository_config):
        """
        Synchronize local directory with remote source.

        Args:
            db_uri: URI for synchronization with remote source.
            repository_config: repository config.

        Returns:
            SyncedData object that gives access to the directory with data.
        """
        download_dir = TemporaryDirectory()
        if wget(db_uri, download_dir.name):
            raise SyncError('sync failed: ' + db_uri)

        tmp_dir = TemporaryDirectory()
        for f_name in glob.iglob(os.path.join(download_dir.name, '*.tar.gz')):
            if os.system("tar -xvzf " + f_name + " -C " + tmp_dir.name):
                raise SyncError('sync failed (unpacking)')

        tmp_path = os.path.join(tmp_dir.name, os.listdir(tmp_dir.name)[0])
        del download_dir
        return TmpSyncedData(tmp_path, tmp_dir)


SUPPORTED_SYNCERS = {"tgz": TGZSyncer}

# git_syncer module is optional, we should check if it is installed
try:
    from .git_syncer.git_syncer import GITSyncer
    SUPPORTED_SYNCERS["git"] = GITSyncer

except ImportError as e:
    pass
