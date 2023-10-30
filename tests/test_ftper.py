
from sky_eye import ftper
import unittest
import os
from pathlib import Path

class TestFtper(unittest.TestCase):

    FTP_URL = "127.0.0.1"
    FTP_USERNAME = "testuser"
    FTP_PASSWD = "testpasswd"
    FTP_DIR = Path(f"tests/ftpout/{FTP_USERNAME}")
 

    def setUp(self) -> None:
        print("setUp")
        # check that tests/ftpout/testuser exists
        self.assertTrue(os.path.exists(self.FTP_DIR), f"directory {self.FTP_DIR} does not exist")

        # remove any files in the directory
        for file in os.listdir(self.FTP_DIR):
            file_path = os.path.join(self.FTP_DIR, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
            #
        #
        print(f"deleted all files in {self.FTP_DIR}")

    def test_server_active(self) -> None:
        # verify that ftp server at FTP_URL is reachable
        # verify that FTP_USERNAME and FTP_PASSWD are correct
        myftp = ftper.Ftper(self.FTP_URL, self.FTP_USERNAME, self.FTP_PASSWD)
        retval = myftp.check_server
        self.assertTrue(retval)

    def test_successful_transfer(self) -> None:
        print("test_successful_transfer")
        # verify that ftp server at FTP_URL is reachable
        # verify that FTP_USERNAME and FTP_PASSWD are correct
        myftp = ftper.Ftper(self.FTP_URL, self.FTP_USERNAME, self.FTP_PASSWD)
        myftp.transfer("tests/test_ftper.py")
        # verify that the file was transferred
        dest_path = self.FTP_DIR / "test_ftper.py"
        self.assertTrue(dest_path.exists())

