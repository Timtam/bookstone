import heapq
import itertools
import os
from PyQt5.QtCore import QThreadPool, QMutex

from .thread_pool_signal_handler import ThreadPoolSignalHandler

class ThreadPool(QThreadPool):

  def __init__(self):
    QThreadPool.__init__(self)

    self._counter = itertools.count()
    self._waiting = []
    self._running = []
    self._thread_mutex = QMutex()
    self.signals = ThreadPoolSignalHandler()

  # add a new thread to the pool and run it if necessary
  def enqueue(self, thread):
    
    self._thread_mutex.lock()

    thread.index = next(self._counter)

    heapq.heappush(self._waiting, thread)

    self._thread_mutex.unlock()

    self._run_threads()

  # try to run as many waiting threads as possible until maxThreadCount is reached
  def _run_threads(self):
  
    def gen_lambda(thread):
      return lambda s: self._finished_handler(thread, s)

    if self.maxThreadCount == self.currentThreadCount:
      return
  
    self._thread_mutex.lock()

    for i in range(self.maxThreadCount - self.currentThreadCount):

      if len(self._waiting) == 0:
        break

      new_thread = heapq.heappop(self._waiting)

      new_thread.signals.finished.connect(gen_lambda(new_thread))

      self._running.append(new_thread)
      print('now running new thread with index {index}'.format(index = new_thread.index))
      self.start(new_thread)

    self._thread_mutex.unlock()

  # called whenever a thread finishes
  # remove the thread and run others when necessary
  def _finished_handler(self, thread, success):

    self._thread_mutex.lock()

    print('thread {index} finished running'.format(index = thread.index))
    self._running.remove(thread)
    
    self._thread_mutex.unlock()

    self.signals.threadFinished.emit(thread, success)

    self._run_threads()

  @property
  def maxThreadCount(self):
    return os.cpu_count()
  
  @property
  def currentThreadCount(self):
    return len(self._running)
    
  @property
  def waitingThreadCount(self):
    return len(self._waiting)