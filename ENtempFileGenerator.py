# -*- coding: utf-8 -*-
#import MySQLdb
import cPickle
import sys
import allPaths
import time
import os



#generate the files'path
tts = time.clock()
path = allPaths.ENoriginalDataDir
tempPath = allPaths.ENgeneratedMidFileDir
root = os.listdir(path)
numList = allPaths.ENeach2toNgramfiles
files = []
tempFiles = []
initNum = 2
stdSuffix = '0000'
for Ngram in numList:
	for fileName in xrange(Ngram):
		if fileName<=9:
			files.append(''.join((path,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-1],str(fileName))))
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-1],str(fileName))))		
		elif 99>=fileName>9:
			files.append(''.join((path,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-2],str(fileName))))
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-2],str(fileName))))
		else:
			files.append(''.join((path,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-3],str(fileName))))
			tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-3],str(fileName))))
	initNum += 1

#load the dictionary 

with open('/home/akamalab/Desktop/python_ngram/ENvocabulary.pickle','rb') as f:
	dict = cPickle.load(f)

#starting the mapping process which assigns the specify number for each word through checking the dictionary

numFunc = 0

for i in xrange(sum(numList)):
	ts = time.clock()
	numFunc += 1	
	g = open(tempFiles[i],'wb')
	countline = 1
#Reading the original n-gram file
	with open(files[i],'rb') as f1:
		print "Now processing with the file\n",files[i],"...",
		for record in f1:
			try:		
				tempParse = record.split('\t')
				reNum = tempParse[1]
				tempParse = tempParse[0].split(' ')
				if numFunc <= numList[0]:
					re1 = dict[tempParse[0]]			
					re2 = dict[tempParse[1]]
					tempStr = '\t'.join((str(re1),str(re2),str(reNum)))
				elif (numList[0]+numList[1]) >= numFunc > numList[0]:
					re1 = dict[tempParse[0]]			
					re2 = dict[tempParse[1]]
					re3 = dict[tempParse[2]]
					tempStr = '\t'.join((str(re1),str(re2),str(re3),str(reNum)))
				elif (numList[0]+numList[1]+numList[2]) >= numFunc > (numList[0]+numList[1]):
					re1 = dict[tempParse[0]]			
					re2 = dict[tempParse[1]]
					re3 = dict[tempParse[2]]
					re4 = dict[tempParse[3]]
					tempStr = '\t'.join((str(re1),str(re2),str(re3),str(re4),str(reNum)))
				elif numFunc > (numList[0]+numList[1]+numList[2]):
					re1 = dict[tempParse[0]]			
					re2 = dict[tempParse[1]]
					re3 = dict[tempParse[2]]
					re4 = dict[tempParse[3]]
					re5 = dict[tempParse[4]]
					tempStr = '\t'.join((str(re1),str(re2),str(re3),str(re4),str(re5),str(reNum)))
				
				#result1 = dict[tempParse[0]]			
				#result2 = dict[tempParse[1]]
				#tempStr = str(result1[0])+'\t'+str(result2[0])+'\t'+str(resultNum)
				#tempStr = '\t'.join((str(result1),str(result2),str(resultNum)))
				#if numFunc <= numList[0]:
					#tempStr = funcForParse.2gramParse(record)
				#if (numList[0]+numList[1]) >= numFunc > numList[0]:
					#tempStr = funcForParse.3gramParse(record)
				#if (numList[0]+numList[1]+numList[2]) >= numFunc > (numList[0]+numList[1]):
					#tempStr = funcForParse.4gramParse(record)
			except IndexError as detail:
				print 'Error in row',countline,' in file testfor.txt:',detail			
			except TypeError as detailForTypeError:
				#if result1 == None:
					#result1 = (0,)
				#elif result2 == None:
					#result2 = (0,)
				#tempStr = str(result1[0])+'\t'+str(result2[0])+'\t'+str(resultNum)
				print 'Error in row',countline,' in file testfor.txt:',detailForTypeError		
			g.write(tempStr)
			countline += 1
	g.close()
	te = time.clock()
	print '\n','using',(te-ts),'seconds.\n'
tet = time.clock()
print '\nTotal time is',(tet-tts),'seconds.\n'
#create table for 1gram and input the data directly from the original n-gram file 
#cursor.execute('CREATE TABLE IF NOT EXISTS test2gram(ID int(9) unsigned NOT NULL PRIMARY KEY auto_increment, word1_id mediumint(8) unsigned NOT NULL, word2_id mediumint(8) unsigned NOT NULL, freq bigint(8) unsigned NOT NULL, KEY word1_id (word1_id), KEY word2_id (word2_id), KEY freq (freq), INDEX(word1_id,word2_id))ENGINE = MyISAM partition by hash(ID)')
#cursor.execute('LOCK TABLES test2gram WRITE')
#cursor.execute('ALTER TABLE test2gram DISABLE KEYS')
#cursor.execute('load data local infile %s into table test2gram(word1_id,word2_id,freq)',allPaths.tempDir+'test2gm-0000')
#cursor.execute('ALTER TABLE test2gram ENABLE KEYS')
#cursor.execute('UNLOCK TABLES')



					


