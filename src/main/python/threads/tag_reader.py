import mutagen
from PyQt5.QtCore import pyqtSlot

from .priorizable_thread import PriorizableThread
from library.tags import Tags

class TagReaderThread(PriorizableThread):

  def __init__(self, node):
  
    PriorizableThread.__init__(self)
    
    self._node = node
    self.priority = 5
  
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

  @pyqtSlot()
  def run(self):
  
    node = self._node
    backend = self._node.getBackend()

    #self.signals.statusChanged.emit(library, 'reading stats from {name}'.format(name = node.getName()))
      
    stats = backend.getStats(node.getPath())

    if stats.st_size == node.getSize() and stats.st_mtime == node.getModificationTime():
      self.signals.finished.emit(True)
      return

    #self.signals.statusChanged.emit(library, 'reading tags from {name}'.format(name = node.getName()))
      
    # creating the stream
    file = backend.openFile(node.getPath())

    tags_reader = mutagen.File(file)
    node.tags['title'].value = self.getTitleTag(tags_reader.tags)
    node.tags['author'].value = self.getAuthorTag(tags_reader.tags)
    file.close()
      
    node.setModificationTime(stats.st_mtime)
    node.setSize(stats.st_size)

    self.signals.finished.emit(True)
