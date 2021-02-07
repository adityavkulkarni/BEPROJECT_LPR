

'''
def get_from_db(inp):
    db = MySQLdb.connect('localhost', 'lpr', 'lpr', 'demo')
    cursor = db.cursor()

    if (cursor.execute("select * from detail where lp =  '{}' ".format(inp))):
        a = cursor.fetchone()
        return True, ('Data Found ! Vehicle belongs to the premises.'+'<br>Details : <br>Owner Name : {} <br> Vehicle no: {}'.format(a[1], a[0]))
    else:
        return False, ('Data not found in database.<br> <p style="color:  red  ;">!!!!#### Vehicle does not belongs to the premises ####!!!! <br>Fetched Record from RTO </p>  ')
'''