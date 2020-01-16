from storage import Storage

class WindowController:
  __instance = None

  @staticmethod 
  def getInstance():
    """ Static access method. """
    if WindowController.__instance == None:
      WindowController()
    return WindowController.__instance
  def __init__(self):
    """ Virtually private constructor. """
    if WindowController.__instance != None:
      raise Exception("This class is a singleton!")

    WindowController.__instance = self

    self._window_stack = []
  
  def pushWindow(self, window):
  
    self._window_stack.append(window)
    window.closed.connect(self.popWindow)
    
    try:
      self._window_stack[-2].hide()
    except IndexError:
      pass
    
    window.show()
  
  def popWindow(self):
  
    current = self._window_stack[-1]
    current.hide()
    current.deleteLater()
    
    del self._window_stack[-1]
    
    try:
      self._window_stack[-1].show()
    except IndexError:
      Storage.getInstance().getApplicationContext().app.exit()
