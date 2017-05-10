from dpkt.pcapng import Reader as PCAPReader
from json_packet import JsonPacket
from sender import Sender
from os import listdir
from pathlib import Path


class Reader:

    def __init__(self, config):
        self.pcaps_folder = config['GENERAL']['pcaps_folder']

    def spool(self):
        while True:
            try:
                files = [filename for filename in listdir(self.pcaps_folder) if filename.endswith(".pcap")]
                if len(files) > 1:
                    files.sort()
                    for file in files[:-1]:
                        path = Path('\\' + self.pcaps_folder + '\\' + file)
                        locked_path = self._lock(path)
                        json_path = self._read_file(locked_path)
                        zip_path = self._zip_json(json_path)
                        yield zip_path
            except Exception as e:
                # add logging
                pass

    @staticmethod
    def _read_file(pcap_path):
        with open(pcap_path, 'rb') as pcap_file:
            pcap = PCAPReader(pcap_file)
            for no, (ts, packet) in enumerate(pcap, 1):
                yield JsonPacket(packet, ts, no)

    def _lock(self, pcap_path):
        pass