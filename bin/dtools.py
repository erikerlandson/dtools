#!/bin/env python

# dtools: simple tools for manipulating and plotting data
#
# Copyright (c) 2011 Erik Erlandson
#
# Author:  Erik Erlandson <erikerlandson@yahoo.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import argparse


def slicelist_arg(a):
    emsg = 'bad slicelist format "%s"'%(a)
    ss = a.split(',')
    ss = [x.strip(' \t') for x in ss]
    r = []
    for s in ss:
        if ':' in s:
            t = s.split(':')
            if len(t) > 3: raise argparse.ArgumentTypeError(emsg)
            for v in t:
                if v == '': continue
                try: j = int(v)
                except: raise argparse.ArgumentTypeError(emsg)
            r.append(s)
        else:
            try: j = int(s)
            except: raise argparse.ArgumentTypeError(emsg)
            r.append("%d:%d"%(j,j+1))
    return r


def scrub_arg(a):
    emsg = 'bad scrub argument format "%s"'%(a)
    if '+' in a: t = a.split('+')
    else: t = [a]
    t = [x.strip(' \t') for x in t]
    if len(t) > 2: raise argparse.ArgumentTypeError(emsg)
    if len(t) == 1: t.append('x%d')
    t[0] = slicelist_arg(t[0])
    return t


def slicefun(expr):
    e = "lambda L:L["+expr+"]"
    return eval(e)


def load_slice_data(dfile, delim=None, cslice=':', rslice=':', sslices=[]):
    cslf = [slicefun(x) for x in cslice]
    rslf = [slicefun(x) for x in rslice]
    sslfs = [[slicefun(x) for x in xx] for xx in [s[0] for s in sslices]]
    sfmts = [s[1] for s in sslices]
    smaps = [{} for s in sslices]
    data = []
    n = 0
    for ln in dfile:
        ln = ln.strip('\r\n')
        t = ln.split(delim)
        d = []
        for f in cslf: d.extend(f(t))
        for j in xrange(len(sslfs)):
            v = []
            for f in sslfs[j]: v.extend(f(t))
            k = "|".join(v)
            if not smaps[j].has_key(k):
                smaps[j][k] = sfmts[j]%(n)
                n += 1
            d.append(smaps[j][k])
        data.append(d)
    t = data
    data = []
    for f in rslf: data.extend(f(t))
    return data
