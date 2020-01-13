import os.path

from storage import Storage

def getAppDirectory():
  return Storage.getInstance().getApplicationContext()._resource_locator._dirs[0]

def getConfigDirectory():
  return os.path.join(getAppDirectory(), 'config')

def getLibrariesDirectory():
  return os.path.join(getConfigDirectory(), 'libraries')
  