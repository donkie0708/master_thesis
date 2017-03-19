#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import socket
import pickle
import JPservermethod0515 as serverMethod
import sys
from time import ctime

'''
host为空表示bind可以绑定到所有有效地址上
port 必须要大于1024
bufsiz为缓冲区 我们设置为1024(1k)
'''
host = ''  
port = 23457
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
	db = 'jp_ngram',
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
        print '通信コネクションを待っている...'
        newTcpSerSock,addr = tcpSerSock.accept()
        print addr,'　と通信コネクションが確定されました。'

        while True:
	    try:
                dataFromClient = newTcpSerSock.recv(bufsiz)
	    except socket.error:
		continue
	    if not dataFromClient:
		print '何もない!\n'                
		break
	    print dataFromClient
	    try:
		statInput = serverMethod.JPinputValidator(dataFromClient)
	    except:
		print 'Unexpected error:',sys.exc_info()
		newTcpSerSock.send(pickle.dumps(['Un expected error',]))
		continue
	    if statInput[0] == 0:
		pass
	    elif statInput[0] == 1:
		newTcpSerSock.send(pickle.dumps(['JP','invalid',['以下の単語はコーパスに存在しませんので、改めて入力してください！'],statInput[1]]))
		continue
	    resultForC = []
	    
	    resultForC = serverMethod.whichmode(dataFromClient)
	
	    resultForC.insert(0,'JP')
            
	    newTcpSerSock.send(pickle.dumps(resultForC,-1))
	    
except KeyboardInterrupt:
    print '管理者に中止されました！'
    tcpSerSock.close()    
finally:
    tcpSerSock.close()  #记住在服务器退出时记得关闭
