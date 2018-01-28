from pynvml import *
import numpy as np


class GpuProfiler:
    profiler = None

    def __init__(self):
        nvmlInit()
        self.handles = []
        deviceCount = nvmlDeviceGetCount()
        for i in range(0, deviceCount):
            self.handles.append(nvmlDeviceGetHandleByIndex(i))

    def find_free_gpu(self):
        # this approximately runs in 0.1ms
        return np.argmin([int(nvmlDeviceGetUtilizationRates(handle).gpu) for handle in self.handles])

    def __del__(self):
        nvmlShutdown()

    @staticmethod
    def get_instance():
        if GpuProfiler.profiler is None:
            GpuProfiler.profiler = GpuProfiler()
        return GpuProfiler.profiler


def scheduled_run(sess, output, feed_tuple, hard_assign=-1):
    gpu_id = hard_assign if hard_assign >= 0 else GpuProfiler.get_instance().find_free_gpu()
    if isinstance(output, list):
        for i, o in enumerate(output):
            output[i] = o[gpu_id]
        else:
            output = output[gpu_id]
    feed_dict = {}
    for t in feed_tuple:
        feed_dict[t[0][gpu_id]] = t[1]
    return sess.run(output, feed_dict=feed_dict)

