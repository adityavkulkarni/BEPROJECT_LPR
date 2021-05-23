import sqlite3
from sqlite3 import Error
import io
from paths import  *
from PIL import Image
import  pandas as pd

#conn = None

status_mapping ={
    0: 'Number plate not found',
    1: 'Record exists in DB',
    2: 'Record does not exist in DB'
}

def create_connection(db_file=MASTER_DB_PATH):
    """ create a database connection to a SQLite database """
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
    if conn:
        conn.close()
        print('connection closed successfully')

def create_vehicle_data_table():
    '''Creates Vehicle Table'''
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
    '''Create History Table'''
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
    '''Drop Table'''
    conn = create_connection()
    query = 'DROP TABLE '+table+';'
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    close_db(conn)

def insert_data(id,name,contact_no,address):
    '''Insert Data into vehicle_data'''
    conn = create_connection()
    insert_query = '''
                    INSERT INTO vehicle_data VALUES(
                    ?,?,?,?);
                    '''
    cursor = conn.cursor()
    cursor.execute(insert_query,(id,name,contact_no,address))
    conn.commit()
    close_db(conn)

def get_details(id):
    '''Get Data from vehicle_data'''
    conn = create_connection()
    get_query = "SELECT vehicle_id,name,contact_no,address FROM vehicle_data WHERE vehicle_id = '"+id+"';"
    cursor = conn.cursor()
    cursor.execute(get_query)
    data = None
    res = cursor.fetchall()
    if len(res) > 0:
        data_lst = res[0]
        data = pd.DataFrame([data_lst],columns=['Vehicle Number','Name','Contact','Address'])
    close_db(conn)
    return data

def insert_history_data(status,image):
    '''Insert Data into history_data'''
    # loaded image from temp dir
    #image = Image.open(TEMP_DIR_PATH+'detected.png')
    blob_val = open(TEMP_DIR_PATH+image,'rb').read()
    # db.create_connection(paths.MASTER_DB_PATH)
    # deleting unknown vehicle from temp dir after storing to db
    # image.close()
    conn = create_connection()
    insert_query = '''
                    INSERT INTO history_data (status,photo,timestamp)
                    VALUES(?,?,?);
                    '''
    cursor = conn.cursor()
    cursor.execute(insert_query,(status,blob_val,TIMESTAMP()))
    conn.commit()
    close_db(conn)

def clean(timestamp):
    datem = datetime.datetime.strptime(timestamp, "%Y%m%d#%H:%M:%S")
    return  "Date: " + str(datem.day ) + " " + str(datem.strftime("%B")) + " " + str(datem.year) + \
            "  Time: "+ str(datem.hour)+":"+ str(datem.minute)+":"+ str(datem.second)


def get_history_data():
    '''Get Data from history_data'''
    conn = create_connection()
    get_query = "SELECT vehicle_id,status,photo,timestamp FROM history_data;"
    cursor = conn.cursor()
    cursor.execute(get_query)
    results = cursor.fetchall()
    lst = []
    for res in results:
        id = res[0]
        status = res[1]
        img = res[2]
        timestamp = res[3]
        path = STATIC_TEMP_DIR_PATH+'db_'+str(id)+'.jpg'
        file_like = io.BytesIO(img)
        img = Image.open(file_like)
        img.save(TEMP_DIR_PATH+'db_'+str(id)+'.jpg')
        lst.append({
            'Status': status_mapping[int(status)],
            'Timestamp':clean(timestamp),
            'Path':path
        })
    conn.close()
    close_db(conn)
    return lst

def query_drop_all(table):
    conn = create_connection()
    query = 'DELETE  FROM '+table+';'
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    close_db(conn)

def query_all():
    conn = create_connection()
    query = '''
            SELECT * FROM vehicle_data;
            '''
    cur = conn.cursor()
    cur.execute(query)
    if len(cur.fetchall())>0:
        print(cur.fetchall()[0])
    close_db(conn)



if __name__=="__main__":

    #create_history_data_table()
    #drop_table('history_data')
    print(clean('20210523#11:32:04'))
    #print(get_details('HR26DK8337'))
    #query_drop_all('history_data')
