import uuid

from backends import Backends

class Library:

  def __init__(self):

    self._backend = None
    self._uuid = str(uuid.uuid4())
    self._name = ''
  
  def getBackend(self):
    return self._backend
  
  def setBackend(self, backend):
    self._backend = backend

    if self._name == '':
      self._name = backend.getPath()
  
  def serialize(self):
    return {
      'name': self._name,
      'backendName': self._backend.getName(),
      'backend': self._backend.serialize(),
      'uuid': self._uuid,
    }

  def deserialize(self, serialized):
    
    name = serialized.get('backendName', '')
    
    backend = None

    for b in Backends:
      if b.getName() == name:
        backend = b()
        break
    
    if not backend:
      raise IOError('backend with name {name} not found'.format(name = name))
    
    ser = serialized.get('backend', '')
    
    if not ser:
      raise IOError('no backend data supplied')
    
    backend.deserialize(ser)
    
    self._backend = backend
    self._uuid = serialized.get('uuid', '')
    self._name = serialized.get('name', '')
    
    if not self._uuid:
      raise IOError('no valid UUID found')

  def getUUID(self):
    return self._uuid
  
  def __eq__(self, lib):
    if isinstance(lib, Library):
      return self._uuid == lib._uuid
    elif isinstance(lib, str):
      return self._uuid == lib
    else:
      return NotImplemented

  def getName(self):
    return self._name
  
  def setName(self, name):
    self._name = name