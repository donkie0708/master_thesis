# -*- coding: utf-8 -*-
import wx,threading,socket,sys,goslate
import pickle
import time
from wx.lib.pubsub import Publisher

gs = goslate.Goslate()

class serverConn(threading.Thread):
    def __init__(self,host,port,msg=None):
	threading.Thread.__init__(self)
	self.ADDR = (host,port)
	self.msg = msg
	self.recvList = []
	#self.start()
	

    def run(self):

	try:
	    self.tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    self.tcpCliSock.connect(self.ADDR)
	except Exception as e:
		sys.exit('Could not be able to get into the database!')
	wx.CallAfter(self.sendAndRecv,self.msg)

    def sendAndRecv(self,msgTo):
	self.tcpCliSock.send(msgTo)
	self.receive = self.tcpCliSock.recv(65536*64)
	
	try:
            self.recvList = pickle.loads(self.receive)
        except:
            self.recvList = ['','','The result for the current inquiry is too large,You may consider the [Limit] option,and try it again!']
            self.tcpCliSock.close()
	    #self.recvList = []
	    #self.recvList.append(['The result for the current inquiry is too large,You may consider the [Limit] option,and try it again!'])
	#if self.recvList[1] == 'invalid':
	    #self.recvList[1] = ['There are no such words below in the database:']
	#if self.recvList[1] == 0:
	    #self.recvList.append(['Sorry,found nothing in the corpus.'])
	#elif self.recvList[1] == 1:
	    #self.recvList = self.recvList[2:]
	    #pass
	#return self.recvList
	Publisher().sendMessage("update", self.recvList)
	self.tcpCliSock.close()
	

class checkPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
	wx.Panel.__init__(self, parent, *args, **kwargs)
	self.ENcheck = wx.CheckBox(self, -1, "English",  size=(90,-1))
	self.JPcheck = wx.CheckBox(self, -1, "Japanese",  size=(90,-1))
	self.CHNcheck = wx.CheckBox(self, -1, "Chinese",  size=(90,-1))
	self.Bind(wx.EVT_CHECKBOX, self.enableConn, self.ENcheck)
	self.Bind(wx.EVT_CHECKBOX, self.enableConn, self.JPcheck)
	self.Bind(wx.EVT_CHECKBOX, self.enableConn, self.CHNcheck)
	#self.connectButton = wx.Button(self, label="Connect")
	#self.Bind(wx.EVT_BUTTON, self.OnClick, self.connectButton)
	#self.connectButton.Enable(False)

	self.sizerH = wx.BoxSizer(wx.HORIZONTAL)
	#self.sizerV = wx.BoxSizer(wx.VERTICAL)
	self.sizerH.Add(self.ENcheck, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 25)
	self.sizerH.Add(self.JPcheck, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 25)
	self.sizerH.Add(self.CHNcheck, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 25)
	#self.sizerH.Add(self.sizerV, 2, wx.ALIGN_LEFT|wx.ALL, 5)
	#self.sizerH.Add(self.connectButton, 1, wx.ALIGN_CENTER|wx.ALL, 25)

	self.SetSizer(self.sizerH)
	self.SetAutoLayout(1)

    def enableConn(self,event):
	if self.ENcheck.IsChecked():
	    if self.checkConn('EN'):
	        pass
	    else:
	    	self.ConnWarning('English')
	    	self.ENcheck.SetValue(False)
	    	
	elif self.JPcheck.IsChecked():
	    if self.checkConn('JP'):
	        pass
	    else:
	    	self.ConnWarning('Japanese')
	    	self.JPcheck.SetValue(False)
	elif self.CHNcheck.IsChecked():
	    if self.checkConn('CHN'):
	        pass
	    else:
	    	self.ConnWarning('Chinese')
	    	self.JPcheck.SetValue(False)

    def checkConn(self,which):
    	self.conn = 1
	self.EN = ('192.168.11.15',33457)
	self.JP = ('192.168.11.15',23457)
	self.CHN = ('192.168.11.12',23457)
	if which == 'EN':
	    try:
	        self.ADDR = self.EN
	        self.tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        self.tcpCliSock.connect(self.ADDR)
	    except Exception as e:
		self.conn = 0
	    self.tcpCliSock.close()
	elif which == 'JP':
	    try:
	        self.ADDR = self.JP
	        self.tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        self.tcpCliSock.connect(self.ADDR)
	    except Exception as e:
		self.conn = 0
	    self.tcpCliSock.close()
	elif which == 'CHN':
	    try:
	        self.ADDR = self.CHN
	        self.tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        self.tcpCliSock.connect(self.ADDR)
	    except Exception as e:
		self.conn = 0
	    self.tcpCliSock.close()
	return self.conn
	
    def ConnWarning(self,msg):
        dial = wx.MessageDialog(None, "Can't access to the '"+msg+"' server!", 'Warning', wx.OK)
        dial.ShowModal()
	
class recordSearchPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
	wx.Panel.__init__(self, parent, *args, **kwargs)
	self.p = wx.Panel(self)
        self.recordLimit = wx.StaticText(self.p,-1, "LIMIT for showing records ", pos=(20,0), style=wx.ALIGN_CENTRE)
	self.sld = wx.Slider(self.p, value=15, minValue=5, maxValue=100, pos=(20,50), size=(100, 20), style=wx.SL_HORIZONTAL)
	self.txt = wx.StaticText(self.p, label='15', pos=(20, 90), style=wx.ALIGN_CENTRE)
	self.sld.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
	
	self.query = wx.TextCtrl(self, value="Input query here:  never * * * *   eg.", size=(100,-1))
	self.sizer = wx.BoxSizer(wx.VERTICAL)
	self.sizer.Add(self.p, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 20)
	
	self.sizer.Add(self.query, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 20)
	self.SetSizer(self.sizer)
	self.SetAutoLayout(1)
	
    def OnSliderScroll(self, e):
        
        obj = e.GetEventObject()
        val = obj.GetValue()
        if val == 100:
            self.txt.SetLabel('NO LIMIT')
            
        else:
            self.txt.SetLabel(str(val))  
	
    def getValueFor1stMode(self,lan):
        
        limit = str(self.sld.GetValue())
	if lan == 'EN':
	    query = '1 ' + limit + ' ' + (gs.translate(self.query.GetValue(),'en')).encode('utf-8')
	elif lan == 'JP':
	    query = '1　' + limit + '　' + (gs.translate(self.query.GetValue(),'ja')).encode('utf-8')
	elif lan == 'CHN':
	    query = '1 ' + limit + ' ' +  (gs.translate(self.query.GetValue(),'zh')).encode('utf-8')
	
	print query
	
	return query
	

	

class searchPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
	wx.Panel.__init__(self, parent, *args, **kwargs)
	self.panel = wx.Panel(self)
	#self.grid = wx.GridBagSizer(3, 3)
	self.sb1 = wx.StaticBox(self, -1, '1st concept', pos=(15,20), size=(380, 80)) 
	self.sb2 = wx.StaticBox(self, -1, '2nd concept', pos=(15,110), size=(380, 80)) 
	self.word1 = wx.TextCtrl(self, value=u"りんご", pos=(35,50), size=(100,-1))
	self.word2 = wx.TextCtrl(self, value=u"アップル", pos=(35,140), size=(100,-1))
	twoChoices = ["Fixed word","As concept"]
	self.radioList1 = wx.RadioBox(self, choices=twoChoices, pos=(160,35), style=wx.RA_HORIZONTAL)
	self.radioList2 = wx.RadioBox(self, choices=twoChoices, pos=(160,125), style=wx.RA_HORIZONTAL)


    def getValueFor2ndMode(self,lan):
        query = ''
	if lan == 'EN':
	    query = '2 ' + (gs.translate(self.word1.GetValue(),'en')).encode('utf-8') + '\t' + (gs.translate(self.word2.GetValue(),'en')).encode('utf-8')
	elif lan == 'JP':
	    query = '2　' + (gs.translate(self.word1.GetValue(),'ja')).encode('utf-8') + '\t' + (gs.translate(self.word2.GetValue(),'ja')).encode('utf-8')
	elif lan == 'CHN':
	    query = '2 ' + (gs.translate(self.word1.GetValue(),'zh')).encode('utf-8') + '\t' + (gs.translate(self.word2.GetValue(),'zh')).encode('utf-8')
	#query = ' '.join(('2',self.word1.GetValue().decode('utf-8'),self.word2.GetValue().decode('utf-8')))
	print query
	#self.query = query
	return query
	#self.grid.Add(self.sText1, pos=(0,1))
	#self.grid.Add(self.word1, pos=(0,2))
	#self.grid.Add(self.sText2, pos=(3,1))
	#self.grid.Add(self.word2,pos=(3,2))
	#self.grid.Add(self.radioList1,pos=(0,3))
	#self.grid.Add(self.radioList2,pos=(3,3))

	#self.SetSizer(self.grid)
	#self.SetAutoLayout(1)
	


class ENpanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
	wx.Panel.__init__(self, parent, *args, **kwargs)
	self.textPanel = wx.Panel(self)
	self.ENtext = wx.StaticText(self.textPanel,-1, "English", (100,0), (-1,-1), wx.ALIGN_CENTRE)
	self.ENtext.SetForegroundColour('red')
	self.ENwindow = wx.TextCtrl(self, style=wx.TE_MULTILINE)
	self.sizer = wx.BoxSizer(wx.VERTICAL)
	self.sizer.Add(self.textPanel, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	self.sizer.Add(self.ENwindow, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	#self.ENtext.Centre()
	
	self.SetSizer(self.sizer)
	self.SetAutoLayout(1)


class JPpanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
	wx.Panel.__init__(self, parent, *args, **kwargs)
	self.textPanel = wx.Panel(self)
	self.JPtext = wx.StaticText(self.textPanel,-1,"Japanese", (100,0), (-1,-1), wx.ALIGN_CENTRE)
	self.JPtext.SetForegroundColour('red')
	self.JPwindow = wx.TextCtrl(self, style=wx.TE_MULTILINE)
	self.sizer = wx.BoxSizer(wx.VERTICAL)
	self.sizer.Add(self.textPanel, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	self.sizer.Add(self.JPwindow, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	#self.JPtext.Centre()
	
	self.SetSizer(self.sizer)
	self.SetAutoLayout(1)


class CHNpanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
	wx.Panel.__init__(self, parent, *args, **kwargs)
	self.textPanel = wx.Panel(self)
	self.CHNtext = wx.StaticText(self.textPanel,-1,"Chinese", (100,0), (-1,-1), wx.ALIGN_CENTRE)
	self.CHNtext.SetForegroundColour('red')
	self.CHNwindow = wx.TextCtrl(self, style=wx.TE_MULTILINE)
	self.sizer = wx.BoxSizer(wx.VERTICAL)
	self.sizer.Add(self.textPanel, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	self.sizer.Add(self.CHNwindow, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	#self.CHNtext.Centre()
	
	self.SetSizer(self.sizer)
	self.SetAutoLayout(1)


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
	
	self.mysize = wx.GetDisplaySize()
	wx.Frame.__init__(self, parent, wx.ID_ANY, title=title, pos=(0,40), size=(420,400))
	self.CreateStatusBar() # A Statusbar in the bottom of the window	
	self.searchButton = wx.Button(self, label="Search")
	self.Bind(wx.EVT_BUTTON, self.OnClick, self.searchButton)
	#self.searchButton.Enable(False)
	self.check = checkPanel(self)
	self.nb = wx.Notebook(self)
	self.corpus = recordSearchPanel(self.nb)
	self.wordnet = searchPanel(self.nb)
	self.staLine = wx.StaticLine(self, -1, size=(300,1))
	self.nb.AddPage(self.corpus, "Corpus query mode")
	self.nb.AddPage(self.wordnet, "WordNet associated")
	
	
        self.relativePos = (int(self.mysize[0]*0.3),40)
        
	self.topSizer = wx.BoxSizer(wx.VERTICAL) 
	self.topSizer.Add(self.check, 0, wx.EXPAND)
	self.topSizer.Add(self.staLine, 0, wx.EXPAND|wx.ALIGN_CENTER)
	self.topSizer.Add(self.nb, 1, wx.EXPAND)
	self.topSizer.Add(self.searchButton, 0, wx.EXPAND|wx.BOTTOM)
	
	self.SetSizer(self.topSizer)
	
        self.SetAutoLayout(1)
        #self.topSizer1.Fit(self)
        self.Show()
	Publisher().subscribe(self.updateDisplay, "update")
	

    def OnClick(self,event):    
	if self.nb.GetSelection() == 0:
	    self.getword = self.corpus.getValueFor1stMode
	    self.subframeCo_occur = SubWindow(frame, 'Ngram Records', mypos=self.relativePos, mysize=(int(self.mysize[0]*0.6),int(self.mysize[1]*0.6)))
	elif self.nb.GetSelection() == 1:
	    self.getword = self.wordnet.getValueFor2ndMode
	    self.subframeCo_occur = SubWindow(frame, 'Co-occurence Results', mypos=self.relativePos, mysize=(int(self.mysize[0]*0.6),int(self.mysize[1]*0.6)))
	self.relativePos = (self.relativePos[0]+25,self.relativePos[1]+25)
	if self.check.ENcheck.IsChecked():
	    ENquery = serverConn('192.168.11.15', 33457)
	    ENquery.setDaemon(True)
	    #self.query = self.wordnet.getValueFor2ndMode('EN')
	    self.query = self.getword('EN')
	    ENquery.msg = self.query
	    #Publisher().subscribe(self.JPupdateDisplay, "update")
	    #result = JPquery.sendAndRecv(self.query)
	    #self.subframeCo_occur.showResult('JP', result)
	    ENquery.start()
	if self.check.JPcheck.IsChecked():
	    JPquery = serverConn('192.168.11.15', 23457)
	    JPquery.setDaemon(True)
	    #self.query = self.wordnet.getValueFor2ndMode('JP')
	    self.query = self.getword('JP')
	    JPquery.msg = self.query
	    #Publisher().subscribe(self.JPupdateDisplay, "update")
	    #result = JPquery.sendAndRecv(self.query)
	    #self.subframeCo_occur.showResult('JP', result)
	    JPquery.start()
	    #result = JPquery.recvList
	    #self.subframeCo_occur.showResult('JP', result)
	if self.check.CHNcheck.IsChecked():
	    CHNquery = serverConn('192.168.11.12', 23457)
	    CHNquery.setDaemon(True)
	    #self.input.getValueFor2ndMode('CHN')
	    #self.query = self.input.query
	    #self.query = self.wordnet.getValueFor2ndMode('CHN')
	    self.query = self.getword('CHN')
	    CHNquery.msg = self.query
	    #Publisher().subscribe(self.CHNupdateDisplay, "update")
	    #result = CHNquery.sendAndRecv(self.query)
	    #self.subframeCo_occur.showResult('CHN', result)
	    CHNquery.start()
	    #result = CHNquery.recvList
	    #self.subframeCo_occur.showResult('CHN', result)

    #def JPupdateDisplay(self,msg):
	#result = msg.data
	#if result[0] == 'JP':
	    #self.subframeCo_occur.showResult('JP', result[2:])  
	    
    #def CHNupdateDisplay(self,msg):
	#result = msg.data
	#if result[0] == 'CHN':
	    #self.subframeCo_occur.showResult('CHN', result[2:])  

	#t=threading.Thread(target=self.__run)
	#t.start()

    def updateDisplay(self,msg):
	result = msg.data
	if result[0] == 'JP':
	    self.subframeCo_occur.showResult('JP', result[2:])  
	elif result[0] == 'CHN':
	    self.subframeCo_occur.showResult('CHN', result[2:])
	elif result[0] == 'EN':
	    self.subframeCo_occur.showResult('EN', result[2:])       
	

    


class SubWindow(wx.Frame):
    def __init__(self, parent, title, mypos, mysize):
	
	wx.Frame.__init__(self, parent, wx.ID_ANY, title=title, pos=mypos, size=mysize)
        
	self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
	
	self.sizer1 = ENpanel(self)
	self.sizer2 = JPpanel(self)
	self.sizer3 = CHNpanel(self)
	
	self.topSizer.Add(self.sizer1,1,wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	self.topSizer.Add(self.sizer2,1,wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)
	self.topSizer.Add(self.sizer3,1,wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)

	self.SetSizer(self.topSizer)
        self.Show()


    def showResult(self,lan,result):
        
	if lan == 'EN':
	    for record in result:
		for item in record:
		    try:
                        self.sizer1.ENwindow.AppendText(str(item)+'\t')
                    except UnicodeEncodeError:
                        self.sizer1.ENwindow.AppendText(item.encode('utf-8')+'\t')
		self.sizer1.ENwindow.AppendText('\n\n')
	elif lan == 'JP':
	    for record in result:
		for item in record:
		    try:
                        self.sizer2.JPwindow.AppendText(str(item)+'\t')
                    except UnicodeEncodeError:
                        self.sizer2.JPwindow.AppendText(item.encode('utf-8')+'\t')
		self.sizer2.JPwindow.AppendText('\n\n')
	elif lan == 'CHN':
	    print 'Hi CHN'
	    for record in result:
		for item in record:
		    try:
                        self.sizer3.CHNwindow.AppendText(str(item)+'\t')
                    except UnicodeEncodeError:
                        self.sizer3.CHNwindow.AppendText(item.encode('utf-8')+'\t')
		self.sizer3.CHNwindow.AppendText('\n\n')
 
     
		


if __name__ == '__main__':
    app = wx.App()
    frame = MainWindow(None, "Search Terminal")
    app.MainLoop()
