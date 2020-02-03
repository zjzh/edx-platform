from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait

POOL = ThreadPoolExecutor()
# POOL = ProcessPoolExecutor()
NOT_DONE = object()


def defer(func, *args, **kwargs):
    proxy_result = kwargs.pop('proxy_result', False)
    fut = POOL.submit(func, *args, **kwargs)
    if proxy_result:
        fut = FutureProxy(fut)
    return fut


def map(func, *iterables):
    return POOL.map(func, *iterables)


class FutureProxy:
    def __init__(self, fut):
        self.fut = fut
        self._result = NOT_DONE

    def _check_done(self):
        if self._result is NOT_DONE:
            self._result = self.fut.result()

    def __getattr__(self, attr):
        self._check_done()
        return getattr(self._result, attr)

    def __getitem__(self, item):
        self._check_done()
        return self._result[item]

    def __contains__(self, item):
        self._check_done()
        return item in self._result

    def __iter__(self):
        self._check_done()
        return iter(self._result)
