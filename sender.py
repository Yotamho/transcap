from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from pathlib import Path
from zipfile import ZipFile, ZIP_BZIP2
from os import remove, rename


class Sender:

    def __init__(self, config):
        self.zips_folder = config['GENERAL']['zips_folder']
        self.relay_pcaps_folder = Path(config['RELAY_SERVER']['pcaps_folder'])
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(config['RELAY_SERVER']['host'],
                         username=config['RELAY_SERVER']['username'],
                         password=config['RELAY_SERVER']['password'])
        self.scp = SCPClient(self.ssh.get_transport())
        self.delete_completed = bool(config['GENERAL']['delete_completed'])

    def send(self, file_to_send: Path):
        temp_file_to_send = file_to_send.with_suffix('.tempzip')
        rename(file_to_send, temp_file_to_send)
        self.scp.put(str(temp_file_to_send), str(self.relay_pcaps_folder.as_posix()))
        print('Sent ' + temp_file_to_send.name)
        file_server_path = self.relay_pcaps_folder / temp_file_to_send.name

        if self.delete_completed:
            remove(temp_file_to_send)

        self.ssh.exec_command('mv {} {}'.format(file_server_path.as_posix(),
                                                file_server_path.with_suffix('.zip').as_posix()))

        print('Renamed')

    def zip(self, file_to_zip: Path):
        zip_path = file_to_zip.parents[1] / self.zips_folder / file_to_zip.with_suffix('.zip').name
        with ZipFile(str(zip_path), "w", compression=ZIP_BZIP2) as compressed:
            compressed.write(file_to_zip, file_to_zip.name)
        if self.delete_completed:
            remove(file_to_zip)
        print('Zipped ' + zip_path.name)
        return zip_path
