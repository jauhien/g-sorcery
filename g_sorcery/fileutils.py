#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    fileutils.py
    ~~~~~~~~~~~~
    
    file utilities
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import glob
import json
import hashlib
import os
import shutil
import tarfile

from .compatibility import TemporaryDirectory
from .exceptions import FileJSONError, DownloadingError
from .serialization import JSONSerializer, deserializeHook

class FileJSON(object):
    """
    Class for JSON files.
    """
    def __init__(self, directory, name, mandatories=[]):
        """
        Args:
            directory: File directory.
            name: File name.
            mandatories: List of requiered keys.
            loadconv: Type change values on loading.
        """
        self.directory = os.path.abspath(directory)
        self.name = name
        self.path = os.path.join(directory, name)
        self.mandatories = mandatories

    def read(self):
        """
        Read JSON file.
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        content = {}
        if not os.path.isfile(self.path):
            for key in self.mandatories:
                content[key] = ""
            with open(self.path, 'w') as f:
                json.dump(content, f, indent=2,
                    sort_keys=True, cls=JSONSerializer)
        else:
            with open(self.path, 'r') as f:
                content = json.load(f, object_hook=deserializeHook)
            for key in self.mandatories:
                if not key in content:
                    raise FileJSONError('lack of mandatory key: ' + key)
        
        return content

    def write(self, content):
        """
        Write JSON file.
        """
        for key in self.mandatories:
            if not key in content:
                raise FileJSONError('lack of mandatory key: ' + key)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        with open(self.path, 'w') as f:
            json.dump(content, f, indent=2, sort_keys=True, cls=JSONSerializer)


def hash_file(name, hasher, blocksize=65536):
    """
    Get a file hash.

    Args:
        name: file name.
        hasher: Hasher.
        blocksize: Blocksize.

    Returns:
        Hash value.
    """
    with open(name, 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
    return hasher.hexdigest()

def copy_all(src, dst):
    """
    Copy entire tree.

    Args:
       src: Source.
       dst: Destination.
    """
    for f_name in os.listdir(src):
        src_name = os.path.join(src, f_name)
        dst_name = os.path.join(dst, f_name)
        if os.path.isdir(src_name):
            shutil.copytree(src_name, dst_name)
        else:
            shutil.copy2(src_name, dst_name)

def wget(uri, directory, output=""):
    """
    Fetch a file.

    Args:
        uri: URI.
        directory: Directory where file should be saved.

    Returns:
        Nonzero in case of a failure.
    """
    if output:
        ret = os.system('wget ' + uri +
                    ' -O ' + os.path.join(directory, output))
    else:
        ret = os.system('wget -P ' + directory + ' ' + uri)
    return ret

def get_pkgpath(root = None):
    """
    Get package path.

    Returns:
        Package path.
    """
    if not root:
        root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    return os.path.dirname(os.path.abspath(root))

class ManifestEntry:
    """
    A manifest entry for a file.
    """

    __slots__ = ('directory', 'name', 'ftype', 'digest',
                 'size', 'sha256', 'sha512', 'whirlpool')
    
    def __init__(self, directory, name, ftype):
        self.directory = directory
        self.name = name
        self.ftype = ftype
        self.digest()

    def digest(self):
        """
        Digest a file associated with a manifest entry.
        """
        h_sha256 = hashlib.new('SHA256')
        h_sha512 = hashlib.new('SHA512')
        h_whirlpool = hashlib.new('whirlpool')
        with open(os.path.join(self.directory, self.name), 'rb') as f:
            src = f.read()
        h_sha256.update(src)
        h_sha512.update(src)
        h_whirlpool.update(src)
        self.size = str(len(src))
        self.sha256 = h_sha256.hexdigest()
        self.sha512 = h_sha512.hexdigest()
        self.whirlpool = h_whirlpool.hexdigest()


def fast_manifest(directory):
    """
    Digest package directory.
    This function is intended to be used in place of repoman manifest,
    as it is to slow.

    Args:
        directory: Directory.
    """
    manifest = []
    metadata = os.path.join(directory, "metadata.xml")

    for aux in glob.glob(os.path.join(directory, "files/*")):
        manifest.append(ManifestEntry(os.path.dirname(aux),
                            os.path.basename(aux), "AUX"))
    for ebuild in glob.glob(os.path.join(directory, "*.ebuild")):
        manifest.append(ManifestEntry(directory,
                            os.path.basename(ebuild), "EBUILD"))
    if (os.path.isfile(metadata)):
        manifest.append(ManifestEntry(directory, "metadata.xml", "MISC"))

    manifest = [" ".join([m.ftype, m.name, m.size,
                          "SHA256", m.sha256, "SHA512", m.sha512,
                          "WHIRLPOOL", m.whirlpool])
                for m in manifest]

    with open(os.path.join(directory, "Manifest"), 'w') as f:
        f.write('\n'.join(manifest) + '\n')


def _call_parser(f_name, parser, open_file = True, open_mode = 'r'):
    """
    Call parser on a given file.

    Args:
        f_name: File name.
        parser: Parser function.
        open_file: Whether parser accepts a file descriptor.
        open_mode: Open mode for a file.

    Returns:
        A dictionary with one entry. Key if a file name, content is
    content returned by parser.
    """
    data = None
    if open_file:
        with open(f_name, open_mode) as f:
            data = parser(f)
    else:
        data = parser(f_name)
    return {os.path.basename(f_name): data}


def load_remote_file(uri, parser, open_file = True, open_mode='r', output=""):
    """
    Load files from an URI.

    Args:
        uri: URI.
        parser: Parser that will be applied to downloaded files.
        open_file: Whether parser accepts a file descriptor.
        open_mode: Open mode for a file.
        output: What output name should downloaded file have
    (it will be a key identifying data loaded from this file)

    Returns:
        Dictionary with a loaded data. Key is filename, content is data returned by parser.
    """
    download_dir = TemporaryDirectory()
    loaded_data = {}
    if wget(uri, download_dir.name, output):
        raise DownloadingError("wget failed: " + uri)
    for f_name in glob.glob(os.path.join(download_dir.name, "*")):
        if tarfile.is_tarfile(f_name):
            unpack_dir = TemporaryDirectory()
            with tarfile.open(f_name) as f:
                f.extractall(unpack_dir.name)
            for uf_name in glob.glob(os.path.join(unpack_dir, "*")):
                loaded_data.update(_call_parser(uf_name, parser,
                                    open_file=open_file, open_mode=open_mode))
            del unpack_dir
        else:
            name, extention = os.path.splitext(f_name)
            if extention in [".xz", ".lzma"]:
                if (os.system("xz -d " + f_name)):
                    raise DownloadingError("xz failed: "
                                + f_name + " from " + uri)
                f_name = name
            loaded_data.update(_call_parser(f_name, parser,
                                open_file=open_file, open_mode=open_mode))
    del download_dir
    return loaded_data
