import MySQLdb
import cPickle
import sys
import allPaths
# -*- coding: utf-8 -*-

#connect to the database
try:
	db = MySQLdb.connect(
		host = 'localhost',
		user = 'root',
		passwd = 'fmri',
		db = 'en_ngram',
		charset='utf8',
		local_infile = 1
		)
except Exception as e:
	sys.exit('Could not be able to get into the database!')

#create table for 1gram and input the data directly from the original n-gram file 
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS 1gram(ID mediumint(8) unsigned NOT NULL PRIMARY KEY auto_increment, word varchar(255) character set utf8 collate utf8_general_ci NOT NULL, freq bigint(8) unsigned NOT NULL, KEY word (word), KEY freq (freq))ENGINE = MyISAM partition by KEY()')
cursor.execute('LOCK TABLES 1gram WRITE')
cursor.execute('ALTER TABLE 1gram DISABLE KEYS')

#prepare for 1gram dictionary data structure
dictForUnigram = {}
tempList = []
tempListForDict = []
ID = 1


#make the dictionary and insert 1gram data into table
with open('/home/akamalab/Desktop/vocab','rb') as f:
	for line in f:
		tempParse=line.split('\t')
		tempListForDict.append((tempParse[0],ID))
		tempList.append((tempParse[0],tempParse[1])) 
		ID+=1
dictForUnigram = dict(tempListForDict)

#generate the pickle data structure
with open(allPaths.ENvocabPath,'wb') as output:
	cPickle.dump(dictForUnigram, output)

#insert data						 
cursor.executemany('INSERT INTO 1gram (word,freq) VALUES (%s,%s)',tempList)
cursor.execute('ALTER TABLE 1gram ENABLE KEYS')
cursor.execute('UNLOCK TABLES')
