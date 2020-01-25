from .tag_collection import TagCollection

class Book:

  def __init__(self, path = ''):
  
    self._path = path
    self._tags = TagCollection()
    
  def serialize(self):
    return {
      'tags': self._tags.serialize(),
      'path': self._path,
    }

  def deserialize(self, serialized):
  
    self._path = serialized.get('path', '')
    tags = serialized.get('tags', {})
    
    self._tags.deserialize(tags)

  def getPath(self):
    return self._path
  
  def setPath(self, path):
    self._path = path

  @property
  def tags(self):
    return self._tags
