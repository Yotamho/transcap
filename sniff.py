from subprocess import call
from os.path import exists
from os import makedirs

def sniff(config):

    interface = config['GENERAL']['interface']
    pcap_kb_filesize = config['GENERAL']['pcap_kb_filesize']
    pcaps_folder = config["GENERAL"]["pcaps_folder"]
    pcaps_file_name = config["GENERAL"]["pcaps_file_name"]

    if not exists(pcaps_folder):
        makedirs(pcaps_folder)

    tshark_call = "tshark -i {} -b filesize:{} -w {}\\{} -B 20".format(
        interface, pcap_kb_filesize, pcaps_folder, pcaps_file_name)
    try:
        print("Sniffing Started")
        call(['cmd', '/c', tshark_call])
    except KeyboardInterrupt:
        print("Sniffing Stopped")

if __name__ == "__main__":
    sniff()