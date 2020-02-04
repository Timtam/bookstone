import copy
import os.path
import queue
from PyQt5.QtCore import pyqtSlot

from .priorizable_thread import PriorizableThread
from library.node import Node
from storage import Storage
from utils import getSupportedFileExtensions

class FolderStructureReaderThread(PriorizableThread):

  def __init__(self, library):

    PriorizableThread.__init__(self)

    self._library = library
    self.priority = 0

  @pyqtSlot()
  def run(self):

    lib = self._library

    #self.signals.statusChanged.emit(lib, 'Starting index operation')

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

      #self.signals.statusChanged.emit(lib, 'Processing {path}'.format(path=next_path))
        
      dir_list = backend.listDirectory(next_path)
        
      for dir in dir_list:
          
        if self._cancel:
          self.signals.finished.emit(False)
          return

        new = tree.findChild(os.path.join(next_path, dir))
          
        if new is None:
          new = Node()
          new.setName(dir)
            
        if backend.isDirectory(os.path.join(next_path, dir)):
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

    self.signals.result.emit((lib, tree, ))
          
    self.signals.finished.emit(True)
