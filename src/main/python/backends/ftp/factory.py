import ftplib

class UnencryptedFTPSessionFactory(ftplib.FTP):

  def __init__(self, host, userid, password, port):
    
    ftplib.FTP.__init__(self)
    
    self.connect(host, port)
    self.login(userid, password)

class EncryptedFTPSessionFactory(ftplib.FTP_TLS):

  def __init__(self, host, userid, password, port):
    
    ftplib.FTP_TLS.__init__(self)
    
    self.connect(host, port)
    self.auth()
    self.login(userid, password)
    self.prot_p()
