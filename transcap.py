from multiprocessing import Process
from configparser import ConfigParser

config = ConfigParser('config.ini')
total_processes = config['PARALLELITY']['total_processes']

if __name__ == '__main__':
    sniffer = Process()
    sniffer.start()
    for process_number in range(1, total_processes + 1):
        spooler = Process()
        spooler.start()
