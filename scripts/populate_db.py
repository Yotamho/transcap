from configparser import ConfigParser
from pathlib import Path
from zipfile import ZipFile
from os import remove
from cassandra.cluster import Cluster
from os import listdir
from json import loads


config = ConfigParser()
config.read(config.read(Path.cwd().parent / 'real_config.ini'))
db_server_pcaps_folder = Path(config['DB_SERVER']['pcaps_folder'])
tables_list = config['DB_SERVER']['tables'].split(',')
db_address = config['DB_SERVER']['db_address']
db_keyspace = config['DB_SERVER']['db_keyspace']

# On implementation - use loopback address:
cluster = Cluster(db_address)
session = cluster.connect('research')

# Prepare statements:
prepared_statements = {}
for table in tables_list:
    prepared_statements[table] = session.prepare('INSERT INTO {}.{} (ts, packet_number, json) VALUES (?,?,?)'
                                                 .format(db_keyspace, table))


def unzip(zip_path: Path):
    zipfile = ZipFile(str(zip_path))
    zipfile.extractall()
    remove(str(zip_path))


def insert_all(json_path):
    with open(str(json_path), 'r') as json_file:
        table_name = json_path.name[json_path.name.find('_')]
        for line in json_file:
            json_entry = loads(line)
            session.execute(prepared_statements[table_name], [json_entry['timestamp'], json_entry['num'], line])
        remove(str(json_path))

if __name__ == "__main__":
    while True:
        for file in listdir(str(db_server_pcaps_folder)):
            if file.endswith('.zip'):
                file_path = db_server_pcaps_folder / file
                unzip(file_path)
                insert_all(file_path.with_suffix('.json'))