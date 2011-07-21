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

def slice_funs(slice_expr):
    r=[]
    ss = slice_expr.split(',')
    for s in ss:
        if s.find(':') >= 0: e = "lambda L:L["+s+"]"
        else: e = "lambda L:[L["+s+"]]"
        r.append(eval(e))
    return r


def load_slice_data(dfile, delim=None, cslice=':', rslice=':'):
    cslf = slice_funs(cslice)
    rslf = slice_funs(rslice)
    data = []
    for ln in dfile:
        ln = ln.strip('\r\n')
        t = ln.split(delim)
        d = []
        for f in cslf: d.extend(f(t))
        data.append(d)
    t = data
    data = []
    for f in rslf: data.extend(f(t))
    return data
