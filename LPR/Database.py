import io
import sqlite3
from sqlite3 import Error

import pandas as pd
from PIL import Image

from paths import *

## Dictionary for status mapping
status_mapping = {
    0: 'Number plate not found',
    1: 'Record exists in DB',
    2: 'Record does not exist in DB'
}


def create_connection(db_file=MASTER_DB_PATH):
    '''
    Create connection with db
    :param db_file: path to db file
    :return: connection object
    '''
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
        pass
    finally:
        if conn:
            print('Connection created successfully')
            return conn


def close_db(conn):
    '''
    Close the connection to db
    :param conn: connection object
    '''
    if conn:
        conn.close()
        print('connection closed successfully')

def insert_data(id, name, contact_no, address):
    '''
    Insert provided data in vehicle_data table
    :param id: vehicle number plate
    :param name: name of the owner
    :param contact_no: contact of the owner
    :param address: address of the owner
    '''
    conn = create_connection()
    insert_query = '''
                    INSERT INTO vehicle_data VALUES(
                    ?,?,?,?);
                    '''
    cursor = conn.cursor()
    cursor.execute(insert_query, (id, name, contact_no, address))
    conn.commit()
    close_db(conn)


def get_details(id):
    '''
    Get details of a vehicle from database
    :param id: number plate of the vehicle
    :return:  dataframe containing details of owner['Vehicle Number', 'Name', 'Contact', 'Address']
    '''
    conn = create_connection()
    get_query = "SELECT vehicle_id,name,contact_no,address FROM vehicle_data WHERE vehicle_id = '" + id + "';"
    cursor = conn.cursor()
    cursor.execute(get_query)
    data = None
    res = cursor.fetchall()
    if len(res) > 0:
        data_lst = res[0]
        data=data_lst
        #data = pd.DataFrame([data_lst], columns=['Vehicle Number', 'Name', 'Contact', 'Address'])
    close_db(conn)
    return data


def insert_history_data(status, image):
    '''
    Inserts details into history_data table
    :param status: status of number plate detectio(0,1,2)
    :param image: image path
    '''
    blob_val = open(TEMP_DIR_PATH + image, 'rb').read()
    conn = create_connection()
    insert_query = '''
                    INSERT INTO history_data (status,photo,timestamp)
                    VALUES(?,?,?);
                    '''
    cursor = conn.cursor()
    cursor.execute(insert_query, (status, blob_val, TIMESTAMP()))
    conn.commit()
    close_db(conn)


def get_history_data():
    '''
    Get data from history table
    :return: data in form of list of dictionaries: [{'Status':'1','Timestamp':'2','Path':'3'},{'Status':'1','Timestamp':'2','Path':'3'}]
    '''
    conn = create_connection()
    get_query = "SELECT vehicle_id,status,photo,timestamp FROM history_data ORDER BY vehicle_id DESC;"
    cursor = conn.cursor()
    cursor.execute(get_query)
    results = cursor.fetchall()
    lst = []
    for res in results:
        id = res[0]
        status = res[1]
        img = res[2]
        timestamp = res[3]
        path = STATIC_TEMP_DIR_PATH + 'db_' + str(id) + '.jpg'
        file_like = io.BytesIO(img)
        img = Image.open(file_like)
        img.save(TEMP_DIR_PATH + 'db_' + str(id) + '.jpg')
        lst.append({
            'Status': status_mapping[int(status)],
            'Timestamp': clean_timestamp(timestamp),
            'Path': path
        })
    conn.close()
    close_db(conn)
    return lst


## Util functions
def create_vehicle_data_table():
    '''
    Create vehicle table
    '''
    conn = create_connection()
    query = '''
            CREATE TABLE vehicle_data ( vehicle_id  TEXT KEY,
             name TEXT NOT NULL,
             contact_no TEXT NOT NULL,
             address TEXT NOT NULL);
            '''
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table Created: vehicle_data ( vehicle_id, name, contact_no, address )")
    close_db(conn)


def create_history_data_table():
    '''
    Create history table
    '''
    conn = create_connection()
    query = '''
                CREATE TABLE history_data ( vehicle_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                  status TEXT NOT NULL,
                  photo BLOB NOT NULL,
                  timestamp TEXT NOT NULL);
                '''
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table Created: history_data ( vehicle_id, status, photo,timestamp )")
    close_db(conn)


def drop_table(table):
    '''
    Drop a table
    :param table: table name
    '''
    conn = create_connection()
    query = 'DROP TABLE ' + table + ';'
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    close_db(conn)


def query_drop_all(table):
    '''
    Drop all records from a table
    :param table: table name
    '''
    conn = create_connection()
    query = 'DELETE  FROM ' + table + ';'
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    close_db(conn)

if __name__ == "__main__":
    # create_history_data_table()
    # drop_table('history_data')
    #print(clean_timestamp('20210523#11:32:04'))
     print(get_history_data())
    # query_drop_all('history_data')
