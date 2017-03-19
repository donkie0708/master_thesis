"""
A simulator for a model that predicts fMRI activation using machine learning technique
presented by Tom M.Mitchell et al in Science paper(2008).
"""
from scipy.io import loadmat
from scipy.stats import f_oneway
from itertools import combinations
from operator import itemgetter
from random import sample
import numpy,sys,math


__author__ = 'Wang Zheng'
__email__ = 'wang.z.af@m.titech.ac.jp'
__version__ = '1.1'
__see__ = 'http://www.sciencemag.org/content/320/5880/1191.full'



#define a class for structured result
class result():
	pass


#define some methods for analysing data

# two functions using different module to draw heat map
def _usePlotly(data):
	import plotly.plotly as py
	import plotly.graph_objs
	# Fill in with your personal username and API key
	# or, use this public demo account
	py.sign_in('Python-Demo-Account', 'gwt101uhh0')

	data = plotly.graph_objs.Data([plotly.graph_objs.Heatmap(z=data,colorscale='Jet')])
	layout = plotly.graph_objs.Layout(title='similarity map')
	fig = plotly.graph_objs.Figure(data=data, layout=layout)
	plot_url = py.plot(fig, filename='Jet-heatmap')

def _useMatplotlib(data, labels):
	import matplotlib.pyplot as plt
	fig, ax = plt.subplots()
	heatmap = ax.pcolor(data, cmap=plt.cm.jet, vmin=-1, vmax=1)
	# Format
	fig = plt.gcf()
	fig.set_size_inches(10, 10)
	# turn off the frame
	ax.set_frame_on(False)
	# put the major ticks at the middle of each cell
	ax.set_yticks(numpy.arange(data.shape[0]) + 0.5, minor=False)
	ax.set_xticks(numpy.arange(data.shape[1]) + 0.5, minor=False)
	# table-like display
	ax.invert_yaxis()
	ax.xaxis.tick_bottom()
	ax.set_xticklabels(labels, minor=False, fontsize='x-small')
	ax.set_yticklabels(labels, minor=False, fontsize='x-small')
	# rotate x axis labels
	plt.xticks(rotation=90)
	# plot it out
	plt.colorbar(heatmap)
	plt.show()



def HeatMap(data, matPlotLib=0, labels=None):

	''' This function may help you generate the heatmap based on the matrix data that argument 'data'
contains. 'data' either can be array itself, or the instance of 'clc.result' class.'''

	if isinstance(data,result):
		# Generate data matrix
		dataSet = numpy.zeros((len(data.stimuli),len(data.stimuli)))
		pairResult = data.eachPairResult
		labels = data.stimuli
		for p in pairResult:
			dataSet[p.pair[0]][p.pair[0]] += p.matching[1][0]
			dataSet[p.pair[0]][p.pair[1]] += p.matching[1][1]
			dataSet[p.pair[1]][p.pair[0]] += p.matching[1][2]
			dataSet[p.pair[1]][p.pair[1]] += p.matching[1][3]
		# Because of data along the diagonal repeated adding process 59 times(2 of 60's combinations), mean value will be calculated.
		for ind in xrange(len(data.stimuli)):
			dataSet[ind][ind] = dataSet[ind][ind]/(len(data.stimuli)-1)

	else:
		dataSet = data
		if labels is None:
			labels = list(xrange(data.shape[0]))

	if matPlotLib == 1:
		try:
			import matplotlib.pyplot as plt
			_useMatplotlib(dataSet, labels)
		except ImportError:
			print "You haven't install 'matplotlib' module in your python! \n"
	else:

		try:
			_usePlotly(dataSet)

		except ImportError:
			try:
				_useMatplotlib(dataSet, labels)

			except ImportError:
				print "You need 'plotly' or 'matplotlib' module installed along with your python!\n"




#define a Computation Liguistic class
class clc():


	def __init__(self,matfile,co_occurCSV,normalized_method='mean'):
		print 'Initializing object...\n'
		self.matFile = matfile
		self.mat = loadmat(matfile)
		self.csvData = self.ReadCSV(co_occurCSV)
		#extract stimuli nouns, semantic feature words and their cooresponding co-occur rate from the csv file.
		self.stimuli = [x[0] for x in self.csvData[1:]]
		self.smtFeature = self.csvData[0][1:]
		self.co_occurMatrix = numpy.array([x[1:] for x in self.csvData[1:]])
		#define the numbers of runs and trials.
		self.trialsNum = self.mat['meta']['ntrials'][0][0][0][0]
		self.NounsNum = len(self.stimuli)
		self.runsNum = self.trialsNum/self.NounsNum
		#creat stimuli index dictionary based on the order in the co-occur rate table(csv file)
		self.wordD = dict([(self.stimuli[i],i+1) for i in xrange(self.NounsNum)])
		#In order to sort the original data matrix, find the stimuli presentation orders for 6 runs
		self.wn = self.mat['info']['word']
		self.wnIndex = [self.wordD[self.wn[0][i][0]] for i in xrange(self.trialsNum)]
		self.indArr = zip(self.wnIndex,self.mat['data'])
		#Sort the data matrix
		self.sortedArr = []
		for i in xrange(6):
			self.sortedArr.extend(sorted(self.indArr[i*self.NounsNum:(i+1)*self.NounsNum],key=itemgetter(0)))
		self.finalArr = numpy.array([x[1] for x in self.sortedArr])
		self.runByVoxel = numpy.reshape(self.finalArr,(self.runsNum,self.NounsNum))
		# regularize the data matrix by averaging the intensity value of each voxel within 6 runs
		self._nor = []
		for voxel in xrange(self.mat['meta']['nvoxels'][0][0][0][0]):
			for stimulus in xrange(self.NounsNum):
				itsList = []
				for run in xrange(self.runsNum):
					itsList.append(self.runByVoxel[run][stimulus][0][voxel])
				if normalized_method=='mean':
					intensity = numpy.mean(itsList)
				elif normalized_method=='medianMean':
					intensity = numpy.mean(itsList[1:-1])
				self._nor.append(intensity)
		self.normalized =numpy.reshape(self._nor,(self.NounsNum,int(self.mat['meta']['nvoxels'][0][0][0][0])),order='F')

		one = numpy.ones((self.NounsNum,1))
		self.co_occurDataAddOne = numpy.append(one,self.co_occurMatrix,1).astype(numpy.float32)




	def ReadCSV(self,csvFile):
		import csv
		whole = []
		f = csv.reader(open(csvFile,'rb'))
		for row in f:
			whole.append(row)
		return whole



	def StabilityScore(self,topNum=500):

		print 'Select top %d voxels using stability score algorithm.\n' %topNum
		# Define the total number of the voxels
		voxelNums = self.mat['meta']['nvoxels'][0][0][0][0]

		# Generate the combinations for pairwise correlations
		comb = list(combinations(xrange(self.runsNum),2))
		scores = []
		for VN in xrange(voxelNums):
			oneVoxel = []
			result = 0
			for runN in xrange(self.runsNum):
				temp = []
				for wordN in xrange(self.NounsNum):
					temp.append(self.runByVoxel[runN][wordN][0][VN])
				oneVoxel.append(temp)
			for pair in comb:
				# compute correlation coefficent for each pair
				ccResult =  numpy.corrcoef(oneVoxel[pair[0]],oneVoxel[pair[1]])
				result += ccResult
			finalScore = result/len(comb)
			scores.append([finalScore[0][1],VN])
			sys.stdout.write("\r%d%% has been processed..." %int(VN*100/(voxelNums-1)))
			sys.stdout.flush()
		top =sorted(scores,reverse=True)
		print '\nDone!\n'
		return top[:topNum]



	def StabilityScoreFormal(self,leaveOutTuple, topNum=500):

		# Define the total number of the voxels
		voxelNums = self.mat['meta']['nvoxels'][0][0][0][0]

		# Generate the combinations for pairwise correlations
		comb = list(combinations(xrange(self.runsNum),2))
		leftRunByVoxel = numpy.delete(self.runByVoxel,leaveOutTuple,1)
		scores = []
		for VN in xrange(voxelNums):
			oneVoxel = []
			result = 0
			for runN in xrange(self.runsNum):
				temp = []
				for wordN in xrange(self.NounsNum-len(leaveOutTuple)):
					temp.append(leftRunByVoxel[runN][wordN][0][VN])
				oneVoxel.append(temp)
			for pair in comb:
				# compute correlation coefficent for each pair
				ccResult =  numpy.corrcoef(oneVoxel[pair[0]],oneVoxel[pair[1]])
				result += ccResult
			finalScore = result/len(comb)
			scores.append([finalScore[0][1],VN])
			sys.stdout.write("\rvoxel selection(%d%%)..." %int(VN*100/(voxelNums-1)))
			sys.stdout.flush()
		top =sorted(scores,reverse=True)
		return top[:topNum]



	def Anova(self,topNum=500):
		print 'Select top %d voxels using ANOVA.\n' %topNum
		# Define the total number of the voxels
		voxelNums = self.mat['meta']['nvoxels'][0][0][0][0]

		result = []
		for VN in xrange(voxelNums):
			oneVoxel = []
			for wordN in xrange(self.NounsNum):
				temp = []
				for runN in xrange(self.runsNum):
					temp.append(self.runByVoxel[runN][wordN][0][VN])
				oneVoxel.append(temp)
			fp=f_oneway(*oneVoxel)
			result.append([fp[1],VN])
			sys.stdout.write("\r%d%% has been processed..." %int(VN*100/(voxelNums-1)))
			sys.stdout.flush()
		result.sort()
		print '\nDone!\n'
		return result[:topNum]



	def AnovaFormal(self,leaveOutTuple,topNum=500):

		# Define the total number of the voxels
		voxelNums = self.mat['meta']['nvoxels'][0][0][0][0]
		leftRunByVoxel = numpy.delete(self.runByVoxel,leaveOutTuple,1)
		result = []
		for VN in xrange(voxelNums):
			oneVoxel = []
			for wordN in xrange(self.NounsNum-len(leaveOutTuple)):
				temp = []
				for runN in xrange(self.runsNum):
					temp.append(leftRunByVoxel[runN][wordN][0][VN])
				oneVoxel.append(temp)
			fp=f_oneway(*oneVoxel)
			result.append([fp[1],VN])
			sys.stdout.write("\rvoxel selection(%d%%)..." %int(VN*100/(voxelNums-1)))
			sys.stdout.flush()
		result.sort()
		return result[:topNum]




	def LearnTheta(self,leaveOutTuple,voxelSelection='stabilityS',regression='ols',voxelNum=500):

		voxelS = self.StabilityScore
		if voxelSelection=='anova':
			voxelS = self.Anova
		topVoxel = [x[1] for x in voxelS(topNum=voxelNum)]
		xVar = self.co_occurDataAddOne
		voxItsMat = self.normalized
		xVar = numpy.delete(xVar,leaveOutTuple,0)
		if regression == 'QR':
			q,r = numpy.linalg.qr(xVar)
		voxItsMat = numpy.delete(voxItsMat,leaveOutTuple,0)
		thetaSets = []
		for voxel in topVoxel:
			yVar = []
			for stimulus in xrange(self.NounsNum-len(leaveOutTuple)):
				yVar.append(voxItsMat[stimulus][voxel])
			if regression == 'QR':
				thetaSets.append(numpy.dot(numpy.linalg.pinv(r),numpy.dot(q.T,yVar)))
			elif regression == 'ols':
				thetaSets.append(numpy.dot(numpy.linalg.pinv(numpy.dot(xVar.T,xVar)),numpy.dot(xVar.T,yVar)))
		returnResult = result()
		returnResult.topVoxelInd = topVoxel
		returnResult.theta = thetaSets
		return returnResult



	def LearnThetaReg(self,voxelSelection='stabilityS',voxelNum=500):

		voxelS = self.StabilityScore
		if voxelSelection=='anova':
			voxelS = self.Anova
		topVoxel = [x[1] for x in voxelS(topNum=voxelNum)]
		xVar = self.co_occurDataAddOne
		voxItsMat = self.normalized
		#define the dataset for test by choose one stimulous(fixed,not randomly) from each category
		leaveOutTuple = (0,1,2,7,16,19,23,36,43,52,54,55)

		xVar = numpy.delete(xVar,leaveOutTuple,0)
		voxItsMat = numpy.delete(voxItsMat,leaveOutTuple,0)
		lambda4eachVox = []
		lambdaList = [0]
		rest = [float((2**x))/100 for x in xrange(18)]
		lambdaList.extend(rest)
		eye = numpy.eye(26)
		eye[0][0] = 0
		detail = []
		for voxel in topVoxel:
			yVar = []
			thetaOptions = []
			errors = []
			for stimulus in xrange(self.NounsNum-len(leaveOutTuple)):
				yVar.append(voxItsMat[stimulus][voxel])
			for trial in lambdaList:
				thetaOptions.append(numpy.dot(numpy.linalg.pinv(numpy.dot(xVar.T,xVar)+(trial*eye)),numpy.dot(xVar.T,yVar)))
			for option in thetaOptions:
				for i in leaveOutTuple:
					onePredict = []
					oneReal = []
					print i,
					oneReal.append(self.normalized[i][voxel])
					onePredict.append(numpy.dot(self.co_occurDataAddOne[i],option))
				#calculate predicted error sum of squares
				press = list(map(lambda x: (x[0]-x[1])**2, zip(onePredict,oneReal)))
				errors.append(sum(press)/2*(len(leaveOutTuple)))
			lambda4eachVox.append(lambdaList[errors.index(min(errors))])
			detail.append([voxel,thetaOptions,errors])
		returnResult = result()
		returnResult.topVoxelInd = topVoxel
		returnResult.lambda4voxels = lambda4eachVox
		returnResult.details = detail
		return returnResult



	def PredictTomData(self,wordIndexTuple,voxelSelection='stabilityS',regression='ols',voxelNum=500):
		theta = self.LearnTheta(wordIndexTuple,voxelSelection=voxelSelection,regression=regression,voxelNum=voxelNum)
		resultList = []
		for i in wordIndexTuple:
			oneResult = []
			for j in theta.theta:
				oneResult.append(numpy.dot(self.co_occurDataAddOne[i],j))
			resultList.append(oneResult)
		returnList = result()
		returnList.topVoxelInd = theta.topVoxelInd
		returnList.theta = theta.theta
		returnList.wordsIndex = wordIndexTuple
		returnList.voxelValueForWords = resultList
		return returnList


	def _FetchOrigDataRegularized(self,wordIndexTuple,topVoxelInd):
		''' Make sure that the argument 'topVoxelInd'  only contains index number of voxels.'''
		result = []
		if len(wordIndexTuple) > 1:
			for i in wordIndexTuple:
				oneWordRaw = []
				for j in topVoxelInd:
					oneWordRaw.append(self.normalized[i][j])
				result.append(oneWordRaw)

		elif len(wordIndexTuple) == 1:
			ind = wordIndexTuple[0]
			innerList = []
			for z in topVoxelInd:
				innerList.append(self.normalized[ind][z])
			result.append(innerList)

		return result


	def _FetchOneRunOrigData(self,wordIndexTuple,runNum,topVoxelInd):
		''' Make sure that the argument 'topVoxelInd'  only contains index number of voxels.'''
		# fetch data from one particular run
		result = []
		if len(wordIndexTuple) > 1:
			for i in wordIndexTuple:
				midResult = []
				for j in topVoxelInd:
					midResult.append(self.runByVoxel[runNum][i][0][j])
				result.append(midResult)

		elif len(wordIndexTuple) == 1:
			ind = wordIndexTuple[0]
			innerList = []
			for z in topVoxelInd:
				innerList.append(self.runByVoxel[runNum][ind][0][z])
			result.append(innerList)

		return result


	def HeatmapOvsO(self, voxelSelection='stabilityS', voxelNum=500, matPlotLib=0):
		''' 'oVSo' stands for 'observed versus observed', the function will automatically generate the heatmap with participant's observed data.'''
		if voxelSelection=='stabilityS':
			voxelS = self.StabilityScore
		elif voxelSelection=='anova':
			voxelS = self.Anova
		voxelInd = [x[1] for x in voxelS(topNum=voxelNum)]

		mat = numpy.zeros((self.NounsNum,self.NounsNum))
		for i in xrange(self.NounsNum):
			a = self._FetchOrigDataRegularized((i,),voxelInd)
			for j in xrange(self.NounsNum):
				b = self._FetchOrigDataRegularized((j,),voxelInd)
				mat[i][j] = (numpy.dot(a[0],b[0]))/((math.sqrt(numpy.dot(a[0],a[0])))*(math.sqrt(numpy.dot(b[0],b[0]))))

		HeatMap(mat, matPlotLib=matPlotLib, labels=self.stimuli)



	def _CosineSimilarity(self,predict,raw):
		flag = 0
		result = []
		for i in predict:
			for j in raw:
				result.append((numpy.dot(i,j))/((math.sqrt(numpy.dot(i,i)))*(math.sqrt(numpy.dot(j,j)))))
		#resultArr = numpy.reshape(result,(len(predict),len(predict)))
		# Code below only apply for the case for two words pair calculation, for words comparation that more than 2, you should rewrite the code below
		if (result[0]+result[3]) > (result[1]+result[2]):
			flag = 1
		#print result
		#print resultArr.max()
		return [flag,result]


	def _CorrelationSimilarity(self,predict,raw):
		flag = 0
		result = []
		for i in predict:
			for j in raw:
				result.append(numpy.corrcoef(i,j)[0][1])
		# Code below only apply for the case for two words pair calculation, for words comparation that more than 2, you should rewrite the code below
		if (result[0]+result[3]) > (result[1]+result[2]):
			flag = 1
		#print result
		return [flag,result]



	def Match(self,wordIndexTuple,method='cosineS',voxelNum=500):
		predictV = self.PredictTomData(wordIndexTuple,voxelNum)
		predict = predictV.voxelValueForWords
		raw = self._FetchOrigDataRegularized(wordIndexTuple,predictV.topVoxelInd)
		if method == 'cosineS':
			flag = self._CosineSimilarity(predict,raw)
		elif method == 'corrS':
			flag = self._CorrelationSimilarity(predict,raw)
		return flag



	def RunNoRegu(self, voxelSelection='stabilityS', regression='ols', matching='cosineS', voxelNum=500, showDetail=True):
		successNum = 0.0
		total = 1
		if voxelSelection=='stabilityS':
			voxelS = self.StabilityScore
		elif voxelSelection=='anova':
			voxelS = self.Anova
		topVoxel = [x[1] for x in voxelS(topNum=voxelNum)]
		pairSets = list(combinations(xrange(self.NounsNum),2))

		returnList = result()
		returnList.topVoxelInd = topVoxel
		returnList.eachPairResult = []

		for pair in pairSets:
			xVar = self.co_occurDataAddOne
			voxItsMat = self.normalized
			xVar = numpy.delete(xVar,pair,0)
			if regression == 'QR':
				q,r = numpy.linalg.qr(xVar)
			elif regression == 'ols':
				pass
			voxItsMat = numpy.delete(voxItsMat,pair,0)
			thetaSets = []
			for voxel in topVoxel:
				yVar = []
				for stimulus in xrange(self.NounsNum-len(pair)):
					yVar.append(voxItsMat[stimulus][voxel])
				if regression == 'QR':
					thetaSets.append(numpy.dot(numpy.linalg.pinv(r),numpy.dot(q.T,yVar)))
				elif regression == 'ols':
					thetaSets.append(numpy.dot(numpy.linalg.pinv(numpy.dot(xVar.T,xVar)),numpy.dot(xVar.T,yVar)))
			predictTwoWordResults = []
			for i in pair:
				oneResult = []
				for j in thetaSets:
					oneResult.append(numpy.dot(self.co_occurDataAddOne[i],j))
				predictTwoWordResults.append(oneResult)
			rawIntenseData = self._FetchOrigDataRegularized(pair,topVoxel)
			if matching == 'cosineS':
				matchingResult = self._CosineSimilarity(predictTwoWordResults,rawIntenseData)
			elif matching == 'corrS':
				matchingResult = self._CorrelationSimilarity(predictTwoWordResults,rawIntenseData)
			successNum += matchingResult[0]
			total += 1
			if showDetail == False:
				sys.stdout.write("\r%s using %s,%s,%s:%d/%d (success/total)" %(self.matFile,voxelSelection,regression,matching,successNum,total))
				sys.stdout.flush()
			elif showDetail:
				print "Matching for '%s'\t and '%s'\t\t(1:success 0:fail): %d\n" %(self.stimuli[pair[0]],self.stimuli[pair[1]],flag)

			pairwiseResult =  result()
			pairwiseResult.pair = pair
			pairwiseResult.matching = matchingResult
			#pairwiseResult.theta = thetaSets
			#pairwiseResult.predicted = predictTwoWordResults
			returnList.eachPairResult.append(pairwiseResult)
		returnList.stimuli = self.stimuli
		returnList.accuracy = successNum*100/len(pairSets)


		print '\nThe accuracy of model is %f%%\n' %(successNum*100/len(pairSets))
		return returnList



	def RunWithEase(self, voxelSelection='stabilityS', matching='cosineS', voxelNum=500, showDetail=True):

		'''Instead of doing voxel selection and finding optimized lambdas each time of the cross-validation, this 'RunWithEase' function will complete the processes once and for all(using the whole 60 stimuli data) at the very beginning outside the leave-two-out loop. Although this kind of method will probably commit the so-called 'Type III errors' which can be simply considered as using already-known-data predict themselves, we can still use it to test new ideas or implement different approaches for its non-time-consuming advantage. '''

		successNum = 0.0
		total = 0
		voxelS = self.StabilityScore
		if voxelSelection=='anova':
			voxelS = self.Anova
		topVoxel = [x[1] for x in voxelS(topNum=voxelNum)]
		pairSets = list(combinations(xrange(self.NounsNum),2))

		print 'Choosing optimized regularization parameters lambda for each voxel\n'
		##define the dataset for test by choose one stimulous(fixed,not randomly) from each category
		#leaveOutTuple = (0,1,2,7,16,19,23,36,43,52,54,55)
		leaveOutTuple = tuple(sample(xrange(self.NounsNum),int(self.NounsNum*0.3)))
		print 'Left out words for test:\n', map(lambda x: self.stimuli[x], leaveOutTuple)

		x4lambda = self.co_occurDataAddOne
		voxItsMat4lambda = self.normalized
		x4lambda = numpy.delete(x4lambda,leaveOutTuple,0)
		voxItsMat4lambda = numpy.delete(voxItsMat4lambda,leaveOutTuple,0)
		lambda4eachVox = []
		lambdaList = [0]
		rest = [float((2**x))/100 for x in xrange(14)]
		lambdaList.extend(rest)
		# generate a identity matrix for regularization
		eye = numpy.eye(26)
		eye[0][0] = 0

		returnList = result()
		returnList.topVoxelInd = topVoxel
		returnList.eachPairResult = []

		for voxel in topVoxel:
			y4lambda = []
			thetaOptions = []
			errors = []
			for stimulus in xrange(self.NounsNum-len(leaveOutTuple)):
				y4lambda.append(voxItsMat4lambda[stimulus][voxel])
			for trial in lambdaList:
				thetaOptions.append(numpy.dot(numpy.linalg.pinv(numpy.dot(x4lambda.T,x4lambda)+(trial*eye)),numpy.dot(x4lambda.T,y4lambda)))
			for option in thetaOptions:
				for i in leaveOutTuple:
					onePredict = []
					oneReal = []
					oneReal.append(self.normalized[i][voxel])
					onePredict.append(numpy.dot(self.co_occurDataAddOne[i],option))
				#calculate predicted error sum of squares
				press = list(map(lambda x: (x[0]-x[1])**2, zip(onePredict,oneReal)))
				errors.append(sum(press)/2*(len(leaveOutTuple)))
			lambda4eachVox.append(lambdaList[errors.index(min(errors))])
		print '\nDone!\n'

		for pair in pairSets:
			xVar = self.co_occurDataAddOne
			voxItsMat = self.normalized
			xVar = numpy.delete(xVar,pair,0)
			voxItsMat = numpy.delete(voxItsMat,pair,0)
			thetaSets = []
			numV = 0
			for voxel in topVoxel:
				yVar = []
				for stimulus in xrange(self.NounsNum-len(pair)):
					yVar.append(voxItsMat[stimulus][voxel])
				thetaSets.append(numpy.dot(numpy.linalg.pinv(numpy.dot(xVar.T,xVar)+(lambda4eachVox[numV]*eye)),numpy.dot(xVar.T,yVar)))
				numV += 1
			predictTwoWordResults = []
			for i in pair:
				oneResult = []
				for j in thetaSets:
					oneResult.append(numpy.dot(self.co_occurDataAddOne[i],j))
				predictTwoWordResults.append(oneResult)
			rawIntenseData = self._FetchOrigDataRegularized(pair,topVoxel)
			if matching == 'cosineS':
				matchingResult = self._CosineSimilarity(predictTwoWordResults,rawIntenseData)
			elif matching == 'corrS':
				matchingResult = self._CorrelationSimilarity(predictTwoWordResults,rawIntenseData)
			successNum += matchingResult[0]
			total += 1
			if showDetail == False:
				sys.stdout.write("\r%s using %s,OLS,%s:%d/%d (success/total)" %(self.matFile,voxelSelection,matching,successNum,total))
				sys.stdout.flush()
			elif showDetail:
				print "Matching for '%s'\t and '%s'\t\t(1:success 0:fail): %d\n" %(self.stimuli[pair[0]],self.stimuli[pair[1]],matchingResult[0])

			pairwiseResult =  result()
			pairwiseResult.pair = pair
			pairwiseResult.matching = matchingResult
			#pairwiseResult.theta = thetaSets
			#pairwiseResult.predicted = predictTwoWordResults
			returnList.eachPairResult.append(pairwiseResult)
		returnList.stimuli = self.stimuli
		returnList.accuracy = successNum*100/len(pairSets)
		returnList.testItems4Reg = leaveOutTuple

		print '\nThe accuracy of model is %f%%\n' %(successNum*100/len(pairSets))
		return returnList



	def RunCMU(self, voxelSelection='stabilityS', matching='cosineS', voxelNum=500, showDetail=True):

		successNum = 0.0
		total = 0
		# generate a identity matrix for regularization
		eye = numpy.eye(26)
		eye[0][0] = 0
		pairSets = list(combinations(xrange(self.NounsNum),2))

		for pair in pairSets:
			voxelS = self.StabilityScoreFormal
			if voxelSelection=='anova':
				voxelS = self.AnovaFormal
			topVoxel = [x[1] for x in voxelS(pair,topNum=voxelNum)]

			# Randomly choose about 30% of the data sample as the test group, and find the optimized lambdas for each voxel at a session.
			x4lambda = self.co_occurDataAddOne
			voxItsMat4lambda = self.normalized
			population = range(self.NounsNum)
			for i in pair:
				population.remove(i)
			leaveOutTuple = tuple(sample(population,int(len(population)*0.3)))
			x4lambda = numpy.delete(x4lambda,leaveOutTuple+pair,0)
			voxItsMat4lambda = numpy.delete(voxItsMat4lambda,leaveOutTuple+pair,0)
			lambda4eachVox = []
			lambdaList = [0]
			rest = [float((2**x))/100 for x in xrange(12)]
			lambdaList.extend(rest)

			for voxel in topVoxel:
				y4lambda = []
				thetaOptions = []
				errors = []
				for stimulus in xrange(self.NounsNum-len(pair)-len(leaveOutTuple)):
					y4lambda.append(voxItsMat4lambda[stimulus][voxel])
				for trial in lambdaList:
					thetaOptions.append(numpy.dot(numpy.linalg.pinv(numpy.dot(x4lambda.T,x4lambda)+(trial*eye)),numpy.dot(x4lambda.T,y4lambda)))
				for option in thetaOptions:
					for i in leaveOutTuple:
						onePredict = []
						oneReal = []
						oneReal.append(self.normalized[i][voxel])
						onePredict.append(numpy.dot(self.co_occurDataAddOne[i],option))
					#calculate predicted error sum of squares
					press = list(map(lambda x: (x[0]-x[1])**2, zip(onePredict,oneReal)))
					errors.append(sum(press)/2*(len(leaveOutTuple)))
				lambda4eachVox.append(lambdaList[errors.index(min(errors))])



			xVar = self.co_occurDataAddOne
			voxItsMat = self.normalized
			xVar = numpy.delete(xVar,pair,0)
			voxItsMat = numpy.delete(voxItsMat,pair,0)
			thetaSets = []
			numV = 0
			for voxel in topVoxel:
				yVar = []
				for stimulus in xrange(self.NounsNum-len(pair)):
					yVar.append(voxItsMat[stimulus][voxel])
				thetaSets.append(numpy.dot(numpy.linalg.pinv(numpy.dot(xVar.T,xVar)+(lambda4eachVox[numV]*eye)),numpy.dot(xVar.T,yVar)))
				numV += 1
			predictTwoWordResults = []
			for i in pair:
				oneResult = []
				for j in thetaSets:
					oneResult.append(numpy.dot(self.co_occurDataAddOne[i],j))
				predictTwoWordResults.append(oneResult)
			rawIntenseData = self._FetchOrigDataRegularized(pair,topVoxel)
			if matching == 'cosineS':
				flag = self._CosineSimilarity(predictTwoWordResults,rawIntenseData)
			elif matching == 'corrS':
				flag = self._CorrelationSimilarity(predictTwoWordResults,rawIntenseData)
			successNum += flag
			total += 1
			if showDetail == False:
				sys.stdout.write("\r\t\t\t\t%s's accuracy:%d/%d (success/total)" %(self.matFile,successNum,total))
				sys.stdout.flush()
			elif showDetail:
				print "Matching for '%s'\t and '%s'\t\t(1:success 0:fail): %d\n" %(self.stimuli[pair[0]],self.stimuli[pair[1]],flag)



			#print successNum

		print '\nThe accuracy of model is %f%%\n' %(successNum*100/len(pairSets))


if __name__ == '__main__':
	# test client
	start = clc('/home/akamalab/Desktop/CLT_wangzheng/scienceParticipentData/data-science-P3.mat','/home/akamalab/Desktop/CLT_wangzheng/scienceParticipentData/co_occurrenceTable.csv')
	result = start.run()
