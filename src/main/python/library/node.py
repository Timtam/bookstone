import os.path
import pathlib

NODE_DIRECTORY = 0
NODE_FILE = 1

class Node:

  def __init__(self, name = '', parent = None):
    
    self._name = name
    self._type = NODE_DIRECTORY
    self._children = []
    self._parent = parent
  
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
    
    return ser
  
  def deserialize(self, serialized):
  
    self._name = serialized.get('name', '')
    self._type = serialized.get('type', '')
    
    children = serialized.get('children', [])
    
    for child in children:
    
      node = Node()
      node.deserialize(child)
      node.setParent(self)
      self._children.append(node)

  def findChild(self, location):
  
    if isinstance(location, Node):
      path = location.getPath()
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
