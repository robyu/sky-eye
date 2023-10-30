import ftplib
from pathlib import Path
import time

class Ftper:
    def __init__(self, dest_url, username, passwd):
        self.dest_url = dest_url
        self.username = username
        self.passwd = passwd
        self.timeout_sec = 10

    def check_server(self):
        """
        check that dest_url is reachable
        """
        success_flag = True
        try:
            with ftplib.FTP(self.dest_url, self.username, self.passwd, timeout=self.timeout_sec) as ftp:
                self.ftp.set_pasv(True)
            #
        except ftplib.error_temp as e:
            print(f'FTP error: {e}')
            success_flag = False
        #
        return success_flag


    def transfer(self, src_fname):
        """
        open dest_url, login as "username", transfer src_fname
        """
        success_flag = False
        try_count = 0
        while success_flag==False and try_count < 3:
            try:
                with ftplib.FTP(self.dest_url, self.username, self.passwd, timeout=self.timeout_sec) as ftp:
                    ftp.set_pasv(True)
                    
                    with open(src_fname, 'rb') as f:
                        ftp.storbinary(f'STOR {Path(src_fname).name}', f)
                    #

            except ftplib.all_errors as e:
                print(f'FTP error: {e}')
                success_flag = False
            else:
                success_flag = True
            #
            try_count += 1

            if success_flag==False:
                print(f"transfer #{try_count} failed; sleep then retry")
                time.sleep(1)
            else:
                print("transfer successful")
            #
        #

        return success_flag


