import copy
import mutagen
import os.path
import queue
from PyQt5.QtCore import QRunnable, pyqtSlot

from .indexer_signal_handler import IndexerSignalHandler
from .node import Node
from .tags import Tags
from storage import Storage
from utils import getSupportedFileExtensions

class IndexerThread(QRunnable):

  signals = IndexerSignalHandler()
  
  def __init__(self, libraries):

    QRunnable.__init__(self)

    self._libraries = libraries
    self._cancel = False

  def getDefaultValueForTag(self, name):
  
    for tag in Tags:
      if tag.name == name:
        return tag.default
    return None

  def getTagValueFromKeys(self, tags, keys):
  
    for key in keys:
      try:
        if isinstance(tags[key].text, list):
          return tags[key].text[0]
        return tags[key].text
      except KeyError:
        continue
    return None
        
  def getTitleTag(self, tags):
  
    keys = (
      'TIT2',
    )
    
    tag = self.getTagValueFromKeys(tags, keys)

    if tag is None:
      return self.getDefaultValueForTag('title')
    return tag

  def getAuthorTag(self, tags):
  
    keys = (
      'TPE1',
    )
    
    tag = self.getTagValueFromKeys(tags, keys)

    if tag is None:
      return self.getDefaultValueForTag('author')
    return tag

  def indexFiles(self, library, tree):
  
    backend = library.getBackend()

    # iterating over all files within the directory tree
    for node in tree.iterFiles():
    
      self.signals.statusChanged.emit(library, 'reading stats from {name}'.format(name = node.getName()))
      
      stats = backend.getStats(node.getPath())

      if stats.st_size != node.getSize() or stats.st_mtime != node.getModificationTime():

        self.signals.statusChanged.emit(library, 'reading tags from {name}'.format(name = node.getName()))
      
        # creating the stream
        file = backend.openFile(node.getPath())

        tags_reader = mutagen.File(file)
        node.tags['title'].value = self.getTitleTag(tags_reader.tags)
        node.tags['author'].value = self.getAuthorTag(tags_reader.tags)
        file.close()
      
        node.setModificationTime(stats.st_mtime)
        node.setSize(stats.st_size)

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
      self.indexFiles(lib, tree)

      self.signals.result.emit(lib, tree)
          
    self.signals.finished.emit(True)

  def cancel(self):
    self._cancel = True
