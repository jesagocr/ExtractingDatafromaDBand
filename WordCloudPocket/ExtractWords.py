#Extracts words from the DB and creates a js file with the necesarry data to create a word cloud (with the help of d3.layout.cloud and d3.v2)

import sqlite3
import urllib.parse # to show tilde in the spanish words 

conn = sqlite3.connect("pocketbd.sqlite")
cur = conn.cursor()

cur.execute("SELECT ID, TITLE FROM ITEMS")

titles = {}

for id in cur:
    titles[id[0]] = id[1]

#I save the words and its count in another dict
counts = {}

stop_words = ['','-','|','/','—','–','&','and','with','of','the','for','para',"'",'a','de','to','en','un','y','in','el','con','la','las','by','i','no','del','is','you','your']

for key in titles.keys():
    words = titles[key].lower()
    words = words.split()

    for word in words:
        if word not in stop_words:
            if word not in counts:
                counts[word] = 0  
            counts[word] = counts[word] + 1 

#Teacher ideas:
ordenado = sorted(counts, key=lambda x: counts[x], reverse=True)

highest = None
lowest = None

for k in ordenado[:50]:
    if highest is None or highest < counts[k] :
        highest = counts[k]
    if lowest is None or lowest > counts[k] :
        lowest = counts[k]
print('Range of counts:',highest,lowest)

# Spread the font sizes across 20-100 based on the count
bigsize = 80
smallsize = 20

fhand = open('jwords.js','w',encoding='utf8')  #cuando creo el archivo le tengo que crear el formato, sino las words no se ven bien
fhand.write("jwords = [")
first = True
for k in ordenado[:50]:
    if not first : fhand.write( ",\n")
    first = False
    size = counts[k]
    size = (size - lowest) / float(highest - lowest)
    size = int((size * bigsize) + smallsize)
    fhand.write("{text: '"+str(k)+"', size: "+str(size)+"}")
fhand.write( "\n];\n")
fhand.close()

conn.commit()
cur.close()