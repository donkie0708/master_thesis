# -*- coding: utf-8 -*-
import MySQLdb
import cPickle
import sys
import allPaths
import time
import os
#import chooseQuery
import operator
# readline可以解决raw_input中对于unicode的退格键（backspace）的不识别问题
import readline
from ENmethod import *


tts = time.ctime()

print '\nLoading....\n'
with open(allPaths.ENvocabPath,'rb+') as f:
	dictCHN = cPickle.load(f)
with open(allPaths.ENvocabReversePath,'rb+') as f:
	reverseDictCHN = cPickle.load(f)
print 'Successfully Completed!\n'

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
print ("""\n\t<Google 1T 5-gram corpus query system version 1.0>\n\tMode 1：N-gram query	Mode 2：Co-occurrence query""")
mode = raw_input('\n\tPlease choose 1 Or 2:')

# N-gram频率查询模式
flag = 1
while(flag):
	if mode == '1':
		flag = 0
		while(True):
			try:
				queryWord = raw_input("""\n\tComplete the query by inputting words(5 words at most)\n\t1.Use the asterisk mark "*" as the wild card\n\t2.Quit the system: press <Ctrl> + <D> \n\n\n\t""")
				#deal with the invaild input
				legalQuery = invalidCheck(queryWord)

				#check the word in dictionary,if there's no such word,change another and try again.
				query = legalQuery.split()
				length  = len(query)
				order = 0
				for word in query:
					flag = 1
					time = 0
					while(flag):
						if (word in dictCHN) or (word == '*'):
							flag = 0
							query[order] = word
							order += 1
						else:
							if time < 3:
								word = raw_input('\n\tThere is no such “%s” word in corpus, please input a new one: \n\t'%word)
								time += 1
								wordNew = word.split(' ')
								word = wordNew[0]
								if len(wordNew) > 1:
									flag1 = 1
									while(flag1):
										word = raw_input('\n\tInput one single word please!:\n\t')
										wordNew1 = word.split(' ')
										if len(wordNew1) == 1:
											flag1 = 0
										word = wordNew1[0]
					
							else:
								word = raw_input("\n\tWhat's wrong with you! A normal word please!:\n\t")
								time += 1
								wordNew = word.split(' ')
								word = wordNew[0]
								if len(wordNew) > 1:
									while(wordNew1 > 1):
										word = raw_input('\n\tInput one single word please!:\n\t')
										wordNew1 = word.split(' ')
										if len(wordNew1) == 1:
											flag1 = 0
										word = wordNew1[0]
	
				finalSQL = []
				# In single word case, execute query directly.
				if len(query) == 1:
					cursor.execute('SELECT word,freq from 1gram where word=%s',query[0])
					result = cursor.fetchone()
					print '\n\t',
					for item in result:
						print item,
					print '\n'
				
				# convert each word to the index number within the database
				else:		
					for item in query:
						if item != '*':			
							#cursor.execute('SELECT ID from 1gram where word=%s',item)
							#result = cursor.fetchone()			
							#finalSQL.append(result[0])
							finalSQL.append(dictCHN[item])
						else:
							finalSQL.append('*')
			
				# execute the query for the multiple words case
				#if len(query) > 1:
					sql = wildcardSQL(finalSQL)
					if sql[0] == 1:
						print '\n\n\tSearching...\n\n\t'
						cursor.execute(sql[1]+' LIMIT 100')
						finalResults = cursor.fetchall()
						if len(finalResults) == 0:
							print "\n\tSorry! We haven't found any corresponding record in the corpus.\n\t"
						else:		
							for item in finalResults:
								print '\t',
								print item[length],'\t',
								for i in xrange(length):
									print reverseDictCHN[item[i]],
								print '\n'
							print '\n'
	
					#Output for the n-gram lying between files
					elif sql[0] == 0:
						print '\n\n\tSearching...\n\n\t'
						cursor.execute(sql[1]+' LIMIT 50')
						finalResults = cursor.fetchall()
						cursor.execute(sql[2]+' LIMIT 50')
						finalResults = finalResults + cursor.fetchall()
						finalResults = sorted(finalResults, key=operator.itemgetter(length),reverse=True)
						for item in finalResults:
							print '\t',
							print item[length],'\t',			
							for i in xrange(length):
								print reverseDictCHN[item[i]],
							print '\n'
						print '\n'

			except EOFError:
				sys.exit('\n\tNo zuo no die!\n\t')

	#共起率计算模式
	elif mode == '2':
		flag = 0
		while(True):		
			try:
				queryWord = raw_input("""\n\tComplete the query by inputting two "concept" separated by <tab>, one concept could be any ngram.\n\t**Warning**: Total number of ngram should be less than 5.\n\tInvalid query: one two three	four five six   <------- more than 5 grams(6 grams input)\n\tQuit the system: press <Ctrl> + <D> \n\n\n\t""")
				errorFlag = 1
				mainFlag = 1
				#输入合法性判断
				while(mainFlag):
					if errorFlag == 0:
						queryWord = raw_input('\n\tPlease input again:\n\t')
					errorFlag = 1
					legalQuery = co_occurInvalidCheck(queryWord)
					queryOrigi = legalQuery.split('	')
					first = queryOrigi[0].split(' ')
					second = queryOrigi[1].split(' ')
					allword = first+second
					errorWord = []
					order = 1
					#各个单词或字儿的合法性判别（在语料库中存在与否）
					for word in allword:
						if word not in dictCHN:
							errorWord.append(word)
							errorFlag = 0
						elif errorFlag and order == len(allword):
							mainFlag = 0
						order += 1
					if errorFlag == 0:			
						print "\n\tCan't find these words in the corpus:\n\t"
						for item in errorWord:
							print '\t"',item,'"',
						print '\n'
				
				#计算共起率
				words_count = 0
        			words_count += len(first)
        			words_count += len(second)

				N = []
				S = []
		
				print '\n',first,'-----',second
		
				if len(first) > 1:
					for i in first:
						N.append(dictCHN[i])
				else:					
					N.append(dictCHN[first[0]])
		

				if len(second) > 1:
					for i in second:
						S.append(dictCHN[i])
				else:					
					S.append(dictCHN[second[0]])
				
				single_query = [N,S]

				query1 = [N,S]

				query2 = [S,N]

				query3 = [N,['*'],S] 

				query4 = [S,['*'],N]

				query5 = [N,['*','*'],S]

				query6 = [S,['*','*'],N]

				query7 = [N,['*','*','*'],S]

				query8 = [S,['*','*','*'],N]

				query = [query1,query2,query3,query4,query5,query6,query7,query8]
				
				if words_count > 2:
		    			for i in xrange((words_count-2)*2):
		        			del query[7-i]

				eachCo_occurNum = 0
								
				co_occurNum = 0.0

				singleNum = 0.0	

				ngram = words_count
				
				timing = 2

				for i in query:
					#Flatten the list(remove the bracket "[]" inside the list)			
					listNew = reduce(lambda x,y:x+y,i)
					length = len(listNew)
					sql = wildcardSQL(listNew)
					if timing%2 ==0:					
						print ('\n\t%dgram positive order:\n')%ngram
					else:
						print ('\n\t%dgram reverse order:\n')%ngram				
				
					if sql[0] == 1:
						#print '\n\n\t正在查找。。。\n\n\t'
						cursor.execute(sql[1])
						finalResults = cursor.fetchall()
						#print '这是结果',finalResults
						if len(finalResults) == 0:
							#print '多元共起+0前',co_occurNum					
							co_occurNum += 0
							#print '多元共起+0后',co_occurNum
							print '\tFound nothing！\n'
						else:		
							for item in finalResults:
								eachCo_occurNum += int(item[length])
								co_occurNum += int(item[length])
								print '\t',
								print item[length],'\t',
								for i in xrange(length):
									print reverseDictCHN[item[i]],
								print '\n'
							#print '\n'
							
		
					elif sql[0] == 0:
						#print '\n\n\t正在查找。。。\n\n\t'
						cursor.execute(sql[1])
						finalResults = cursor.fetchall()
						cursor.execute(sql[2])
						finalResults = finalResults + cursor.fetchall()
						finalResults = sorted(finalResults, key=operator.itemgetter(length),reverse=True)
						for item in finalResults:
							eachCo_occurNum += int(item[length])
							co_occurNum += int(item[length])
							print '\t',
							print item[length],'\t',			
							for i in xrange(length):
								print reverseDictCHN[item[i]],
							print '\n'
						#print '\n'
					if timing%2 ==1:					
						print ('\n\tTotal number in the %dgram:')%ngram,eachCo_occurNum
						eachCo_occurNum = 0
						ngram += 1
					
					timing += 1
		

				singleGram = 0
				for j in single_query:
					print '\n\t "',queryOrigi[singleGram],'" in Unigram:\n\t'					 	
					length = len(j)
					#print '单个长度为',length
					if length > 1:
						sql = wildcardSQL(j)
						#print j
						cursor.execute(sql[1])
						finalResults = cursor.fetchall()
						#print '单个结果',finalResults
						if len(finalResults) == 0:
							#print '单元共起+0前',singleNum					
							singleNum += 0
							#print '单元共起+0后',singleNum
							print '\tThe result is 0'
						else:		
							for item in finalResults:
								singleNum += int(item[length])
								#print '单元共起目前为',singleNum
								print '\tResult:',int(item[length])
					else:
						#print '这是一个字儿的情况'
						#print j				
						cursor.execute('SELECT freq from 1gram where ID=%s',j[0])
						finalResults = cursor.fetchall()
						#print '单个结果',finalResults
						if len(finalResults) == 0:
							singleNum += 0
							print '\tThe result is 0'
						else:		
							singleNum += int(finalResults[0][0])
							#print '单元共起目前为',singleNum
							print '\tResult:',int(singleNum)
					singleGram += 1

				co_ocurrence_value = co_occurNum / (singleNum-co_occurNum)
		
				print '\n\tCo-occurrence:',co_ocurrence_value
			
			except EOFError:
					sys.exit('\n\tNo zuo no die\n\t')

	else:
		mode = raw_input('\n\tPlease input 1 or 2:')
