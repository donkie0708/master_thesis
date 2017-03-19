# -*- coding: utf-8 -*-
import MySQLdb
import cPickle
import sys
import allPaths
import time
import os


tts = time.ctime()

timelog = open(allPaths.ENgeneratedMidFileDir+'/logfile/timeLogForInserting.txt','wb+')
timelog.write('This is log file for recording the time during the inserting session.\n\n\nUsing the tableTest.py script for test\n\n')

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

cursor = db.cursor()
tempPath = allPaths.ENgeneratedMidFileDir
numList = allPaths.ENeach2toNgramfiles
files = []
tempFiles = []
initNum = 2
stdSuffix = '0000'
#For command 'executemany()' using
#ngramdata=[2,3,4,5]

#create the paths for inserting the corresponding files
for Ngram in numList:
	for fileName in xrange(Ngram):
		if fileName<=9:
			#files.append(''.join((path,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-1],str(fileName))))
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-1],str(fileName))))
		elif 99>=fileName>9:
			#files.append(''.join((path,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-2],str(fileName))))
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-2],str(fileName))))
		else:
			#files.append(''.join((path,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-3],str(fileName))))
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-3],str(fileName))))				
		
	initNum += 1

print '\nNow initialing standard table for each n-gram.\n'
print 'Processing 2gram_0000...'
cursor.execute('CREATE TABLE IF NOT EXISTS 2gram_0000(ID int(9) unsigned NOT NULL PRIMARY KEY auto_increment, word1_id mediumint(8) unsigned NOT NULL, word2_id mediumint(8) unsigned NOT NULL, freq bigint(8) unsigned NOT NULL, KEY word1_id (word1_id), KEY word2_id (word2_id), KEY freq (freq))ENGINE = MyISAM partition by KEY() partitions 3')
cursor.execute('ALTER TABLE 2gram_0000 DISABLE KEYS')
cursor.execute('load data local infile "/media/HD-LXU3/GoogleN-GramCorpus/web1t_CHN/tempForCHN/2gms/2gm-0000" into table 2gram_0000(word1_id,word2_id,freq)')
#cursor.execute('ALTER TABLE 2gram_0000 ENABLE KEYS')
print '\n2gram-0000 is done!\n'

print 'Processing 3gram_0000...'
cursor.execute('CREATE TABLE IF NOT EXISTS 3gram_0000(ID int(9) unsigned NOT NULL PRIMARY KEY auto_increment, word1_id mediumint(8) unsigned NOT NULL, word2_id mediumint(8) unsigned NOT NULL, word3_id mediumint(8) unsigned NOT NULL, freq bigint(8) unsigned NOT NULL, KEY word1_id (word1_id), KEY word2_id (word2_id), KEY word3_id (word3_id), KEY freq (freq))ENGINE = MyISAM partition by KEY() partitions 3')
cursor.execute('ALTER TABLE 3gram_0000 DISABLE KEYS')
cursor.execute('load data local infile "/media/HD-LXU3/GoogleN-GramCorpus/web1t_CHN/tempForCHN/3gms/3gm-0000" into table 3gram_0000(word1_id,word2_id,word3_id,freq)')
#cursor.execute('ALTER TABLE 3gram_0000 ENABLE KEYS')
print '\n3gram-0000 is done!\n'

print 'Processing 4gram_0000...'
cursor.execute('CREATE TABLE IF NOT EXISTS 4gram_0000(ID int(9) unsigned NOT NULL PRIMARY KEY auto_increment, word1_id mediumint(8) unsigned NOT NULL, word2_id mediumint(8) unsigned NOT NULL, word3_id mediumint(8) unsigned NOT NULL, word4_id mediumint(8) unsigned NOT NULL, freq bigint(8) unsigned NOT NULL, KEY word1_id (word1_id), KEY word2_id (word2_id), KEY word3_id (word3_id), KEY word4_id (word4_id), KEY freq (freq))ENGINE = MyISAM partition by KEY() partitions 3')
cursor.execute('ALTER TABLE 4gram_0000 DISABLE KEYS')
cursor.execute('load data local infile "/media/HD-LXU3/GoogleN-GramCorpus/web1t_CHN/tempForCHN/4gms/4gm-0000" into table 4gram_0000(word1_id,word2_id,word3_id,word4_id,freq)')
#cursor.execute('ALTER TABLE 4gram_0000 ENABLE KEYS')
print '\n4gram-0000 is done!\n'

print 'Processing 5gram_0000...'
cursor.execute('CREATE TABLE IF NOT EXISTS 5gram_0000(ID int(9) unsigned NOT NULL PRIMARY KEY auto_increment, word1_id mediumint(8) unsigned NOT NULL, word2_id mediumint(8) unsigned NOT NULL, word3_id mediumint(8) unsigned NOT NULL, word4_id mediumint(8) unsigned NOT NULL, word5_id mediumint(8) unsigned NOT NULL, freq bigint(8) unsigned NOT NULL, KEY word1_id (word1_id), KEY word2_id (word2_id), KEY word3_id (word3_id), KEY word4_id (word4_id), KEY word5_id (word5_id), KEY freq (freq))ENGINE = MyISAM partition by KEY() partitions 3')
cursor.execute('ALTER TABLE 5gram_0000 DISABLE KEYS')
cursor.execute('load data local infile "/media/HD-LXU3/GoogleN-GramCorpus/web1t_CHN/tempForCHN/5gms/5gm-0000" into table 5gram_0000(word1_id,word2_id,word3_id,word4_id,word5_id,freq)')
#cursor.execute('ALTER TABLE 5gram_0000 ENABLE KEYS')
print '\n5gram-0000 is done!\n'


#create tables for each n-gram
for i in tempFiles[1:numList[0]]:		
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts	
	sqlCreate ='CREATE TABLE 2gram_%s like 2gram_0000'%i[-4:]
	sqlDisablekeys ='ALTER TABLE 2gram_%s DISABLE KEYS'%i[-4:]
	#sqlEnablekeys ='ALTER TABLE 2gram_%s ENABLE KEYS'%i[-4:]
	sqlLoadData ="load data local infile '%s' into table 2gram_%s(word1_id,word2_id,freq)"%(i,i[-4:])		
	cursor.execute(sqlCreate)				
	cursor.execute(sqlDisablekeys)
	cursor.execute(sqlLoadData)
	#cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te	
	

for i in tempFiles[numList[0]+1:(numList[0]+numList[1])]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts		
	sqlCreate ='CREATE TABLE 3gram_%s like 3gram_0000'%i[-4:]
	sqlDisablekeys ='ALTER TABLE 3gram_%s DISABLE KEYS'%i[-4:]
	#sqlEnablekeys ='ALTER TABLE 3gram_%s ENABLE KEYS'%i[-4:]
	sqlLoadData ="load data local infile '%s' into table 3gram_%s(word1_id,word2_id,word3_id,freq)"%(i,i[-4:])		
	cursor.execute(sqlCreate)				
	cursor.execute(sqlDisablekeys)
	cursor.execute(sqlLoadData)
	#cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te		
	

for i in tempFiles[(numList[0]+numList[1]+1):(numList[0]+numList[1]+numList[2])]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts	
	sqlCreate ='CREATE TABLE 4gram_%s like 4gram_0000'%i[-4:]
	sqlDisablekeys ='ALTER TABLE 4gram_%s DISABLE KEYS'%i[-4:]
	#sqlEnablekeys ='ALTER TABLE 4gram_%s ENABLE KEYS'%i[-4:]
	sqlLoadData ="load data local infile '%s' into table 4gram_%s(word1_id,word2_id,word3_id,word4_id,freq)"%(i,i[-4:])		
	cursor.execute(sqlCreate)				
	cursor.execute(sqlDisablekeys)
	cursor.execute(sqlLoadData)
	#cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te	
				
	
for i in tempFiles[numList[0]+numList[1]+numList[2]+1:]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts		
	sqlCreate ='CREATE TABLE 5gram_%s like 5gram_0000'%i[-4:]
	sqlDisablekeys ='ALTER TABLE 5gram_%s DISABLE KEYS'%i[-4:]
	#sqlEnablekeys ='ALTER TABLE 5gram_%s ENABLE KEYS'%i[-4:]
	sqlLoadData ="load data local infile '%s' into table 5gram_%s(word1_id,word2_id,word3_id,word4_id,word5_id,freq)"%(i,i[-4:])		
	cursor.execute(sqlCreate)				
	cursor.execute(sqlDisablekeys)
	cursor.execute(sqlLoadData)
	#cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te			
				

tte = time.ctime()
print 'Started at',tts,'\nFinished at',tte,'\n'
print 'Successfully finished！\nPCをシャットダウンしても、構いません。'
timelog.writelines('\nProcess started at:')
timelog.writelines(tts)
timelog.writelines('And ended at:')
timelog.writelines(tte)
