import gc
import json
from json.decoder import JSONDecodeError
import natsort
import os
import os.path
from PyQt5.QtCore import QObject, pyqtSignal

from . import Library
from .indexer_thread import IndexerThread
from .node import Node
from storage import Storage
from utils import getLibrariesDirectory

class LibraryManager(QObject):

  indexerFinished = pyqtSignal(bool)
  indexerResult = pyqtSignal(Library, Node)
  indexerStarted = pyqtSignal()
  indexerStatusChanged = pyqtSignal(Library, str)

  def __init__(self):

    QObject.__init__(self)

    self._libraries = []
    self._indexer = None
    
  def addLibrary(self, lib):
    self._libraries.append(lib)

  def getLibraries(self):

    return natsort.natsorted(self._libraries[:], key = lambda l: l.getUUID())

  def removeLibrary(self, lib):
    self._libraries.remove(lib)
       
  def load(self, directory):
  
    if not os.path.exists(directory) or not os.path.isdir(directory):
      return
    
    libraries = os.listdir(directory)
    
    for lib in libraries:
    
      libpath = os.path.join(directory, lib)

      with open(libpath, 'r') as libfile:
      
        data = libfile.read()
        
        try:
          ser = json.loads(data)
        except JSONDecodeError:
          continue

        l = Library()
        l.deserialize(ser)
        self._libraries.append(l)

  def save(self, directory):
    
    if not os.path.exists(directory):
      os.makedirs(directory)
      
    # which files do already exist?
    
    libfiles = []
    
    try:
      libfiles = os.listdir(directory)
    except FileNotFoundError:
      pass

    for lib in self._libraries:
      
      libpath = os.path.join(directory, lib.getUUID() + '.json')
      
      with open(libpath, 'w') as libfile:
      
        ser = lib.serialize()
        data = json.dumps(ser, indent = 2)
        
        libfile.write(data)

      try:
        libfiles.remove(lib.getUUID() + '.json')
      except ValueError:
        pass
      
    # all remaining files in libfiles are no longer available / got removed
    for file in libfiles:
      os.remove(os.path.join(directory, file))

  def isIndexing(self):
    return self._indexer is not None

  def startIndexing(self):
  
    if self.isIndexing():
      return False
    
    self._indexer = IndexerThread(self.getLibraries())
    
    self._indexer.signals.statusChanged.connect(self._indexer_status_changed)
    self._indexer.signals.result.connect(self._indexer_result)
    self._indexer.signals.finished.connect(self._indexer_finished)

    Storage.getInstance().getThreadPool().start(self._indexer)
    self.indexerStarted.emit()

  def cancelIndexing(self):
  
    if self._indexer is None:
      return
    
    self._indexer.cancel()
    
    self._indexer.signals.statusChanged.disconnect(self._indexer_status_changed)
    self._indexer.signals.result.disconnect(self._indexer_result)
    self._indexer.signals.finished.disconnect(self._indexer_finished)

    self._indexer = None

  def _indexer_result(self, lib, tree):
    
    self.indexerResult.emit(lib, tree)

    if lib in self._libraries:

      old_tree = lib.getTree()
      old_tree.removeAllChildren()
      gc.collect()

      for child in tree.getChildren():
        old_tree.addChild(child)

      self.save(getLibrariesDirectory())

  def _indexer_finished(self, success):

    self.indexerFinished.emit(success)

    if success:
      self.cancelIndexing()

  def _indexer_status_changed(self, lib, msg):
    self.indexerStatusChanged.emit(lib, msg)
