''' Semsphore module '''

import threading

class Sem():
    ''' Semaphore '''
    __SEM_TIMEOUT = 30
    __sem = threading.BoundedSemaphore(1)

    def acquire(self):
        ''' Acquire semaphore '''
        if not self.__sem.acquire(blocking=True, timeout=self.__SEM_TIMEOUT):
            return False
        return True

    def release(self):
        ''' Release semaphore '''
        try:
            self.__sem.release()
        except ValueError:
            pass
