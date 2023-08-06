# Licensed under GNU General Public License v3 or later, see COPYING.
# Copyright (c) 2019 Red Hat, Inc., see CONTRIBUTORS.

import datetime
import os
import sys
import time

from fingertip.util import log, weak_hash, units


class Expiration:
    def __init__(self, expire_in):
        self.time = time.time() + units.parse_time_interval(expire_in)
        self._deps_files, self._deps_dirs = {}, {}

    def pretty(self):
        return datetime.datetime.fromtimestamp(self.time).isoformat()

    def cap(self, interval):
        self.time = min(self.time,
                        time.time() + units.parse_time_interval(interval))

    def is_expired(self, by=None):
        return self.time < (by or time.time())

    def depend_on(self, tree):
        if not os.path.isdir(tree):
            self.depend_on_a_file(tree)
        else:
            for root, dirs, files in os.walk(tree):
                self.depend_on_a_directory_listing(root)
                for d in dirs:
                    self.depend_on_a_directory_listing(os.path.join(root, d))
                for f in files:
                    self.depend_on_a_file(os.path.join(root, f))

    def depend_on_a_directory_listing(self, path):
        hash_ = weak_hash.of_string(repr(sorted(os.listdir(path))))
        self._deps_dirs[path] = (os.stat(path).st_mtime, hash_)

    def depend_on_a_file(self, path):
        path = os.path.abspath(path)
        if ((path.startswith('/usr/lib') or '/site-packages/' in path)
                and '/fingertip/' not in path):
            return
        self._deps_files[path] = (os.stat(path).st_mtime,
                                  weak_hash.of_file(path))

    def file_has_not_changed(self, path):
        log.debug(f'checking that {path} has not changed...')
        mtime, hash_ = self._deps_files[path]
        try:
            if mtime != (os.stat(path).st_mtime):
                if hash_ != weak_hash.of_file(path):
                    log.warning(f'{path} has changed, set '
                                'FINGERTIP_IGNORE_FILE_CHANGES=1 to ignore')
                    return False
        except FileNotFoundError:
            return False
        return True

    def dir_listing_has_not_changed(self, path):
        log.debug(f'checking that {path} listing has not changed...')
        mtime, hash_ = self._deps_dirs[path]
        try:
            if mtime != (os.stat(path).st_mtime):
                listing = repr(sorted(os.listdir(path)))
                if hash_ != weak_hash.of_string(listing):
                    log.warning(f'{path} listing has changed, set '
                                'FINGERTIP_IGNORE_FILE_CHANGES=1 to ignore')
                    return False
        except FileNotFoundError:
            return False
        return True

    def files_have_not_changed(self):
        if (os.getenv('FINGERTIP_IGNORE_CODE_CHANGES', '0') != '0' or
                os.getenv('FINGERTIP_IGNORE_FILE_CHANGES', '0') != '0'):
            return True
        return (all((self.file_has_not_changed(p) for p in self._deps_files))
                and
                all((self.dir_listing_has_not_changed(p)
                    for p in self._deps_dirs)))

    def depend_on_loaded_python_modules(self):
        """
        Make the machine depend on all python modules loaded to date
        in an imprecise best-effort overly-cautious attempt
        to get automatic rebuilds triggered on source code changes.
        """
        for module in sys.modules:
            try:
                module_file = sys.modules[module].__file__
                if module_file:
                    self.depend_on_a_file(module_file)
            except AttributeError:
                pass
