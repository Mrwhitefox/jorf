import os
import re
import ssl
import socket
import ftplib
from datetime import datetime
from tqdm import tqdm

FTPTLS_OBJ = ftplib.FTP_TLS

# Class to manage implicit FTP over TLS connections, with passive transfer mode
# - Important note:
#   If you connect to a VSFTPD server, check that the vsftpd.conf file contains
#   the property require_ssl_reuse=NO
class FTPTLS(FTPTLS_OBJ):

    host = "127.0.0.1"
    port = 990
    user = "anonymous"
    timeout = 60

    logLevel = 0

    # Init both this and super
    def __init__(self, host=None, user=None, passwd=None, acct=None, keyfile=None, certfile=None, context=None, timeout=60):        
        FTPTLS_OBJ.__init__(self, host, user, passwd, acct, keyfile, certfile, context, timeout)

    # Custom function: Open a new FTPS session (both connection & login)
    def openSession(self, host="127.0.0.1", port=990, user="anonymous", password=None, timeout=60):
        self.user = user
        # connect()
        ret = self.connect(host, port, timeout)
        # prot_p(): Set up secure data connection.
        try:
            ret = self.prot_p()
            if (self.logLevel > 1): self._log("INFO - FTPS prot_p() done: " + ret)
        except Exception as e:
            if (self.logLevel > 0): self._log("ERROR - FTPS prot_p() failed - " + str(e))
            raise e
        # login()
        try:
            ret = self.login(user=user, passwd=password)
            if (self.logLevel > 1): self._log("INFO - FTPS login() done: " + ret)
        except Exception as e:
            if (self.logLevel > 0): self._log("ERROR - FTPS login() failed - " + str(e))
            raise e
        if (self.logLevel > 1): self._log("INFO - FTPS session successfully opened")

    # Override function
    def connect(self, host="127.0.0.1", port=990, timeout=60):
        self.host = host
        self.port = port
        self.timeout = timeout
        try:
            self.sock = socket.create_connection((self.host, self.port), self.timeout)
            self.af = self.sock.family
            self.sock = ssl.wrap_socket(self.sock, self.keyfile, self.certfile)
            self.file = self.sock.makefile('r')
            self.welcome = self.getresp()
            if (self.logLevel > 1): self._log("INFO - FTPS connect() done: " + self.welcome)
        except Exception as e:
            if (self.logLevel > 0): self._log("ERROR - FTPS connect() failed - " + str(e))
            raise e
        return self.welcome

    # Override function
    def makepasv(self):
        host, port = FTPTLS_OBJ.makepasv(self)
        # Change the host back to the original IP that was used for the connection
        host = socket.gethostbyname(self.host)
        return host, port

    # Custom function: Close the session
    def closeSession(self):
        try:
            self.close()
            if (self.logLevel > 1): self._log("INFO - FTPS close() done")
        except Exception as e:
            if (self.logLevel > 0): self._log("ERROR - FTPS close() failed - " + str(e))
            raise e
        if (self.logLevel > 1): self._log("INFO - FTPS session successfully closed")

    # Private method for logs
    def _log(self, msg):
        # Be free here on how to implement your own way to redirect logs (e.g: to a console, to a file, etc.)
        print(msg)



class FTPClient:
    def __init__(self, host, verbose=False):
        '''Inits connexion with the distant FTP server.'''

        self.verbose = verbose

        if self.verbose:
            print('Attempting secure connexion to {}...'.format(host))

        # ping echanges.dila.gouv.fr
        # 185.24.187.136
        self.host = host
        self.ftp = FTPTLS()
        self.ftp.connect(host=self.host, port=990)
        self.ftp.login()
        self.ftp.prot_p()

    def retrieveFiles(self, dirPath, outputFolder, downloadsLogFile=None,
                      regex=None, downloadFreemium=True):
        '''Downloads all files in a given directory.'''

        self.ftp.cwd(dirPath)
        fileNames = self.ftp.nlst()
        previouslyDownloadedFileList = []

        if downloadsLogFile and os.path.isfile(downloadsLogFile):
            with open(downloadsLogFile, 'r') as f:
                for line in f:
                    previouslyDownloadedFileList.append(line.split(';')[1].rstrip())

        if self.verbose:
            print('Retrieved file list.')

        if regex:
            fileNames = list(filter(lambda x: re.match(regex, x), fileNames))

        if self.verbose:
            print('Downloading tarballs...')

        for fileName in tqdm(fileNames):
            definitiveOutputFolder = outputFolder

            # If the file's name doesn't contain 'Freemium', then it is
            # an incremental file and thus goes to the incremental folder.
            if not re.match('.*Freemium.*', fileName):
                definitiveOutputFolder = os.path.join(outputFolder, 'incremental')
            elif not downloadFreemium:
                continue

            if re.match('.*\.tar\.gz', fileName) and (fileName not in previouslyDownloadedFileList):
                with open(os.path.join(definitiveOutputFolder, fileName), 'wb') as f:
                    self.ftp.retrbinary('RETR {}'.format(fileName), f.write)

                if downloadsLogFile:
                    with open(downloadsLogFile, 'a+') as f:
                        f.write('{};{}\n'.format(str(datetime.now()), fileName))

    def terminate(self):
        '''Terminate FTP connexion.'''

        self.ftp.quit()
