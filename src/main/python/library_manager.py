import json
import os
import os.path

from library import Library

class LibraryManager:

  def __init__(self):
    self._libraries = []
    
  def addLibrary(self, lib):
    self._libraries.append(lib)

  def getLibraries(self):
    return self._libraries[:]

  def removeLibrary(self, lib):
    self._libraries.remove(lib)
       
  def load(self, directory):
  
    if not os.path.exists(directory) or not os.path.isdir(directory):
      return
    
    libraries = os.listdir(directory)
    
    for lib in libraries:
    
      libpath = os.path.join(directory, lib)

      with open(libpath, 'r') as libfile:
      
        data = libfile.read()
        
        ser = json.loads(data)

        l = Library()
        l.deserialize(ser)
        self._libraries.append(l)

  def save(self, directory):
    
    if not os.path.exists(directory):
      os.makedirs(directory)
      
    # which files do already exist?
    
    libfiles = []
    
    try:
      libfiles = os.listdir(directory)
    except FileNotFoundError:
      pass

    for lib in self._libraries:
      
      libpath = os.path.join(directory, lib.getUUID() + '.json')
      
      with open(libpath, 'w') as libfile:
      
        ser = lib.serialize()
        data = json.dumps(ser)
        
        libfile.write(data)

      try:
        libfiles.remove(lib.getUUID() + '.json')
      except ValueError:
        pass
      
    # all remaining files in libfiles are no longer available / got removed
    for file in libfiles:
      os.remove(os.path.join(directory, file))
