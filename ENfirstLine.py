# -*- coding: utf-8 -*-
import sys
import allPaths
import time
import os


def findHead():

	tempPath = allPaths.ENgeneratedMidFileDir
	numList = allPaths.ENeach2toNgramfiles
	tempFiles = []
	initNum = 2
	stdSuffix = '0000'
	#For command 'executemany()' using
	ngramdata=[2,3,4,5]

	#create the paths for inserting the corresponding files
	for Ngram in numList:
		for fileName in xrange(Ngram):
			
			if fileName<=9:
				tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-1],str(fileName))))
			elif 99>=fileName>9:
				tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-2],str(fileName))))
			else:
				tempFiles.append(''.join((tempPath,'/',str(initNum),'gms/',str(initNum),'gm-',stdSuffix[:-3],str(fileName))))	
		initNum += 1




	firstLine = []
	#create tables for each n-gram
	for i in tempFiles[:numList[0]]:		
		with open(i,'rb') as r:
			string = r.readline()
			string ='\t'.join((string[:-1],i[-8:]))		
			firstLine.append(string)
			

	for i in tempFiles[numList[0]:(numList[0]+numList[1])]:
		with open(i,'rb') as r:
			string = r.readline()
			string ='\t'.join((string[:-1],i[-8:]))		
			firstLine.append(string)
	

	for i in tempFiles[(numList[0]+numList[1]):(numList[0]+numList[1]+numList[2])]:
		with open(i,'rb') as r:
			string = r.readline()
			string ='\t'.join((string[:-1],i[-8:]))		
			firstLine.append(string)
				
	
	for i in tempFiles[(numList[0]+numList[1]+numList[2]):]:
		with open(i,'rb') as r:
			string = r.readline()
			string ='\t'.join((string[:-1],i[-8:]))		
			firstLine.append(string)
	
	
	
	return firstLine

