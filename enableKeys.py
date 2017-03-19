# -*- coding: utf-8 -*-
import MySQLdb
import cPickle
import sys
import allPaths
import time
import os


tts = time.ctime()


#connect to the database
try:
	db = MySQLdb.connect(
		host = 'localhost',
		user = 'root',
		passwd = 'fmri',
		db = 'jp_ngram',
		charset='utf8',
		local_infile = 1
		)
except Exception as e:
	sys.exit('Could not be able to get into the database!')

cursor = db.cursor()
tempPath = allPaths.generatedMidFileDir
numList = allPaths.each2toNgramfiles
files = []
tempFiles = []
initNum = 2
stdSuffix = '0000'
#For command 'executemany()' using
ngramdata=[2,3,4,5,6,7]

#create the paths for inserting the corresponding files
for Ngram in numList:
	for fileName in xrange(Ngram):
		if fileName>9:
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-2],str(fileName))))
		else:
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-1],str(fileName))))
	initNum += 1


#enable index for each table
for i in tempFiles[1:numList[0]]:		
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts	
	sqlEnablekeys ='ALTER TABLE 2gram_%s DISABLE KEYS'%i[-4:]
	cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te	
	

for i in tempFiles[numList[0]+1:(numList[0]+numList[1])]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts		
	sqlEnablekeys ='ALTER TABLE 3gram_%s DISABLE KEYS'%i[-4:]
	cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te		
	

for i in tempFiles[(numList[0]+numList[1]+1):(numList[0]+numList[1]+numList[2])]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts	
	sqlEnablekeys ='ALTER TABLE 4gram_%s DISABLE KEYS'%i[-4:]
	cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te	
				
	
for i in tempFiles[(numList[0]+numList[1]+numList[2]+1):(numList[0]+numList[1]+numList[2]+numList[3])]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts		
	sqlEnablekeys ='ALTER TABLE 5gram_%s DISABLE KEYS'%i[-4:]
	cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te			

	
for i in tempFiles[(numList[0]+numList[1]+numList[2]+numList[3]+1):(numList[0]+numList[1]+numList[2]+numList[3]+numList[4])]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts			
	sqlEnablekeys ='ALTER TABLE 6gram_%s DISABLE KEYS'%i[-4:]
	cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te	


for i in tempFiles[(numList[0]+numList[1]+numList[2]+numList[3]+numList[4])+1:]:
	print '\nNow processing with the file\n',i,'\n'	
	ts = time.ctime()
	print '\nStarting at',ts		
	sqlEnablekeys ='ALTER TABLE 7gram_%s DISABLE KEYS'%i[-4:]
	cursor.execute(sqlEnablekeys)		
	te = time.ctime()
	print '\nFinished at',te	
				

tte = time.ctime()
print 'Started at',tte,'\nFinished at',tts,'\n'
