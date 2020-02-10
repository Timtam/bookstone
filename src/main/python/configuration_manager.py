import json
from json.decoder import JSONDecodeError
import os.path

class ConfigurationManager:

  def __init__(self):
  
    __dict__ = super(ConfigurationManager, self).__getattribute__('__dict__')

    __dict__['_configs'] = {}
    
    # configure default values
    self.init()
  
  def _add(self, key, value):

    __dict__ = super(ConfigurationManager, self).__getattribute__('__dict__')

    __dict__['_configs'][key] = value

  def init(self):

    self._add('askBeforeCloseWhenIndexing', True)
  
  def __getattribute__(self, name):
  
    try:
      return super(ConfigurationManager, self).__getattribute__(name)
    except AttributeError:
      pass

    __dict__ = super(ConfigurationManager, self).__getattribute__('__dict__')

    if name in __dict__['_configs']:
      return __dict__['_configs'][name]
  
    raise AttributeError("ConfigurationManager object has no attribute '{name}'".format(name = name))

  def __setattr__(self, name, value):
  
    __dict__ = super(ConfigurationManager, self).__getattribute__('__dict__')
    
    if name not in __dict__['_configs']:
      raise AttributeError("ConfigurationManager object has no attribute '{name}'".format(name = name))
    
    __dict__['_configs'][name] = value
  
  def load(self, file):
  
    if not os.path.exists(file):
      return
    
    with open(file, 'r') as f:
      data = f.read()
      
      try:
        ser = json.loads(data)
      except JSONDecodeError:
        return
      
      __dict__ = super(ConfigurationManager, self).__getattribute__('__dict__')

      for name, value in ser.items():
        
        if name not in __dict__['_configs']:
          continue
        
        __dict__['_configs'][name] = value

  def save(self, file):
  
    __dict__ = super(ConfigurationManager, self).__getattribute__('__dict__')

    data = json.dumps(__dict__['_configs'], indent = 2)
    
    with open(file, 'w') as f:
      f.write(data)

