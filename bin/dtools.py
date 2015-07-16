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


def trynum(v):
    try: r = int(v)
    except: pass
    else: return r
    try: r = float(v)
    except: pass
    else: return r
    return v


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

def delim_arg(a):
    emsg = 'bad delim argument format "%s"'%(a)
    t = a
    if (a == "tab"): t = "\t"
    if (a == "ws"): t = None
    if (a == "whitespace"): t = None
    if (a == "comma"): t = ","
    if (a == "space"): t = " "
    return t

def slicefun(expr):
    e = "lambda L:L["+expr+"]"
    return eval(e)


def slicelist(x):
    jlst = list(x)
    r = []
    if len(jlst) <= 0: return r
    jL = jlst[0]
    jprv = jL
    for j in jlst[1:]:
        if j == jprv+1:
            jprv = j
            continue
        r.append("%d:%d"%(jL,jprv+1))
        jL = j
        jprv = j
    r.append("%d:%d"%(jL,jprv+1))
    return r


def subtract_slices(N, sl, sublist):
    U = range(N)
    ss = set()
    for s in sublist:
        for f in [slicefun(x) for x in s]: ss |= set(f(U))
    r = []
    for f in [slicefun(x) for x in sl]:
        sr = set(f(U)) - ss
        r.extend(slicelist(sr))
    return r

def apply_slice(data, dslice=':'):
    tcs = dslice[:]
    cslf = [slicefun(x) for x in tcs]
    r = []
    for f in cslf: r.extend(f(data))
    return r

def load_slice_data(dfile, delim=None, cslice=':', rslice=':', sslices=[]):
    rslf = [slicefun(x) for x in rslice]
    sslfs = [[slicefun(x) for x in xx] for xx in [s[0] for s in sslices]]
    sfmts = [s[1] for s in sslices]
    smaps = [{} for s in sslices]
    data = []
    n = 0
    pL = -1
    for ln in dfile:
        ln = ln.strip('\r\n')
        t = ln.split(delim)
        L = len(t)
        if (L != pL) and ((pL < 0) or (len(sslices) > 0)):
            # Compute cslf at least once, first line read
            # If sslices is nonempty, then also recompute each time number of fields changes
            tcs = cslice[:]
            if len(sslices) > 0: tcs = subtract_slices(L, tcs, [s[0] for s in sslices])
            cslf = [slicefun(x) for x in tcs]
            pL = L
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
    r = []
    for f in rslf: r.extend(f(data))
    return r


def load_key_data(dfile, delim=None, kslice='0', rslice=':', cslice='1:', numkey=False):
    rslf = [slicefun(x) for x in rslice]
    cslf = [slicefun(x) for x in cslice]
    kslf = [slicefun(x) for x in kslice]
    data = []
    cmax = 0
    for ln in dfile:
        ln = ln.strip('\r\n')
        t = ln.split(delim)
        key = []
        for f in kslf: key.extend(f(t))
        d = []
        for f in cslf: d.extend(f(t))
        if len(d) > cmax: cmax = len(d)
        data.append([key, d])
    r = []
    for f in rslf: r.extend(f(data))
    data = {}
    for d in r:
        dk = d[0]
        if numkey: dk = [trynum(v) for v in dk]
        key = tuple(dk)
        if not data.has_key(key): data[key] = [list() for x in xrange(cmax)]
        for j in xrange(len(d[1])):
            data[key][j].append(d[1][j])
    return data
