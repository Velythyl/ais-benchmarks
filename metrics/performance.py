"""
Performance metrics will evaluate computation complexity, memory consumption and efficiency (power consumption)
"""

import time
import tracemalloc
import gc

from metrics.base import CMetric


class CElapsedTime(CMetric):
    def __init__(self):
        super().__init__()
        self.name = "time"
        self.type = "performance"
        self.t_ini = 0
        self.t_end = 0

    def pre(self, **kwargs):
        self.t_ini = time.time()

    def post(self, **kwargs):
        self.t_end = time.time()
        self.value += self.t_end - self.t_ini

    def compute(self, **kwargs):
        return self.value

    def reset(self, **kwargs):
        self.t_ini = 0
        self.t_end = 0
        self.value = 0


class CMemoryUsage(CMetric):
    def __init__(self):
        super().__init__()
        self.name = "memory"
        self.type = "performance"
        self.mem_ini_blk = 0
        self.mem_ini_peak_blk = 0
        self.mem_ini = 0
        self.mem_end_blk = 0
        self.mem_end_peak_blk = 0
        self.mem_end = 0
        self.mem_cum = 0
        self.mem_cum_blk = 0
        self.mem_cum_peak_blk = 0
        tracemalloc.start()

    def __del__(self):
        tracemalloc.stop()

    def pre(self, **kwargs):
        gc.collect()
        self.mem_ini_blk, self.mem_ini_peak_blk = tracemalloc.get_traced_memory()
        self.mem_ini = tracemalloc.get_tracemalloc_memory()

    def post(self, **kwargs):
        gc.collect()
        self.mem_end_blk, self.mem_end_peak_blk = tracemalloc.get_traced_memory()
        self.mem_end = tracemalloc.get_tracemalloc_memory()
        self.mem_cum += self.mem_end - self.mem_ini
        self.mem_cum_blk += self.mem_end_blk - self.mem_ini_blk
        self.value = self.mem_cum / (1024.0*1024.0)

    def compute(self, **kwargs):
        return self.value

    def reset(self, **kwargs):
        self.mem_ini_blk = 0
        self.mem_ini_peak_blk = 0
        self.mem_ini = 0
        self.mem_end_blk = 0
        self.mem_end_peak_blk = 0
        self.mem_end = 0
        self.mem_cum = 0
        self.mem_cum_blk = 0
        self.mem_cum_peak_blk = 0
        gc.collect()

