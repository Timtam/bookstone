import copy
import os.path
import queue
from PyQt5.QtCore import QRunnable, pyqtSlot

from .indexer_signal_handler import IndexerSignalHandler
from .node import Node

class IndexerThread(QRunnable):

  signals = IndexerSignalHandler()
  
  def __init__(self, libraries):

    QRunnable.__init__(self)

    self._libraries = libraries

  @pyqtSlot()
  def run(self):

    for lib in self._libraries:
    
      self.signals.statusChanged.emit(lib, 'Starting index operation')

      # we need to create a deep copy of the entire directory tree
      # that is required to not disturb running operations in the gui thread
      tree = copy.deepcopy(lib.getTree())
      
      backend = lib.getBackend()
      
      open = queue.Queue()
      
      open.put(tree)
      
      while not open.empty():
        
        next = open.get()
        
        next_path = next.getPath()

        self.signals.statusChanged.emit(lib, 'Processing {path}'.format(path=next_path))
        
        dir_list = backend.listDirectory(os.path.join(backend.getPath(), next_path))
        
        for dir in dir_list:
          
          new = tree.findChild(os.path.join(next_path, dir))
          
          if new is None:
            new = Node()
            new.setName(dir)
            
          if backend.isDirectory(os.path.join(backend.getPath(), next_path, dir)):
            new.setDirectory()
          else:
            new.setFile()
            
          if next.findChild(new) is None:
            next.addChild(new)

          if new.isDirectory():
            open.put(new)

      self.signals.result.emit(lib, tree)
          
    self.signals.finished.emit()