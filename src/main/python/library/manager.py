import gc
import json
from json.decoder import JSONDecodeError
import natsort
import os
import os.path
from PyQt5.QtCore import QObject, pyqtSignal

from . import Library
from .node import Node
from storage import Storage
from threads.folder_structure_reader import FolderStructureReaderThread
from threads.tag_reader import TagReaderThread
from utils import getLibrariesDirectory

# keeps track of all libraries
# it also manages the library indexing process by enqueuing threads where necessary
class LibraryManager(QObject):

  indexingFinished = pyqtSignal(bool)
  #indexerResult = pyqtSignal(Library, Node)
  indexingStarted = pyqtSignal()
  #indexerStatusChanged = pyqtSignal(Library, str)

  def __init__(self):

    QObject.__init__(self)

    self._libraries = []
    
    Storage.getInstance().getThreadPool().signals.threadFinished.connect(self._thread_finished)

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
    return Storage.getInstance().getThreadPool().currentThreadCount > 0 or Storage.getInstance().getThreadPool().waitingThreadCount > 0 

  def startIndexing(self):
  
    if self.isIndexing():
      return False
    
    pool = Storage.getInstance().getThreadPool()

    for lib in self._libraries:
      thread = FolderStructureReaderThread(lib)
      
      thread.signals.result.connect(self._thread_result)

      pool.enqueue(thread)

    self.indexingStarted.emit()

  def cancelIndexing(self):
  
    if not self.isIndexing():
      return
    
    Storage.getInstance().getThreadPool().cancelAll()
    
  def _thread_result(self, params):
    
    lib, tree = params

    #self.indexerResult.emit(lib, tree)

    if lib in self._libraries:

      old_tree = lib.getTree()
      old_tree.removeAllChildren()
      gc.collect()

      for child in tree.getChildren():
        old_tree.addChild(child)

      pool = Storage.getInstance().getThreadPool()

      for file in old_tree.iterFiles():
      
        thread = TagReaderThread(file)

        pool.enqueue(thread)

  def _thread_finished(self, thread, success):

    pool = Storage.getInstance().getThreadPool()
    
    if pool.currentThreadCount == 0 and pool.waitingThreadCount == 0:

      self.save(getLibrariesDirectory())

      self.indexingFinished.emit(success)

  def _indexer_status_changed(self, lib, msg):
    self.indexerStatusChanged.emit(lib, msg)
