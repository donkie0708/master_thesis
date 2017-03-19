# -*- coding: utf-8 -*-
import MySQLdb
import cPickle
import sys
import operator # for list sort funtion
import allPaths 
import method


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


def inputValidator(query):

    invalidList = []
    for word in query:
	if (word not in dictJP) and (word != '＊'):
	    invalidList.append(word)
    if invalidList == []:
	# 0 means no invalid words	
	result = 0  
	return [result,invalidList]
    else:
	# 1 means user input contains invalid words, and then send the signal back to server	
	result = 1
	return [result,invalidList]  

def JPinputValidator(rawStr):

    invalidList = []
    if rawStr.split('　')[0]=='1':
	#print '进入频率模式判断'
	for word in rawStr.split('　')[2:]:
	    #print word
	    if (word not in dictJP) and (word != '＊'):
	        invalidList.append(word)
		
    elif rawStr.split('　')[0]=='2' or rawStr.split('　')[0]=='3':
	#print '进入共起率模式判断'
        query = rawStr.split('\t')
        for word in query[0].split('　'):
	    print word
	    if (word not in dictJP) and (word != '＊'):
	        invalidList.append(word)
        for word in query[1].split('　'):
	    print word
	    if (word not in dictJP) and (word != '＊'):
	        invalidList.append(word)
    if invalidList == []:
	# 0 means no invalid words	
	result = 0  
	return [result,invalidList]
    else:
	# 1 means user input contains invalid words, and then send the signal back to server	
	result = 1
	return [result,invalidList]  



def seqQuery(query):
    limit = ''
    semi = int(query[0])/2
    if query[0] == 100:
	pass
    else:
	limit = ' LIMIT '+str(query[0])
	semiLimit = ' LIMIT '+str(semi)
    resultForC = []
    length  = len(query[1:])
    #In single word case, execute query directly.
    if length == 1:
    	cursor.execute('SELECT word,freq from 1gram where word=%s',(query[1],))
    	result = cursor.fetchone()
	if result !=[]:
	    resultForC.append(1)
            result = [result[1],result[0]]
	    resultForC.append(result)
        elif result ==[]:			
	    resultForC.append(0)
    else:
	finalSQL = []		
        for item in query[1:]:
	    #print item
	    if item != '＊':
	        finalSQL.append(dictJP[item])
	    else:
	        finalSQL.append('＊')

	#print finalSQL
	sql = method.wildcardSQL(finalSQL)
        if sql[0] == 1:
	    cursor.execute(sql[1]+limit)
	    finalResults = cursor.fetchall()
	    if len(finalResults) == 0:
		resultForC.append(0)
	    else:
		resultForC.append(1)		
		for record in finalResults:
		    # midResult for one record(one line),record[length] is the frequency number
		    midResult = []
		    midResult.append(record[length])
		    for i in xrange(length):
			midResult.append(reverseDictJP[record[i]]) 
		    resultForC.append(midResult)

	elif sql[0] == 0:
	    cursor.execute(sql[1]+semiLimit)
	    finalResults = cursor.fetchall()
	    cursor.execute(sql[2]+semiLimit)
            finalResults = finalResults + cursor.fetchall()
	    finalResults = sorted(finalResults, key=operator.itemgetter(length),reverse=True)	
	    resultForC.append(1)
	    for record in finalResults:
		# midResult for one record(one line),record[length] is the frequency number
		midResult = []
		midResult.append(record[length])
		for i in xrange(length):
	            midResult.append(reverseDictJP[record[i]]) 
		resultForC.append(midResult)

    return resultForC	


def co_occurQuery(first,second):
    limit = 6
    resultForC = []
    resultForC.append(1)
    words_count = 0
    words_count += len(first)
    words_count += len(second)

    N = []
    S = []
	
		
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
	sql = method.wildcardSQL(listNew)
	if timing%2 ==0:
            nTag = ('順番%dgramの中：')%ngram
	else:
	    nTag = ('逆順番%dgramの中：')%ngram
	resultForC.append([nTag])


	if sql[0] == 1:
	    counter = 0
	    cursor.execute(sql[1])
	    finalResults = cursor.fetchall()
	    if len(finalResults) == 0:					
		co_occurNum += 0
		resultForC.append(['記録はありません'])

	    else:							
		for item in finalResults:
		    midResult = []
		    eachCo_occurNum += int(item[length])
		    co_occurNum += int(item[length])
		    #print '\t',
		    #print item[length],'\t',
		    counter += 1
		    if counter < limit:
		        midResult.append(item[length])
		        for i in xrange(length):
			    #print reverseDictJP[item[i]],
			    midResult.append(reverseDictJP[item[i]])
		        resultForC.append(midResult)
		    else:
			continue
		if limit < counter:
		    resultForC.append(['省略。。。'])  
		

	elif sql[0] == 0:
	    counter = 0
	    #print '\n\n\t正在查找。。。\n\n\t'
	    cursor.execute(sql[1])
	    finalResults = cursor.fetchall()
	    cursor.execute(sql[2])
	    finalResults = finalResults + cursor.fetchall()
	    finalResults = sorted(finalResults, key=operator.itemgetter(length),reverse=True)
	    for item in finalResults:
		midResult = []
		eachCo_occurNum += int(item[length])
		co_occurNum += int(item[length])
		#print '\t',
		#print item[length],'\t',
		counter += 1
	        if counter < limit:
		    midResult.append(item[length])			
		    for i in xrange(length):
		        #print reverseDictCHN[item[i]],
		        midResult.append(reverseDictJP[item[i]])
		    resultForC.append(midResult)
		else:
		    continue
	    if limit < counter:
		resultForC.append(['省略。。。'])  
	        

	if timing%2 ==1:					
	    #print ('\n\t在%dgram中总共出现次数为:')%ngram,eachCo_occurNum
	    nReTag = ('%dgramの中に出現回数:')%ngram
	    resultForC.append([nReTag,eachCo_occurNum])
	    eachCo_occurNum = 0
	    ngram += 1
					
	timing += 1


    first.insert(0,'単語：　「')
    first.append('」　の出現頻度：')
    second.insert(0,'単語：　「')
    second.append('」　の出現頻度：')
    tagCount = 1	
    for j in single_query:
        #print '\n\t单词: [',queryOrigi[singleGram],'] 的出现频率：\n\t'				 	
        length = len(j)
        #print '单个长度为',length
	if length > 1:
	    sql = method.wildcardSQL(j)
	    #print j
	    cursor.execute(sql[1])
	    finalResults = cursor.fetchall()
	    #print '单个结果',finalResults
	    if len(finalResults) == 0:
		#print '单元共起+0前',singleNum					
		singleNum += 0
	        #print '单元共起+0后',singleNum
		#print '\t结果为零'
		if tagCount==1:
		    first.append(0)
		else:
		    second.append(0)

	    else:		
		for item in finalResults:
		    singleNum += int(item[length])
		    #print '单元共起目前为',singleNum
		    #print '\t结果为',int(item[length])
		    if tagCount==1:
		        first.append(item[length])
		    else:
		        second.append(item[length])


	else:
	    #print '这是一个字儿的情况'				
	    cursor.execute('SELECT freq from 1gram where ID=%s',j[0])
	    finalResults = cursor.fetchall()
	    #print '单个结果',finalResults
	    if len(finalResults) == 0:
		singleNum += 0
		#print '\t单个结果为零'
		if tagCount==1:
		    first.append(0)
		else:
		    second.append(0)

	    else:		
		singleNum += int(finalResults[0][0])
		#print '单元共起目前为',singleNum
		#print '\t结果为',int(singleNum)
		if tagCount==1:
		    first.append(int(singleNum))
		else:
		    second.append(int(singleNum))

	tagCount += 1

    
    resultForC.append(first)
    resultForC.append(second)
    co_ocurrence_value = co_occurNum / (singleNum-co_occurNum)
		
    print '\n\t共起率：',co_ocurrence_value
    resultForC.append(['共起率：'])
    resultForC.append([co_ocurrence_value])




    return resultForC




	

def whichmode(rawData):
    # data[0] is mode code, '1' will do as the query for the record in the database, '2' is co-occurence calculation, '3' will connect to the WORDNET, as we call it 'wordnet association query'
    data = rawData.split('　')
    if data[0] == '1':
	query = data[1:]
	return seqQuery(query)
    elif data[0] == '2':
	query = rawData.split('\t')
	first = query[0].split('　')[1:]
	second = query[1].split('　')
	return co_occurQuery(first,second)
















	
