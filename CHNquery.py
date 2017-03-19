# -*- coding: utf-8 -*-
import MySQLdb
import cPickle
import sys
import allPaths
import time
import os
import chooseQuery
import operator
from spare import *


tts = time.ctime()

print '\n正在加载程序。。。\n'
with open(allPaths.CHNvocabPath,'rb+') as f:
	dictCHN = cPickle.load(f)
with open(allPaths.CHNvocabReversePath,'rb+') as f:
	reverseDictCHN = cPickle.load(f)
print '加载完毕！\n'

#connect to the database
try:
	db = MySQLdb.connect(
		host = 'localhost',
		user = 'root',
		passwd = 'fmri',
		db = 'chn_ngram',
		charset='utf8',
		local_infile = 1
		)
except Exception as e:
	sys.exit('Could not be able to get into the database!')

cursor = db.cursor()
while(True):
	try:
		queryWord = raw_input('\n\t<Google中文N-gram语料库的查询系统 version 1.0> \n\t此程序可以查询特定N-gram在语料库中的出现频率，请以单词为单位输入中文（单词间用空格隔开，最多为5个单词，注意一个单词应为一个语法单位，如“我是中国人”应拆开输入为 “我 是 中国人”）\n\t1.可以用“*”代表任意单词(目前的版本不支持首位出现“*”号)\n\t2.退出程序请同时按 <Ctrl> 加 <D> \n\n\n\t')
		#deal with the invaild input
		queryWord = chooseQuery.invalidCheck(queryWord)

		#check the word in dictionary,if there's no such word,change another and try again.
		query = queryWord.split(' ')
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
						word = raw_input('\n\tGoogle的语料库中没有“%s”这个单词，请重新输入另一个单词： \n\t'%word)
						time += 1
						wordNew = word.split(' ')
						word = wordNew[0]
						if len(wordNew) > 1:
							flag1 = 1
							while(flag1):
								word = raw_input('\n\t您已无权输入多个词语，请输入一个不带空格的单词或字： \n\t')
								wordNew1 = word.split(' ')
								if len(wordNew1) == 1:
									flag1 = 0
								word = wordNew1[0]
					
					else:
						word = raw_input('\n\t你是存心找茬儿是吗？赶紧的!输个正常词儿\n\t')
						time += 1
						wordNew = word.split(' ')
						word = wordNew[0]
						if len(wordNew) > 1:
							while(wordNew1 > 1):
								word = raw_input('\n\t您已无权输入多个词语，请输入一个不带空格的单词或字： \n\t')
								wordNew1 = word.split(' ')
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
				if item != '*':			
					cursor.execute('SELECT ID from 1gram where word=%s',item)
					result = cursor.fetchone()			
					finalSQL.append(result[0])
				else:
					finalSQL.append('*')
			
		#for num in finalSQL:
			#print num
		if len(query) > 1:
			sql = wildcardSQL(finalSQL)
			if sql[0] == 1:
				print '\n\n\t正在查找。。。\n\n\t'
				cursor.execute(sql[1])
				finalResults = cursor.fetchall()
				if len(finalResults) == 0:
					print '\n\t对不起，您所查找的N-gram，在语料库中无法找到！\n\t'
				else:		
					for item in finalResults:
						print '\t',
						for i in xrange(length):
							print reverseDictCHN[item[i]],
						print '\t',item[length]
					print '\n'
	
			#Output for the n-gram lying between files
			elif sql[0] == 0:
				print '\n\n\t正在查找。。。\n\n\t'
				cursor.execute(sql[1])
				finalResults = cursor.fetchall()
				cursor.execute(sql[2])
				finalResults = finalResults + cursor.fetchall()
				finalResults = sorted(finalResults, key=operator.itemgetter(length),reverse=True)
				for item in finalResults:
					print '\t',			
					for i in xrange(length):
						print reverseDictCHN[item[i]],
					print '\t',item[length]	
				print '\n'

	except EOFError:
		sys.exit('\n\t不会用就别用！\n\t')

