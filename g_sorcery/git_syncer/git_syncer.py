#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    git_syncer.py
    ~~~~~~~~~~~~~

    git sync helper

    :copyright: (c) 2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

from g_sorcery.compatibility import TemporaryDirectory

from g_sorcery.exceptions import SyncError
from g_sorcery.syncer import Syncer, SyncedData, TmpSyncedData


class GITSyncer(Syncer):
    """
    Class used to sync with git repos.
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
        if self.persistent_datadir is None:
            tmp_dir = TemporaryDirectory()
            path = os.path.join(tmp_dir.name, "remote")
        else:
            path = self.persistent_datadir
        try:
            branch = repository_config["branch"]
        except KeyError:
            branch = "master"

        if os.path.exists(path):
            #TODO: allow changing of remotes/branches
            self.pull(path)
        else:
            self.clone(db_uri, branch, path)

        if self.persistent_datadir is None:
            return TmpSyncedData(path, tmp_dir)
        else:
            return SyncedData(path)


    def clone(self, db_uri, branch, path):
        if os.system("git clone --depth 1 --branch " + branch + " " + db_uri + " " + path):
            raise SyncError("sync failed (clonning): " + db_uri)


    def pull(self, path):
        if os.system("cd " + path + " && git pull"):
            raise SyncError("sync failed (pulling): " + path)
