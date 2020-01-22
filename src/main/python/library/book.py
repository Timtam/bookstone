from .tag_collection import TagCollection
from .tags import Tags

class Book:

  def __init__(self):
  
    self._tags = TagCollection()
    
    for tag in Tags:
      self._tags.add(Tag())

  def serialize(self):
    return {
      'tags': self._tags.serialize(),
    }

  def deserialize(self, serialized):
  
    tags = serialized.get('tags', {})
    
    self._tags.deserialize(tags)

  @property
  def tags(self):
    return self._tags
