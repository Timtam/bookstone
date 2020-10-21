import ftplib
import ssl


class UnencryptedFTPSessionFactory(ftplib.FTP):
    def __init__(self, host: str, userid: str, password: str, port: int) -> None:

        super().__init__()

        self.connect(host, port)
        self.login(userid, password)


class EncryptedFTPSessionFactory(ftplib.FTP_TLS):
    def __init__(self, host: str, userid: str, password: str, port: int) -> None:

        super().__init__()

        self.connect(host, port)
        self.auth()
        self.login(userid, password)
        self.prot_p()

    # ssl resumption
    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            session = self.sock.session
            if isinstance(self.sock, ssl.SSLSocket):
                session = self.sock.session
            conn = self.context.wrap_socket(
                conn, server_hostname=self.host, session=session
            )  # this is the fix
        return conn, size
