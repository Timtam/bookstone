import copy
import os.path
import queue
from PyQt5.QtCore import QRunnable, pyqtSlot

from .indexer_signal_handler import IndexerSignalHandler
from .node import Node
from utils import getSupportedFileExtensions

class IndexerThread(QRunnable):

  signals = IndexerSignalHandler()
  
  def __init__(self, libraries):

    QRunnable.__init__(self)

    self._libraries = libraries
    self._cancel = False

  @pyqtSlot()
  def run(self):

    for lib in self._libraries:
    
      self.signals.statusChanged.emit(lib, 'Starting index operation')

      # we need to create a deep copy of the entire directory tree
      # that is required to not disturb running operations in the gui thread
      tree = copy.deepcopy(lib.getTree())
      
      tree.setNotIndexed()

      backend = lib.getBackend()
      
      open = queue.Queue()
      
      open.put(tree)
      
      while not open.empty():
        
        if self._cancel:
          self.signals.finished.emit(False)
          return

        next = open.get()
        
        next_path = next.getPath()

        self.signals.statusChanged.emit(lib, 'Processing {path}'.format(path=next_path))
        
        dir_list = backend.listDirectory(os.path.join(backend.getPath(), next_path))
        
        for dir in dir_list:
          
          if self._cancel:
            self.signals.finished.emit(False)
            return

          new = tree.findChild(os.path.join(next_path, dir))
          
          if new is None:
            new = Node()
            new.setName(dir)
            
          if backend.isDirectory(os.path.join(backend.getPath(), next_path, dir)):
            new.setDirectory()
          else:
            new.setFile()
            
          if new.isFile():
          
            # check file extensions
            _, ext = os.path.splitext(new.getName())

            if not ext.lower() in getSupportedFileExtensions():
              if new.getParent() is not None:
                next.removeChild(new)
              continue            
            else:
              new.setIndexed()

          if next.findChild(new) is None:
            next.addChild(new)

          if new.isDirectory():
            open.put(new)

        next.setIndexed()

      tree.clean()

      self.signals.result.emit(lib, tree)
          
    self.signals.finished.emit(True)

  def cancel(self):
    self._cancel = True
