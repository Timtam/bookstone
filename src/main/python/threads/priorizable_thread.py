from PyQt5.QtCore import QRunnable

from .signal_handler import SignalHandler

class PriorizableThread(QRunnable):

  _cancel = False
  _index = -1
  _priority = -1

  def __init__(self):
    QRunnable.__init__(self)
    
    self.signals = SignalHandler()

  def cancel(self):
    self._cancel = True

  def __lt__(self, other):
    if self._priority == other._priority:
      return self._index < other._index
    return self._priority < other._priority

  def __gt__(self, other):
    if self._priority == other._priority:
      return self._index > other._index
    return self._priority > other._priority

  def __le__(self, other):
    if self._priority == other._priority:
      return self._index <= other._index
    return self._priority <= other._priority

  def __ge__(self, other):
    if self._priority == other._priority:
      return self._index >= other._index
    return self._priority >= other._priority

  def __eq__(self, other):
    return self._index == other._index

  def __ne__(self, other):
    return self._index != other._index

  @property
  def priority(self):
    return self._priority

  @priority.setter
  def priority(self, value):

    if self._priority >= 0:
      raise ValueError('priority can only be set once')

    self._priority = value

  @property
  def index(self):
    return self._index

  @index.setter
  def index(self, value):

    if self._index >= 0:
      raise ValueError('index can only be set once')

    self._index = value
