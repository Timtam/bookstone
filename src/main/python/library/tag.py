def createTag(name, value=''):

  class Tag:
  
    value = value
    _name = name
    _origin = value
    
    def isModified(self):
      return self.value == self._origin

    def serialize(self):
      return value
    
    def deserialize(self, serialized):
      self.value = serialized

    @property
    def name(self):
      return self._name
    
    return Tag
