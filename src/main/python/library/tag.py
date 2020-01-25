def createTag(_name_, _value_=''):

  class Tag:
  
    value = _value_
    _name = _name_
    _default = _value_
    
    def isModified(self):
      return self.value != self._default

    def serialize(self):
      return self.value
    
    def deserialize(self, serialized):
      self.value = serialized

    @property
    def name(self):
      return self._name
    
    @property
    def default(self):
      return self._default

    def __str__(self):
      return 'Tag[{name}] = {value}'.format(name = self._name, value = self.value)

    def __repr__(self):
      return str(self)

  return Tag
