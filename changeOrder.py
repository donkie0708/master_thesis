#!usr/bin/python
#changeOrder.py

import csv

import sys

if len(sys.argv)!=2:

    print '\n','Usage : changeOrder.py file_name.csv'
    print '\n','This algorithm is for changing only the row orders of an csv file which has the header both in row and column.','\n'
    sys.exit()

original_file_name=sys.argv[1]

dicCMU={'':0,'bear':1, 'cat':2, 'cow':3, 'dog':4, 'horse':5, 'arm':6, 'eye':7, 'foot':8, 'hand':9, 'leg':10, 'apartment':11, 'barn':12, 'church':13, 'house':14, 'igloo':15, 'arch':16, 'chimney':17, 'closet':18, 'door':19, 'window':20, 'coat':21, 'dress':22, 'pants':23, 'shirt':24, 'skirt':25, 'bed':26, 'chair':27, 'desk':28, 'dresser':29, 'table':30, 'ant':31, 'bee':32, 'beetle':33, 'butterfly':34, 'fly':35, 'bottle':36, 'cup':37, 'glass':38, 'knife':39, 'spoon':40, 'bell':41, 'key':42, 'refrigerator':43, 'telephone':44, 'watch':45, 'chisel':46, 'hammer':47, 'pliers':48, 'saw':49, 'screwdriver':50, 'carrot':51, 'celery':52, 'corn':53, 'lettuce':54, 'tomato':55, 'airplane':56, 'bicycle':57, 'car':58, 'train':59, 'truck':60}

dicAkamaLab={'':0,'airplane':1, 'ant':2, 'apartment':3, 'arch':4, 'arm':5, 'barn':6, 'bear':7, 'bed':8, 'bee':9, 'beetle':10, 'bell':11, 'bicycle':12, 'bottle':13, 'butterfly':14, 'car':15, 'carrot':16, 'cat':17, 'celery':18, 'chair':19, 'chimney':20, 'chisel':21, 'church':22, 'closet':23, 'coat':24, 'corn':25, 'cow':26, 'cup':27, 'desk':28, 'dog':29, 'door':30, 'dress':31, 'dresser':32, 'eye':33, 'fly':34, 'foot':35, 'glass':36, 'hammer':37, 'hand':38, 'horse':39, 'house':40, 'igloo':41, 'key':42, 'knife':43, 'leg':44, 'lettuce':45, 'pants':46, 'pliers':47, 'refrigerator':48, 'saw':49, 'screwdriver':50, 'shirt':51, 'skirt':52, 'spoon':53, 'table':54, 'telephone':55, 'tomato':56, 'train':57, 'truck':58, 'watch':59, 'window':60}

newListCMU=range(61)

newListAkamaLab=range(61)

temp=csv.reader(open(original_file_name,'rb'))

for row in temp:

    newListCMU[dicCMU[row[0]]]=row

    newListAkamaLab[dicAkamaLab[row[0]]]=row

with file('CMUorder_'+original_file_name,'wb') as f:

    writer=csv.writer(f)

    writer.writerows(newListCMU)

with file('AkamaLabOrder_'+original_file_name,'wb') as f:

    writer=csv.writer(f)

    writer.writerows(newListAkamaLab)

print '\n','Sorting is done, two new files have been generated in the current directory.','\n'
