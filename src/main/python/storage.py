from threads import ThreadPool

class Storage:
  __instance = None

  @staticmethod 
  def getInstance():
    """ Static access method. """
    if Storage.__instance == None:
      Storage()
    return Storage.__instance
  def __init__(self):
    """ Virtually private constructor. """
    if Storage.__instance != None:
      raise Exception("This class is a singleton!")

    Storage.__instance = self

    self._application_context = None
    self._audio_manager = None
    self._library_manager = None
    self._thread_pool = ThreadPool()

  def getApplicationContext(self):
    return self._application_context
  
  def setApplicationContext(self, context):
    self._application_context = context
    
  def getLibraryManager(self):
    return self._library_manager

  def setLibraryManager(self, manager):
    self._library_manager = manager

  def getThreadPool(self):
    return self._thread_pool

  def setAudioManager(self, manager):
    self._audio_manager = manager
  
  def getAudioManager(self):
    return self._audio_manager