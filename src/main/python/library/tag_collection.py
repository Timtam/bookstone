from collections import UserDict

from .tags import Tags

class TagCollection(UserDict):

  def __init__(self):
    UserDict.__init__(self)
    
    for tag in Tags:
      self.add(tag())

  def __delitem__(self, idx):
    raise IndexError('you cannot remove tags')
  
  def add(self, tag):
  
    self[tag.name] = tag

  def serialize(self):
  
    res = {}
    
    for tag in self.data.values():
      if tag.isModified():
        res[tag.name] = tag.value
    
    return res
  
  def deserialize(self, serialized):
  
    for name, value in serialized.items():
      
      try:
        tag = self[name]
        
        tag.value = value
      except IndexError:
        pass
