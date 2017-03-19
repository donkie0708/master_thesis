# -*- coding: utf-8 -*-
import MySQLdb
import cPickle
import sys
import allPaths
import os
import operator
# readlineモジュールはraw_input()でunicodeの文字に対するbackspace鍵の認識できない問題を解決する
import readline
from method import *


print '\nロード中。。。\n'
with open(allPaths.JPvocabPath,'rb+') as f:
	dictJP = cPickle.load(f)
with open(allPaths.JPvocabReversePath,'rb+') as f:
	reverseDictJP = cPickle.load(f)
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
print ("""\n\t<Google日本語７グラム検索システム version 1.0>\n\tモード1：N-gram頻度検索	モード2：共起率検索""")
mode = raw_input('\n\tモードを選び 1或2を入力：')

# N-gram頻度検索モード
flag = 1
while(flag):
	if mode == '１' or mode == '1':
		flag = 0
		while(True):
			try:
				queryWord = raw_input("""\n\t日本語Nグラム単語を入力してください（空白で間隔、最長７グラム）\n\t1.任意の単語は「＊」(shift+8)を使いください（現在は首位＊はまだ対応になっていません）\n\t2.<Ctrl> と <D>を同時に押すと終了する \n\n\n\t""")
				#deal with the invaild input
				legalQuery = invalidCheck(queryWord)

				#check the word in dictionary,if there's no such word,change another and try again.
				query = legalQuery.split('　')
				length  = len(query)
				order = 0
				for word in query:
					flag = 1
					time = 0
					while(flag):
						if (word in dictJP) or (word in asterisk):
							flag = 0
							query[order] = word
							order += 1
						else:
							if time < 3:
								word = raw_input('\n\t「%s」と言う単語は、Googleデータにはありません、「%s」を別の単語に書き換えてください： \n\t'%(word,word))
								time += 1
								wordNew = word.split('　')
								word = wordNew[0]
								if len(wordNew) > 1:
									flag1 = 1
									while(flag1):
										word = raw_input('\n\t空白を入れず一つの単語を入力してください： \n\t')
										wordNew1 = word.split('　')
										if len(wordNew1) == 1:
											flag1 = 0
										word = wordNew1[0]
					
							else:
								word = raw_input('\n\t文法上独立の単位を入力してください、例えば「わたしは」を、「私」と「は」を分けて入力すれば、コーパスから見つけられます\n\t')
								time += 1
								wordNew = word.split('　')
								word = wordNew[0]
								if len(wordNew) > 1:
									while(wordNew1 > 1):
										word = raw_input('\n\t空白を入れず一つの単語を入力してください： \n\t')
										wordNew1 = word.split('　')
										if len(wordNew1) == 1:
											flag1 = 0
										word = wordNew1[0]
	
				finalSQL = []
				if len(query) == 1:
					cursor.execute('SELECT word,freq from 1gram where word=%s',query[0])
					result = cursor.fetchone()
					print '\n\t',
					for item in result:
						print item,
					print '\n'
		
				else:		
					for item in query:
						if item not in asterisk:			
							cursor.execute('SELECT ID from 1gram where word=%s',item)
							result = cursor.fetchone()			
							finalSQL.append(result[0])
						else:
							finalSQL.append('＊')
			

				if len(query) > 1:
					sql = wildcardSQL(finalSQL)
					if sql[0] == 1:
						print '\n\n\t検索中。。。\n\n\t'
						cursor.execute(sql[1]+' LIMIT 15')
						finalResults = cursor.fetchall()
						if len(finalResults) == 0:
							print '\n\tすみません、入力したN-gramはGoogleデータにはありません！\n\t'
						else:		
							for item in finalResults:
								print '\t',
								print item[length],'\t',
								for i in xrange(length):
									print reverseDictJP[item[i]],
								print '\n'
							print '\n'
	
					#Output for the n-gram lying between files
					elif sql[0] == 0:
						print '\n\n\t検索中。。。\n\n\t'
						cursor.execute(sql[1]+' LIMIT 15')
						finalResults = cursor.fetchall()
						cursor.execute(sql[2]+' LIMIT 15')
						finalResults = finalResults + cursor.fetchall()
						finalResults = sorted(finalResults, key=operator.itemgetter(length),reverse=True)
						for item in finalResults:
							print '\t',
							print item[length],'\t',			
							for i in xrange(length):
								print reverseDictJP[item[i]],
							print '\n'
						print '\n'

			except EOFError:
				sys.exit('\n\tご利用ありがとうございます。\n\t')

	#共起率計算モード
	elif mode == '２' or mode =='2':
		flag = 0
		while(True):		
			try:
				queryWord = raw_input("""\n\t二つの日本語Nグラム単語を入力してください，グラムの間は<tab>鍵で間隔し，それぞれのグラムは一つ或は複数の単語で組むことができます、ただし単語の間で空白を入れ，両グラム最長7グラムです。\n\t例えば「日本の納豆」と「おいしい」という二つの単語の共起率を求める場合は，正確の入力は 「日本　の　納豆<tab>おいしい」となります\n\t<Ctrl> と <D>を同時に押すと終了する \n\n\n\t""")
				errorFlag = 1
				mainFlag = 1
				#入力が違法か否かを判断する
				while(mainFlag):
					if errorFlag == 0:
						queryWord = raw_input('\n\tもう一回お願いします：\n\t')
					errorFlag = 1
					legalQuery = co_occurInvalidCheck(queryWord)
					queryOrigi = legalQuery.split('	')
					first = queryOrigi[0].split('　')
					second = queryOrigi[1].split('　')
					allword = first+second
					errorWord = []
					order = 1
					#各个单词或字儿的合法性判别（在语料库中存在与否）
					for word in allword:
						if word not in dictJP:
							errorWord.append(word)
							errorFlag = 0
						elif errorFlag and order == len(allword):
							mainFlag = 0
						order += 1
					if errorFlag == 0:			
						print '\n\tすみません、入力した内容の中Googleデータにないものがあります：\n\t'
						for item in errorWord:
							print '\t「',item,'」',
						print '\n'
				
				#计算共起率
				words_count = 0
        			words_count += len(first)
        			words_count += len(second)

				N = []
				S = []
		
				#print '\n',first,'-----',second
		
				if len(first) > 1:
					for i in first:
						N.append(dictJP[i])
				else:					
					N.append(dictJP[first[0]])
		

				if len(second) > 1:
					for i in second:
						S.append(dictJP[i])
				else:					
					S.append(dictJP[second[0]])
				
				single_query = [N,S]

				query1 = [N,S]

				query2 = [S,N]

				query3 = [N,['＊'],S] 

				query4 = [S,['＊'],N]

				query5 = [N,['＊','＊'],S]

				query6 = [S,['＊','＊'],N]

				query7 = [N,['＊','＊','＊'],S]

				query8 = [S,['＊','＊','＊'],N]

				query9 = [N,['＊','＊','＊','＊'],S]

				query10 = [S,['＊','＊','＊','＊'],N]

				query11 = [N,['＊','＊','＊','＊','＊'],S]

				query12 = [S,['＊','＊','＊','＊','＊'],N]				
				
				query = [query1,query2,query3,query4,query5,query6,query7,query8,query9,query10,query11,query12]
				
				if words_count > 2:
		    			for i in xrange((words_count-2)*2):
		        			del query[11-i]

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
						print ('\n\t%dgram中：\n')%ngram				
				
					if sql[0] == 1:
						cursor.execute(sql[1])
						finalResults = cursor.fetchall()
						if len(finalResults) == 0:					
							co_occurNum += 0
							print '\t関連記録はありません\n'
						else:		
							for item in finalResults:
								eachCo_occurNum += int(item[length])
								co_occurNum += int(item[length])
								print '\t',
								print item[length],'\t',
								for i in xrange(length):
									print reverseDictJP[item[i]],
								print '\n'
							
		
					elif sql[0] == 0:
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
								print reverseDictJP[item[i]],
							print '\n'

					if timing%2 ==1:					
						print ('\n\t合計%dgram中に出現頻度は：')%ngram,eachCo_occurNum
						eachCo_occurNum = 0
					ngram += 0.5
					timing += 1
		

				singleGram = 0
				for j in single_query:
					print '\n\t単語： 「',queryOrigi[singleGram],'」：\n\t'					 	
					length = len(j)
					if length > 1:
						sql = wildcardSQL(j)
						cursor.execute(sql[1])
						finalResults = cursor.fetchall()
						if len(finalResults) == 0:					
							singleNum += 0
							print '\t出現頻度はゼロ'
						else:		
							for item in finalResults:
								singleNum += int(item[length])
								print '\t出現頻度は',int(item[length])
					else:				
						cursor.execute('SELECT freq from 1gram where ID=%s',j[0])
						finalResults = cursor.fetchall()
						if len(finalResults) == 0:
							singleNum += 0
							print '\t出現頻度はゼロ'
						else:		
								singleNum += int(finalResults[0][0])
								print '\t出現頻度は',int(finalResults[0][0])
					singleGram += 1

				co_ocurrence_value = co_occurNum / (singleNum-co_occurNum)
				
				print '\n\n\t',
				for i in first:
					print i,
				print '  AND  ',
				for j in second:
					print j,
		
				print '\n\t最終の共起率は：',co_ocurrence_value
			
			except EOFError:
					sys.exit('\n\tご利用ありがとうございます。\n\t')

	else:
		mode = raw_input('\n\t日本語入力モードで１或２を入力してください：')
