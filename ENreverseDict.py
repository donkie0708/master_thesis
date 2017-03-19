#import MySQLdb
import cPickle
import sys
import allPaths
# -*- coding: utf-8 -*-



#prepare for 1gram dictionary data structure
dictForUnigram = {}
tempList = []
tempListForDict = []
ID = 1


#make the dictionary and insert 1gram data into table
with open('/home/akamalab/Desktop/vocab','rb') as f:
	for line in f:
		tempParse=line.split('\t')
		tempListForDict.append((ID,tempParse[0])) 
		ID+=1
dictForUnigram = dict(tempListForDict)

#generate the pickle data structure
with open('/home/akamalab/Desktop/python_ngram/ENvocabularyReverse.pkl','wb') as output:
	cPickle.dump(dictForUnigram, output)

