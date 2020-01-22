def createTag(_name_, _value_=''):

  class Tag:
  
    value = _value_
    _name = _name_
    _origin = _value_
    
    def isModified(self):
      return self.value == self._origin

    def serialize(self):
      return self.value
    
    def deserialize(self, serialized):
      self.value = serialized

    @property
    def name(self):
      return self._name
    
  return Tag
