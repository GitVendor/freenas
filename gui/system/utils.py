# Copyright 2014 iXsystems, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#####################################################################
import logging
import json
import os

from django.utils.translation import ugettext as _

log = logging.getLogger('system.utils')


class CheckUpdateHandler(object):

    def __init__(self):
        self.output = ''

    def call(self, op, newpkg, oldpkg):
        if op == 'upgrade':
            self.output += '%s: %s-%s -> %s-%s\n' % (
                _('Upgrade'),
                newpkg.Name(),
                newpkg.Version(),
                oldpkg.Name(),
                oldpkg.Version(),
            )


class UpdateHandler(object):

    DUMPFILE = '/tmp/.upgradeprogress'

    def __init__(self):
        self.step = 1
        self.progress = 0
        self.indeterminate = False
        self.details = ''
        self._pkgname = ''

    def get_handler(self, index, pkg, pkgList):
        log.error("get_handler %r %r %r", index, pkg, pkgList)
        self.step = 1
        self._pkgname = '%s-%s' % (
            pkg.Name(),
            pkg.Version(),
        )
        self.details = 'Downloading %s' % self._pkgname
        self._baseprogress = int((1.0 / float(len(pkgList))) * 100)
        self.progress = (index - 1) * self._baseprogress
        self.dump()
        return self.get_file_handler

    def get_file_handler(self, method, filename, progress=None):
        log.error("downloading get file %r %r", filename, progress)
        if progress is not None and self._pkgname:
            self.progress = (progress * self._baseprogress) / 100
            self.details = '%s (%d%%)' % (self._pkgname, progress)
        self.dump()

    def install_handler(self, index, name, packages):
        self.step = 2
        self.indeterminate = False
        total =len(packages)
        self.progress = int((float(index) / float(total)) * 100.0)
        self.details = 'Installing %s (%d/%d)' % (
            name,
            index,
            total,
        )

    def dump(self):
        with open(self.DUMPFILE, 'wb') as f:
            data = {
                'step': self.step,
                'percent': self.progress,
                'indeterminate': self.indeterminate,
            }
            if self.details:
                data['details'] = self.details
            f.write(json.dumps(data))

    def load(self):
        if not os.path.exists(self.DUMPFILE):
            return {}
        with open(self.DUMPFILE, 'rb') as f:
            data = json.loads(f.read())
        return data
