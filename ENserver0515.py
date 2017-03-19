#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import socket
import pickle
import ENservermethod0515 as ENserverMethod
from time import ctime

'''
host为空表示bind可以绑定到所有有效地址上
port 必须要大于1024
bufsiz为缓冲区 我们设置为1024(1k)
'''
host = ''  
port = 33457
bufsiz = 65536*64
ADDR = (host,port)

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)   #参数表示允许多少连接同时连进来


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


try:
    while True:
        '''
        进入服务器的无限循环中，等待连接到来
        有链接时，进入对话循环，等待客户发送数据，如果消息为空，表示客户端已经退出，等待下一个客户端连接
        得到客户端消息后在消息前加一个时间戳后返回
        '''
        print 'waiting for connection...'
        newTcpSerSock,addr = tcpSerSock.accept()
        print '...connected from ',addr

        while True:
	    try:
                dataFromClient = newTcpSerSock.recv(bufsiz)
	    except socket.error:
		continue
	    if not dataFromClient:
		print 'Got nothing!\n'                
		break
	    data = dataFromClient.split()
	    print dataFromClient
	    query = data[1:]
	    statInput = ENserverMethod.inputValidator(query)
	    if statInput[0] == 0:
		pass
	    elif statInput[0] == 1:
		newTcpSerSock.send(pickle.dumps(['EN','invalid',['There are no such words in the corpus! Please input again.'],statInput[1]]))
		continue
	    resultForC = []
	    
	    resultForC = ENserverMethod.whichmode(dataFromClient)

	    resultForC.insert(0,'EN')
            
	    newTcpSerSock.send(pickle.dumps(resultForC,-1))

except KeyboardInterrupt:
    print '\nTerminated by administrator!'	    
    tcpSerSock.close()
finally:
    tcpSerSock.close()  #记住在服务器退出时记得关闭
