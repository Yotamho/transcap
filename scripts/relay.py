import os
from configparser import ConfigParser
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from pathlib import Path


class Relay:

    def __init__(self):
        config = ConfigParser()
        config.read(str(Path.cwd().parent / 'real_config.ini'))

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
            for file in os.listdir(str(self.relay_pcaps_folder)):
                if file.endswith('.zip'):
                    temp_file_to_send = (self.relay_pcaps_folder / file).with_suffix('.tempzip')
                    os.rename(str(self.relay_pcaps_folder / file), str(temp_file_to_send))
                    self.scp.put(str(temp_file_to_send), str(self.db_server_pcaps_folder))
                    self.ssh.exec_command('mv {} {}'.format(self.db_server_pcaps_folder / temp_file_to_send.name,
                                                            (self.db_server_pcaps_folder / temp_file_to_send.name)
                                                            .with_suffix('.zip')))
                    os.remove(str(temp_file_to_send))
if __name__ == "__main__":
        relay = Relay()
        relay.spool()