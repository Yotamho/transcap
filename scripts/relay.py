import os
from configparser import ConfigParser
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from pathlib import Path


class Relay:

    def __init__(self):
        config = ConfigParser()
        config.read('config.ini')

        self.relay_pcaps_folder = Path(config['RELAY_SERVER']['pcaps_folder'])
        self.db_server_pcaps_folder = Path(config['DB_SERVER']['pcaps_folder'])

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(
            hostname=config['DB_SERVER']['host'],
            username=config['DB_SERVER']['username'],
            password=config['DB_SERVER']['password']
        )
        self.scp = SCPClient(self.ssh.get_transport())

    def spool(self):
        while True:
            for file in os.listdir(self.relay_pcaps_folder):
                if file.endswith('.readyzip'):
                    self.scp.put(self.relay_pcaps_folder / file, self.db_server_pcaps_folder)
                    self.ssh.exec_command('mv {} {}'.format(self.db_server_pcaps_folder / file,
                                                            (self.db_server_pcaps_folder / file).with_suffix('zip')))
