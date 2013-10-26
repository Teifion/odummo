import signal
import sys
import time

class TimeoutException(Exception):
    def __init__(self, value="Timeout error"):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class TimeoutFunction:
    def __init__(self, function, timeout):
        self.timeout    = timeout
        self.function   = function
    
    def handle_timeout(self, signum, frame):
        raise TimeoutException()
    
    def __call__(self, *args):
        old = signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.timeout)
        try:
            result = self.function(*args)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)
        signal.alarm(0)
        return result

def progressbar(it, prefix = "", size = 60, with_eta=False):
    """
    for i in progressbar(range(15), "Computing: ", 40):
         time.sleep(0.1) # long computation
    """
    
    count = len(it)
    start_time = time.time()
    
    def _show(_i):
        eta_string = ""
        if _i > 0:
            time_so_far = time.time() - start_time
            time_per_item = time_so_far / _i
            eta = (count - _i) * time_per_item
            
            if with_eta:
                eta_string = "  eta %s" % round(eta, 1)
            
            if eta < 0.1:
                eta_string = "           "
        
        x = int(size*_i/count)
        sys.stdout.write("%s[%s%s] %i/%i%s\r" % (prefix, "#"*x, "."*(size-x), _i, count, eta_string))
        sys.stdout.flush()
    
    _show(0)
    for i, item in enumerate(it):
        yield item
        _show(i+1)
    # sys.stdout.write("".join([" " for i in range(size + 40)]))
    # sys.stdout.flush()
    
    # Cleanup
    time_so_far = time.time() - start_time
    
    if with_eta:
        eta_string = " in %ss" % round(time_so_far, 1)
        
        sys.stdout.write("%s[%s%s] %i/%i%s\r" % (prefix, "#"*size, "."*0, count, count, eta_string))
        sys.stdout.flush()
    
    print()