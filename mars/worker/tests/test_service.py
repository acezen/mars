# -*- coding: utf-8 -*-
# Copyright 1999-2020 Alibaba Group Holding Ltd.
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

import unittest

from mars.worker.service import WorkerService
from mars.config import options
from mars.tests.core import patch_method


class Test(unittest.TestCase):
    def setUp(self):
        self._old_spill_dirs = options.worker.spill_directory

    def tearDown(self):
        options.worker.spill_directory = self._old_spill_dirs

    def testServiceArgs(self):
        svc = WorkerService(ignore_avail_mem=True)
        self.assertGreaterEqual(svc._cache_mem_size, 0)
        self.assertIsInstance(svc._soft_mem_limit, int)
        self.assertIsInstance(svc._hard_mem_limit, int)
        self.assertIsInstance(svc._cache_mem_size, int)

        svc = WorkerService(ignore_avail_mem=True, total_mem=256 * 1024 * 1024)
        self.assertEqual(svc._total_mem, 256 * 1024 ** 2)

        svc = WorkerService(ignore_avail_mem=True, total_mem='512m')
        self.assertEqual(svc._total_mem, 512 * 1024 ** 2)

        with self.assertRaises(MemoryError):
            WorkerService(soft_mem_limit='128m', cache_mem_size='256m')

        with self.assertRaises(MemoryError), \
                patch_method(WorkerService._get_plasma_size, new=lambda *_, **__: 0):
            WorkerService(min_cache_mem_size='1g', cache_mem_size='256m')

        svc = WorkerService(ignore_avail_mem=True, spill_dirs='/tmp/a', min_cache_mem_size=0)
        self.assertListEqual(svc._spill_dirs, ['/tmp/a'])

        svc = WorkerService(ignore_avail_mem=True, n_cpu_process=4, n_net_process=2,
                            min_cache_mem_size=0)
        self.assertEqual(svc.n_process, 7)

        svc = WorkerService(ignore_avail_mem=True, n_cpu_process=4, n_net_process=2,
                            spill_dirs='/tmp/a', min_cache_mem_size=0)
        self.assertEqual(svc.n_process, 8)

        svc = WorkerService(ignore_avail_mem=True, n_cpu_process=4, n_net_process=2,
                            spill_dirs=['/tmp/a', '/tmp/b'], min_cache_mem_size=0)
        self.assertEqual(svc.n_process, 8)
