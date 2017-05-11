from dpkt.pcapng import Reader as PCAPReader
from json_packet import JsonPacket
from os import listdir, rename, remove
from pathlib import Path
from json import dump
from traceback import print_exc


class Jsonizer:

    def __init__(self, config, process_number):
        self.pcaps_folder = config['GENERAL']['pcaps_folder']
        self.jsons_folder = config['GENERAL']['jsons_folder']

        self.delete_completed = bool(config['GENERAL']['delete_completed'])

        self.process_number = process_number

    def spool(self):
        while True:
            try:
                files = [filename for filename in listdir(self.pcaps_folder) if filename.endswith(".pcap")]
                if len(files) > 1:
                    files.sort()
                    for file in files[:-1]:
                        path = Path(self.pcaps_folder + '\\' + file)

                        locked_pcap_path = self._lock(path)
                        json_path = locked_pcap_path.parents[1] / self.jsons_folder \
                                    / locked_pcap_path.with_suffix('.json').name

                        with open(json_path, 'w') as json_file:
                            for json_packet in self._read_file(locked_pcap_path):
                                self._dump_to_json(json_packet, json_file)

                        if self.delete_completed:
                            remove(locked_pcap_path)

                        print('Created json ' + json_path.name)
                        yield json_path

            # this exception is thrown when two processes try to rename the same file
            except FileNotFoundError as e:
                pass

            except Exception as e:
                print_exc()

    @staticmethod
    def _read_file(pcap_path):
        with open(pcap_path, 'rb') as pcap_file:
            pcap = PCAPReader(pcap_file)
            for no, (ts, packet) in enumerate(pcap, 1):
                yield JsonPacket(packet, ts, no)

    # assure atomicity
    def _lock(self, pcap_path):
        locked_pcap_path = pcap_path.with_suffix('.' + str(self.process_number) + '.tpcap')
        rename(pcap_path, locked_pcap_path)
        return locked_pcap_path

    @staticmethod
    def _dump_to_json(json_packet, json_file):
        dump(json_packet.dict, json_file)