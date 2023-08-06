#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Alibaba Group Holding Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pickle

try:
    import pyarrow as pa
except ImportError:
    pa = None


def default_builder(client, value):
    ''' Default builder: serialize the object, using pyarrow if it presents,
        otherwise with pickle, then build a blob object for it.
    '''
    if pa is not None:
        payload = pa.serialize(value).to_buffer().to_pybytes()
        serialization = 'pyarrow'
    else:
        payload = pickle.dumps(value)
        serialization = 'pickle'

    buffer = client.create_blob(len(payload))
    buffer.copy(0, payload)
    buffer['serialization'] = serialization
    return buffer.seal(client).id


def default_resolver(obj):
    view = memoryview(obj)
    serialization = obj.meta['serialization']
    if serialization:
        if pa is not None and serialization == 'pyarrow':
            return pa.deserialize(view)
        if serialization == 'pickle':
            return pickle.loads(view, fix_imports=True)
    # fallback: still returns the blob
    return obj


def register_default_types(builder_ctx=None, resolver_ctx=None):
    if builder_ctx is not None:
        builder_ctx.register(object, default_builder)

    if resolver_ctx is not None:
        resolver_ctx.register('vineyard::Blob', default_resolver)
