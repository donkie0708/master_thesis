# -*- coding: utf-8 -*-
import MySQLdb
import cPickle
import sys
import allPaths
import os
import operator
import csv
from method import *


print '\nロード中。。。\n'
with open(allPaths.JPvocabPath,'rb+') as f:
	dictJP = cPickle.load(f)
print 'ロード完了！\n'

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

if len(sys.argv)!=3:
	sys.exit('\n','Usage : co-occurCHN.py input_file.csv output_file.csv','\n\n','This python script allows you to use the google n-gram corpus for calculating the co_occurrence between nouns and verbs.','\n','Please be sure that the input CSV file has the following format:','\n','1) List of nouns lies in the 1st column.','\n','2) List of semantic features(only but three different tense of one verb)lies in the 1st row.','\n') 

# The 'headerCSVFileName' is the name of your .csv format file containing the nouns and the semantic feature words which lie in the 1st column and 1st row.

headerCSVFileName= sys.argv[1]

# The 'resultFileCSV' is the file name you want wirte into with the .csv format.

resultFileCSV= sys.argv[2]


temp =csv.reader(open('/home/akamalab/Desktop/csvSample/'+headerCSVFileName,'rb'))

warnFlag = 0
errorWord = []
wholeText = []
nounList = []
single_round = []
rowCount = 1

#Parse the csv file
for row in temp:
        
	wholeText.append(row)
    	nounList.append(row[0])

semanticFeatureList=wholeText[0][1:]	
nounList=nounList[1:]


#check the input words in the dictionary
for word in semanticFeatureList:
	if len(word.split(CSVseparateJP)) <= 1:
		for item in word.split('　'):	
			if item not in dictJP:
				errorWord.append(item)
				warnFlag = 1
	else:
		wordParse = word.split(CSVseparateJP)
		for section in wordParse:
			for item in section.split('　'):
				if item not in dictJP:
					errorWord.append(item)
					warnFlag = 1
			
for word in nounList:
	if len(word.split(CSVseparateJP)) <= 1:	
		for item in word.split('　'):	
			if item not in dictJP:
				errorWord.append(item)
				warnFlag = 1
		
	else:	
		wordParse = word.split(CSVseparateJP)
		for section in wordParse:
			for item in section.split('　'):
				if item not in dictJP:
					errorWord.append(item)
					warnFlag = 1

#Giving a warning message
if warnFlag == 1:
	print '\n\tCSVファイルの中にGoogleコーパスに存在しない語彙があります：\n\t'
	for item in errorWord:
		print '\t[',item,']',
	print '\n'
	answer = raw_input('\t続きますか？（はい：1 或 いいえ：0）\n\t「はい」を選んだら，以上の語彙を含めるあらゆるの行と列の共起率結果はゼロになります。「いいえ」の場合は、ファイルを修正するため強制退出します\n\tお選びください：')
	while(True):	
		if answer == 'はい' or answer in ['1','１']:
			break
		elif answer == 'いいえ' or answer in ['0','０']:
			sys.exit('\n\tご利用ありがとうございます。\n')
		else:
			answer = raw_input('\n\t「はい」か「いいえ」、或はそれに対応する数字を入力してください：')
		
	

for nounWord in nounList:
	
	for semanticFeatureWord in semanticFeatureList:
		
		words_count = 0

        	sNUM = semanticFeatureWord.split(CSVseparateJP)

        	#words_count += len(sNUM.split('　'))
		
		nNUM = nounWord.split(CSVseparateJP)

        	#words_count += len(nNUM.split('　'))

		Nban = []
		Sban = []
		
		print '\n',nounWord,'-----',semanticFeatureWord
		
		try:
			#if len(nNUM) > 1:
			for i in nNUM:
				for wordi in i.split('　'):							
					Nban.append(dictJP[wordi])
			
		
		except KeyError:
			print i,'という単語が存在しないため、所属する一行の結果は全部ゼロとなります！\n'
			single_round = [0]*(len(semanticFeatureList))
			break

		try:
			#if len(sNUM) > 1:
			for j in sNUM:
				for wordj in j.split('　'):					
					Sban.append(dictJP[wordj])		
		
		except KeyError:
			print j,'が存在しないため、共起率はゼロになります！\n'
			single_round.append(0)
			continue
		 				
		co_occurNum = 0.0

		singleNum = 0.0

		single_query = Nban+Sban

		for N in Nban:
			N = [N]
			for S in Sban:

				S = [S]
				
				query1 = N+S

				query2 = S+N

				query3 = N+star+S 

				query4 = S+star+N

				query5 = N+star*2+S

				query6 = S+star*2+N

				query7 = N+star*3+S

				query8 = S+star*3+N

				query9 = N+star*4+S

				query10 = S+star*4+N

				query11 = N+star*5+S

				query12 = S+star*5+N				
				
				query = [query1,query2,query3,query4,query5,query6,query7,query8,query9,query10,query11,query12]
				
				words_count = len(N) + len(S)				
				
				if words_count > 2:
		    			for i in xrange((words_count-2)*2):
		        			del query[11-i]



				for i in query:
					#Flatten the list(remove the bracket "[]" inside the list)			
					#listNew = reduce(lambda x,y:x+y,i)
					length = len(i)
					sql = wildcardSQL(i)
					if sql[0] == 1:
						cursor.execute(sql[1])
						finalResults = cursor.fetchall()
						if len(finalResults) == 0:				
							co_occurNum += 0
						else:		
							for item in finalResults:
								co_occurNum += int(item[length])
		
					elif sql[0] == 0:
						cursor.execute(sql[1])
						finalResults = cursor.fetchall()
						cursor.execute(sql[2])
						finalResults = finalResults + cursor.fetchall()
						for item in finalResults:
							co_occurNum += int(item[length])
				#print 'each co-occur',co_occurNum		

		for j in single_query:
										
			cursor.execute('SELECT freq from 1gram where ID=%s',j)
			finalResults = cursor.fetchall()
			if len(finalResults) == 0:
				singleNum += 0
			else:		
					singleNum += int(finalResults[0][0])
					#print int(finalResults[0][0])
			
		#print 'total co-occur',co_occurNum
		#print 'total single',singleNum
		co_ocurrence_value = co_occurNum / (singleNum-co_occurNum)
		
		single_round.append(co_ocurrence_value)

		print '共起率：',co_ocurrence_value
			
	wholeText[rowCount][1:] = single_round	

	single_round = []

	rowCount+=1				


with open('/home/akamalab/Desktop/csvSample/'+resultFileCSV, 'wb') as f:
    
	writer = csv.writer(f)
   	writer.writerows(wholeText)
