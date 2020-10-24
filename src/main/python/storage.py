from py_singleton import singleton

from threads.thread_pool import ThreadPool


@singleton
class Storage:

    _application_context = None
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
