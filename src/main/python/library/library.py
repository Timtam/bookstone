import uuid

from backends import Backends
from .book import Book
from .node import Node

class Library:

  def __init__(self):

    self._backend = None
    self._books = []
    self._uuid = str(uuid.uuid4())
    self._name = ''
    self._tree = Node()
  
  def getBackend(self):
    return self._backend
  
  def setBackend(self, backend):
    self._backend = backend

    if self._tree is not None:
      self._tree.setBackend(self._backend)

    if self._name == '':
      self._name = backend.getPath()
  
  def serialize(self):
    return {
      'name': self._name,
      'backendName': self._backend.getName(),
      'backend': self._backend.serialize(),
      'uuid': self._uuid,
      'tree': self._tree.serialize(),
      'books': [b.serialize() for b in self._books],
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
    self._tree.setBackend(self._backend)
    self._uuid = serialized.get('uuid', '')
    self._name = serialized.get('name', '')
    
    if not self._uuid:
      raise IOError('no valid UUID found')

    tree = serialized.get('tree', '')
    
    if tree != '':
      self._tree.deserialize(tree)

    books = serialized.get('books', [])
    
    for book in books:
    
      b = Book()
      b.deserialize(book)
      
      self._books.append(b)
    
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

  def getTree(self):
    return self._tree

  def getBooks(self):
    return self._books[:]
    