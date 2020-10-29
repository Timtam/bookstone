from py_singleton import singleton


@singleton
class Storage:

    _application_context = None
    _library_manager = None

    def getApplicationContext(self):
        return self._application_context

    def setApplicationContext(self, context):
        self._application_context = context

    def getLibraryManager(self):
        return self._library_manager

    def setLibraryManager(self, manager):
        self._library_manager = manager
