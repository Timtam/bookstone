import os.path
import pathlib

from .tag_collection import TagCollection

NODE_DIRECTORY = 0
NODE_FILE = 1

class Node:

  def __init__(self, name = '', parent = None):
    
    self._backend = None
    self._name = name
    self._type = NODE_DIRECTORY
    self._children = []
    self._parent = parent
    self._indexed = True
    self._tags = TagCollection()
  
  def setName(self, name):
    self._name = name
  
  def getName(self):
    return self._name
  
  def setDirectory(self):
    self._type = NODE_DIRECTORY
  
  def setFile(self):
    self._type = NODE_FILE
  
  def isDirectory(self):
    return self._type == NODE_DIRECTORY
  
  def isFile(self):
    return self._type == NODE_FILE

  def getChildren(self):
    return self._children[:]

  def addChild(self, child):

    if self.isFile():
      raise IOError('trying to add child {child} to parent {parent}: files cannot have children'.format(child = child, parent = self))

    child.setParent(self)
    child.setBackend(self._backend)
    self._children.append(child)

  def getParent(self):
    return self._parent
    
  def setParent(self, parent):
    self._parent = parent
  
  def getRoot(self):
    
    root = self
    
    while root._parent is not None:
      root = root._parent
    
    return root
  
  def isRoot(self):
    return self._parent is None

  def getPath(self):
  
    if self._parent is None:
      return self._name
    
    return os.path.join(self._parent.getPath(), self._name)

  def serialize(self):

    ser = {
      'name': self._name,
      'type': self._type,
      'children': [],
    }

    for child in self._children:
      ser['children'].append(child.serialize())
    
    if self.isFile():
      ser['tags'] = self._tags.serialize()

    return ser
  
  def deserialize(self, serialized):
  
    self.removeAllChildren()
    self._name = serialized.get('name', '')
    self._type = serialized.get('type', '')
    
    children = serialized.get('children', [])
    
    for child in children:
    
      node = Node()
      node.deserialize(child)
      node.setParent(self)
      node.setBackend(self._backend)
      self._children.append(node)

    if self.isFile():
      self._tags.deserialize(serialized.get('tags', {}))

  def findChild(self, location):
  
    if isinstance(location, Node):
      try:
        path = os.path.relpath(location.getPath(), self.getPath())
      except ValueError:
        if self.getPath() == '':
          path = location.getPath()
        else:
          # paths do not overlap -> child is not in that part of the tree
          return None
    elif isinstance(location, str):
      path = location
    else:
      raise NotImplementedError()

    if not path:
      return self

    parts = pathlib.Path(path).parts
    child_name = parts[0]

    for child in self._children:
      if child._name == child_name:
        if len(parts) == 1:
          return child
        else:
          return child.findChild(os.path.join(*parts[1:]))
    
    return None

  def __str__(self):
    
    desc = '<'
    
    if self.isFile():
      desc = desc + 'File at ' + self.getPath()
    else:
      desc = desc + 'Directory at ' + self.getPath()
    
    desc = desc + '>'
    
    return desc

  def __repr__(self):
    return str(self)

  def removeChild(self, child):
  
    if not child in self._children:
      return
    
    self._children.remove(child)
    
    child.setParent(None)

    child.removeAllChildren()
  
  def removeAllChildren(self):

    for child in self._children:
      child.setParent(None)
      child.removeAllChildren()
      
    self._children.clear()

  def clean(self):
  
    for child in self._children[:]:

      if not child.isIndexed():
        # the element is flagged as 'not indexed', thus it can be dropped
        # if its a directory, it should take all of its children with it
        self.removeChild(child)
        continue

      if child.isDirectory():

        child.clean()

        # directories without supported files don't need to exist in our tree
        if len(child.getChildren()) == 0:
          self.removeChild(child)

  def isIndexed(self):
    return self._indexed
  
  def setIndexed(self):
    self._indexed = True

  def setNotIndexed(self):

    self._indexed = False
    
    for child in self._children:
      child.setNotIndexed()
  
  def setBackend(self, backend):

    self._backend = backend
  
    for child in self._children:
      child.setBackend(backend)

  def getBackend(self):
    return self._backend
  
  # generator to iterate over all files below this node
  def iterFiles(self):
  
    for child in self._children:
      if child.isFile():
        yield child
      else:
        yield from child.iterFiles()
  
  @property
  def tags(self):
  
    if self.isFile():
      return self._tags
    return None