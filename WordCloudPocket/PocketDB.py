"""
the first you have to do is create a connection to pocket to use the api, here some webs that helped a lot:
(webs que me ayudaron a configurar el API)

https://getpocket.com/developer/docs/authentication
http://www.jamesfmackenzie.com/getting-started-with-the-pocket-developer-api/
https://www.everydayplots.com/reading-habit-analysis-pocket-api-python/
https://gist.github.com/alexpyoung/7e241a8f3f805630f0f66a1cf0763675

"""

import sqlite3
import requests
import json
from datetime import datetime
import ssl #no lo necesita un jupiter notebook



# Ignore SSL certificate errors  #no lo necesita un notebook
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#conexion a una base de datos y el cursor para ejecutar queryes
conn = sqlite3.connect('pocketbd.sqlite')
cur = conn.cursor()

def gather_data(since=None):
    baseurl = "https://getpocket.com/v3/get"
    parameters = {}
    parameters['consumer_key'] = "93250-ffc1c3229d62d2ea578b1786"
    parameters['access_token'] = "187fbba6-4fce-6dcf-b1a6-e6bfdd"
    parameters['state'] = "all" 
    parameters['detailType'] = "simple"
    parameters['count'] = 20 #you can delete this line if you want all your data at once (not just 20 items)
    parameters['sort'] = "oldest" 
    if since is None:
        pass
    else:
        parameters['since'] = since

    response = requests.post(baseurl,parameters)
    return response

#checking the last time we retrieve data from pocket to avoid unnecesary data
try:
    with open('file.txt','r') as f:
        content = f.read()
        lista = content.split()
        last_retrieve = lista[-1]
    data = gather_data(last_retrieve).json()
    #despues de encontrar el since debemos añadirlo al historial: Adding the since value to history:
    with open('file.txt','a') as history: #a mode adds (append to the file)
        history.write('{} '.format(data['since']))

except:
    print('no file.txt')
    data = gather_data().json()    
    with open('file.txt','a') as history: #a mode adds (append to the file)
        history.write('{} '.format(data['since']))


cur.execute('''CREATE TABLE IF NOT EXISTS ITEMS
                 (ID INTEGER PRIMERY KEY UNIQUE,
                  ITEM_ID VARCHAR,
                  URL VARCHAR,
                  TITLE VARCHAR,
                  ADDED DATETIME,
                  LANGUAGE VARCHAR,
                  WORD_COUNT)''')

conn.commit()

start = None
cur.execute("SELECT MAX(ID) FROM ITEMS")


try:
    row = cur.fetchone() #devuelve tupla
    if row[0] is None:
        start = 0 #it needs to start in 0 because is in the for loop that we increment it.
    else:
        start = (row[0])
except:
    print("hubo un error")
    start = 1


for key in data['list']:
    #sometimes an extra item without data appear in my data, this item does not have the attributes so I have to skip it. 
    if len(data['list'][key].keys()) < 6:
        pass

    else:
        start = start +1 #I uptaded the start value even when the data was bad so it must stay here, just if the data is ok
        
        i_time = datetime.fromtimestamp(int(data['list'][key]['time_added']))
        date = str(i_time)[:10]
    
        item_id = key
        
        URL = data['list'][key]['given_url']
        
        if data['list'][key]['given_title'] == '':
            TITLE = data['list'][key]['excerpt'][:100]
        else:
            TITLE = data['list'][key]['given_title']

        word_count = data['list'][key]['word_count']
       
        if data['list'][key]['lang'] == '':
            LANG = 'en'
        else:
            LANG = data['list'][key]['lang']
  

        cur.execute('''INSERT INTO ITEMS
                        VALUES ( ?, ?, ?, ?, ?, ?, ?)''',( start, item_id, URL, TITLE, date, LANG, word_count))

conn.commit()
cur.close()
print('BD is closed')