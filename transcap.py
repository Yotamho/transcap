from multiprocessing import Process
from configparser import ConfigParser
from sniff import sniff

config = ConfigParser()
config.read('real_config.ini')
total_processes = config['PARALLELITY']['total_processes']

if __name__ == '__main__':
    sniffer = Process(target=sniff, args=[config])
    sniffer.start()
    # for process_number in range(1, total_processes + 1):
    #     spooler = Process()
    #     spooler.start()
