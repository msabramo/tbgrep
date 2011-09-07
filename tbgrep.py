#!/usr/bin/env python
# tbgrep - Python Traceback Extractor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2011 Luke Macken <lmacken@redhat.com>

import sys
import fileinput

from collections import defaultdict
from operator import itemgetter

tb_head = 'Traceback (most recent call last):'

class TracebackGrep(object):
    tb = index = None
    stats = firstline = prefix = False
    tracebacks = defaultdict(int)

    def __init__(self, stats=False):
        self.stats = stats

    def process(self, line):
        if self.tb:
            if line:
                if self.firstline:
                    self.prefix = line[0] != ' '
                    self.firstline = False
                if self.prefix:
                    line = line[self.index:]
                self.tb += line
                if line and line[0] != ' ':
                    tb = self.tb
                    self.tb = None
                    if self.stats:
                        self.tracebacks[tb] += 1
                    return tb
        elif tb_head in line:
            self.index = line.index(tb_head)
            self.tb = line[self.index:]
            self.firstline = True

    def get_stats(self):
        return sorted(self.tracebacks.items(), key=itemgetter(1))

    def print_stats(self):
        header = lambda x: '== %s %s' % (x, '=' * (76 - len(x)))
        stats = self.get_stats()
        for tb, num in stats:
            print header('%d occurence%s' % (num,
                    (num == 1 and [''] or ['s'])[0]))
            print
            print tb
        print '=' * 80
        print "%d unique tracebacks extracted" % len(stats)


if __name__ == '__main__':
    stats = False
    if '--stats' in sys.argv:
        stats = True
        sys.argv.remove('--stats')

    extractor = TracebackGrep(stats=stats)

    for line in fileinput.input():
        tb = extractor.process(line)
        if not stats and tb:
            print tb
    if stats:
        extractor.print_stats()