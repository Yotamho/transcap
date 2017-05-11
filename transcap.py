from multiprocessing import Process
from configparser import ConfigParser
from os import makedirs

from os.path import exists

from jsonizer import Jsonizer
from sender import Sender
from sniff import sniff

config = ConfigParser()
config.read('real_config.ini')
total_processes = int(config['PARALLELITY']['total_processes'])
pcaps_folder = config['GENERAL']['pcaps_folder']
jsons_folder = config['GENERAL']['jsons_folder']
zips_folder = config['GENERAL']['zips_folder']


def jsonize_and_send(process_number_input, config_input):
    jsonizer = Jsonizer(config_input, process_number_input)
    sender = Sender(config_input)
    for json in jsonizer.spool():
        zip_path = sender.zip(json)
        sender.send(zip_path)


if __name__ == '__main__':

    if not exists(pcaps_folder):
        makedirs(pcaps_folder)

    if not exists(jsons_folder):
        makedirs(jsons_folder)

    if not exists(zips_folder):
        makedirs(zips_folder)

    # jsonize_and_send(1, config)

    sniffer = Process(target=sniff, args=[config])
    sniffer.start()
    for process_number in range(1, total_processes + 1):
        spooler = Process(target=jsonize_and_send, args=[process_number, config])
        spooler.start()


