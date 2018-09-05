__author__ = "Jason Tam"
#import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
#plt.ion() # Interactive Plots
#plt.interactive(True)
import numpy as np
import math
import time
import pytz
import pandas as pd
import datetime as dt
from pandasql import sqldf
import seaborn as sns


###################################################################
###################################################################
###################################################################
###################################################################

class NOxCalibration():

###################################################################
###################################################################

    def __init__(self, inputFile):
        
        self.runAnalysis(inputFile)
        
        return
    
###################################################################
###################################################################

    def runAnalysis(self, inputFile):
    
        print("Running Analysis....")
        
        # Load Gas data
        DF_RAW_Input = pd.read_csv(inputFile, sep=',')#, low_memory=False)#skiprows=[0], 
        self.DF_RAW_Input = DF_RAW_Input.dropna()
        self.DF_RAW = self.DF_RAW_Input.copy()
        
        # Extract Time information
        self.DF_RAW['dateTimeObj'] = self.DF_RAW['Epoch'].apply(lambda x: self.epochToDTObj(x))
        self.DF_RAW['dateString'] = self.DF_RAW['dateTimeObj'].apply(lambda x: self.dateTimeObjToString(x, unit='Date'))
        self.DF_RAW['hourString'] = self.DF_RAW['dateTimeObj'].apply(lambda x: self.dateTimeObjToString(x, unit='Hour'))
        self.DF_RAW['minString'] = self.DF_RAW['dateTimeObj'].apply(lambda x: self.dateTimeObjToString(x, unit='Min'))

        # Compute daily mean and Max for determining Span cycle times
        self.DF_RAW['dailyMean'] = self.DF_RAW.groupby(['dateString'])['NO'].transform('mean')
        
        DF_RawData = self.DF_RAW[['Epoch', 'dateTimeObj', 'dateString', 'hourString', 'minString', 'NO', 'NO2', 'NOX', 'dailyMean']]
        
        # Extract Span Calibration Cycles
        spanCycleStart_dataThreshold = []
        spanMaxTime = ''
        spanCycleEnd_dataThreshold = []
        isInCycle = False
        
        # Find times of data that are greater than 200
        for index, row in self.DF_RAW.iterrows():
            if row['NO'] > 200:
                if isInCycle == False:
                    spanCycleStart_dataThreshold.append(row['dateTimeObj'])
                isInCycle = True
            else:
                if isInCycle == True:
                    spanCycleEnd_dataThreshold.append(row['dateTimeObj'])
                isInCycle = False
                
        # Drop the time periods that are shorter than 20 min
        spanCycleStart_timeThreshold = []
        spanCycleEnd_timeThreshold = []
                
        for i in range(0, len(spanCycleStart_dataThreshold)):
            minDiff = (spanCycleEnd_dataThreshold[i] - spanCycleStart_dataThreshold[i]).total_seconds() / 60.0
            if minDiff >= 20:
                spanCycleStart_timeThreshold.append(spanCycleStart_dataThreshold[i])
                spanCycleEnd_timeThreshold.append(spanCycleEnd_dataThreshold[i])
            
        spanCycle_DataTimeThreshold = pd.DataFrame({'spanCycleStart_timeThreshold':spanCycleStart_timeThreshold, 'spanCycleEnd_timeThreshold':spanCycleEnd_timeThreshold}) 
        
        query = """
        SELECT
            DF_RawData.dateTimeObj AS dateTimeObj
            , DF_RawData.Epoch AS Epoch
            , DF_RawData.dateString AS dateString
            , DF_RawData.hourString AS hourString
            , DF_RawData.minString AS minString
            , DF_RawData.NO AS NO
            , DF_RawData.NO2 AS NO2
            , DF_RawData.NOX AS NOX
            , DF_RawData.dailyMean AS dailyMean
            , spanCycle_DataTimeThreshold.spanCycleStart_timeThreshold AS spanCycleStart_timeThreshold
            , spanCycle_DataTimeThreshold.spanCycleEnd_timeThreshold AS spanCycleEnd_timeThreshold
        FROM
            DF_RawData
        LEFT OUTER JOIN spanCycle_DataTimeThreshold
            ON DF_RawData.dateTimeObj > spanCycle_DataTimeThreshold.spanCycleStart_timeThreshold AND DF_RawData.dateTimeObj < spanCycle_DataTimeThreshold.spanCycleEnd_timeThreshold
        ORDER BY
            DF_RawData.dateTimeObj;
        """

        DF_QueryResult = sqldf(query, locals())
        
        DF_QueryResult['SpanCycleMax'] = DF_QueryResult.groupby(['spanCycleStart_timeThreshold'])['NO'].transform('max')
        
        # Get Time of daily max value
        DF_QueryResult['MaxValue'] = DF_QueryResult['NO'].where((DF_QueryResult['SpanCycleMax'] == DF_QueryResult['NO']) & (DF_QueryResult['SpanCycleMax'] > 200))
        DF_QueryResult.at[DF_QueryResult.duplicated(subset=['spanCycleStart_timeThreshold','MaxValue'],keep='last'), 'MaxValue'] = ''
        DF_QueryResult['MaxTime'] = DF_QueryResult['dateTimeObj'].where((DF_QueryResult['SpanCycleMax'] == DF_QueryResult['NO']) & (DF_QueryResult['SpanCycleMax'] > 200) & (DF_QueryResult['MaxValue'] != ''))
        
        DF_MaxTime_GB = DF_QueryResult.groupby(['MaxValue','MaxTime'], as_index=False).count()
        DF_MaxTime = DF_MaxTime_GB[['MaxValue','MaxTime']]
        
        DF_FindZero = DF_QueryResult[::-1]
        spanCycleStart_timeThreshold_index = len(spanCycleStart_timeThreshold) - 1
        
        zeroVal = []
        zeroValTimes = []
        
        counter = 0

        # Find times of data that are greater than 200
        for index, row in DF_FindZero.iterrows():
            spanCycleStartTime = spanCycleStart_timeThreshold[spanCycleStart_timeThreshold_index]
            
            if counter > 0 and index > 0:
                dateTimeObj = self.epochToDTObj(row['Epoch'])
                if dateTimeObj < spanCycleStartTime:
                    previousVal = DF_FindZero.at[index+1,'NO']
                    nextVal = DF_FindZero.at[index-1,'NO']
                    if row['NO'] < previousVal and row['NO'] < nextVal and row['NO'] < row['dailyMean']:
                        zeroValTimes.append(dateTimeObj)
                        zeroVal.append(row['NO'])
                        if spanCycleStart_timeThreshold_index == 0:
                            break
                        else:
                            spanCycleStart_timeThreshold_index = spanCycleStart_timeThreshold_index - 1
            
            counter = counter + 1
            
        DF_zeroVal = pd.DataFrame({'zeroValTimes':zeroValTimes, 'zeroVal':zeroVal})
        
        DF_QueryResult['dateTimeObj'] = DF_QueryResult['Epoch'].apply(lambda x: self.epochToDTObj(x))
        
        DF_zeroVal_Join = pd.merge(DF_QueryResult, DF_zeroVal, left_on='dateTimeObj', right_on='zeroValTimes', how='left', sort=False)
        
        spanEndTimes = []
        spanCycleStart_timeThreshold_index = 0
        
        # Find times of data that are greater than 300
        for index, row in DF_zeroVal_Join.iterrows():
            spanCycleStartTime = spanCycleStart_timeThreshold[spanCycleStart_timeThreshold_index]
            if index < len(DF_zeroVal_Join.index)-4:
                dateTimeObj = self.epochToDTObj(row['Epoch'])
                if dateTimeObj > spanCycleStartTime:
                    nextTwoVal = DF_FindZero.at[index+2,'NO']
                    nextThreeVal = DF_FindZero.at[index+3,'NO']
                    if row['NO'] > 300:
                        if nextTwoVal/row['NO'] < 0.2:

                            if nextThreeVal < row['dailyMean']:
                                spanEndTimes.append(self.epochToDTObj(DF_FindZero.at[index+3,'Epoch']))
                                if spanCycleStart_timeThreshold_index == len(spanCycleStart_timeThreshold)-1:
                                    break
                                else:
                                    spanCycleStart_timeThreshold_index = spanCycleStart_timeThreshold_index + 1
            
        DF_SpanEndTimes = pd.DataFrame({'spanEndTimes':spanEndTimes})
        DF_zeroVal_Join = pd.merge(DF_zeroVal_Join, DF_SpanEndTimes, left_on='dateTimeObj', right_on='spanEndTimes', how='left', sort=False)
        DF_zeroVal_Join['spanTarget'] = DF_zeroVal_Join['MaxValue'].apply(lambda x: 400 if (isinstance(x, float)) and (float(x) > 350) else '')
        
        self.DF_RawData = DF_zeroVal_Join[['dateTimeObj', 'dateString', 'hourString', 'minString', 'NO', 'NO2', 'NOX']]
        
        self.DF_RawData.to_csv('test.csv', sep=',')
        
        zeroTimeArray = []
        zeroValArray = []
        zeroArray = []
        
        for index, row in DF_zeroVal.iloc[::-1].iterrows():
            zeroTime = DF_zeroVal.at[index,'zeroValTimes']
            zeroVal = DF_zeroVal.at[index,'zeroVal']
            lineArray = [zeroTime, zeroVal]
            zeroArray.append(lineArray)
            zeroTimeArray.append(zeroTime)
            zeroValArray.append(zeroVal)
            
        DF_zeroArray = pd.DataFrame({'zeroValTimes':zeroTimeArray, 'zeroVal':zeroValArray})
        DF_SpanZero = pd.concat([DF_zeroArray, DF_SpanEndTimes], axis=1)

        qry = '''
            SELECT
                DF_SpanZero.*,
                DF_MaxTime.*
            FROM
                DF_SpanZero
            LEFT OUTER JOIN
                DF_MaxTime
            ON
                DF_MaxTime.MaxTime > DF_SpanZero.zeroValTimes and DF_MaxTime.MaxTime < DF_SpanZero.spanEndTimes
            ORDER BY
                DF_SpanZero.zeroValTimes
                
        '''
        
        self.DF_SpanCycleData = sqldf(qry, locals())
        self.DF_SpanCycleData['spanTarget'] = self.DF_SpanCycleData['MaxValue'].apply(lambda x: 400 if (isinstance(x, float)) and (float(x) > 350) else '')

        self.DF_SpanCycleData['spanEndTimes'] = self.DF_SpanCycleData['spanEndTimes'].apply(lambda x: self.unicodeToDTObj(x))
        self.DF_SpanCycleData['zeroValTimes'] = self.DF_SpanCycleData['zeroValTimes'].apply(lambda x: self.unicodeToDTObj(x))
        self.DF_SpanCycleData['MaxTime'] = self.DF_SpanCycleData['MaxTime'].apply(lambda x: self.unicodeToDTObj(x))
        self.DF_SpanCycleData = self.DF_SpanCycleData.rename(columns={'zeroValTimes': 'spanStartTimes', 'MaxValue':'spanVal'})

        return

###################################################################
###################################################################

    def getSpanCycleDF(self):
        return self.DF_SpanCycleData
    
###################################################################
###################################################################

    def getRawDataDF(self):
        return self.DF_RawData

###################################################################
###################################################################

    def getRawDF(self):
        return self.DF_RAW
    
###################################################################
###################################################################

    def dateTimeObjToEpoch(self, dateTimeObj):
        
        localtz = pytz.timezone ("Pacific/Auckland")
        localTime = localtz.localize(dateTimeObj, is_dst=None)
        utcTime = localTime.astimezone (pytz.utc)
        
        epochStart = dt.datetime(1970,1,1, tzinfo=pytz.utc)
        
        EpochTime = (utcTime - epochStart).total_seconds()
        
        return EpochTime
    
###################################################################
###################################################################

    def dateTimeObjToString(self, datetimeObj, unit='Date'):
    
        string = ''
        if unit=='Date':
            string = datetimeObj.strftime('%Y-%m-%d')
        if unit == 'Hour':
            string = datetimeObj.strftime('%H')
        if unit == 'Min':
            string = datetimeObj.strftime('%M')
    
        return string

###################################################################
###################################################################
    
    def epochToDTObj(self,epochInt):
        return dt.datetime.fromtimestamp(epochInt)

###################################################################
###################################################################
    
    def unicodeToDTObj(self,string):
        # Assume the string is in 'YYYY-MM-DD HH:MM:SS.000000' format
        dateTimeString = string.split(".")[0]
        
        return  dt.datetime.strptime(dateTimeString,'%Y-%m-%d %H:%M:%S')
    
###################################################################
###################################################################
    
    def plotData(self,x,y,title,xlabel,ylabel,legendLabel):
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.plot(x,y, label=legendLabel)
        ax.legend(loc='best')
        fig.autofmt_xdate()

        return 
    
###################################################################
###################################################################
###################################################################
###################################################################

if __name__ == "__main__":

    sns.set_style("darkgrid")

    startTime = time.time()
    
    inputFile = 'NOx_Data.dat'

    NOxCalibration(inputFile)
    
    endTime = time.time()
    
    print("Time elapsed: " + repr(endTime-startTime))
    