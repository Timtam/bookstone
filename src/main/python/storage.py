from py_singleton import singleton

from threads import ThreadPool


@singleton
class Storage:

    _application_context = None
    _audio_manager = None
    _configuration_manager = None
    _library_manager = None
    _thread_pool: ThreadPool = ThreadPool()

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

    def setConfigurationManager(self, manager):
        self._configuration_manager = manager

    def getConfigurationManager(self):
        return self._configuration_manager
