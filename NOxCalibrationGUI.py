__author__ = "Jason Tam"
import datetime as dt
import time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from os import path
#import xlrd
#import xlwt
import matplotlib.style as sty
from matplotlib.pyplot import cm
from matplotlib.dates import DateFormatter
import seaborn as sns
import pandas as pd
import tkinter
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
from os import walk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from tkinter.filedialog import asksaveasfilename
import numpy as np
plt.ion() # Turning interactive mode on
import sys
from NOxCalibration import NOxCalibration
from pandas.io.parsers import StringIO
from pandasql import sqldf
import math

###################################################################
###################################################################
###################################################################
###################################################################

class NOxCalibrationGUI:
    
    def __init__(self, master):
        self.master = master
        self.master.title("Data Calibration")
        master.geometry("1200x700")
        
        #self.configFilePath = 'filepaths.conf'
        #self.filePaths = self.getFilePaths(self.configFilePath)
        
        # Create top frame box for path inputs
        self.topFrame = tkinter.Frame()

        # Create main frame box for lists and buttons
        self.mainFrame = tkinter.Frame()

        # Create bottom frame box
        self.bottomFrame = tkinter.Frame()
        
        self.nb = ttk.Notebook(self.mainFrame, width=1150, height=640)
        self.tab_DataSource = ttk.Frame(self.nb)   # first tab
        self.tab_NOData = ttk.Frame(self.nb)   # second tab
        self.tab_SpanCycles = ttk.Frame(self.nb)   # third tab
        self.tab_TimeSeries = ttk.Frame(self.nb)   # forth tab
        self.tab_DataValidation = ttk.Frame(self.nb)   # fifth tab

        self.nb.add(self.tab_DataSource, text='Instructions and Data Sources')
        self.nb.add(self.tab_NOData, text='NO Data')
        self.nb.add(self.tab_SpanCycles, text='Span Cycles')
        self.nb.add(self.tab_TimeSeries, text='Time Series')
        self.nb.add(self.tab_DataValidation, text='Data Validation')
        
        ##################################################################
        #### First tab
        ##################################################################
        
        ###### Instructions Box ########

        
        # Add frame for instructions box
        self.F_InsBox = tkinter.Frame(self.tab_DataSource)
        
        # Add scrollbar
        self.instructionsBoxScrollbar = tkinter.Scrollbar(self.F_InsBox)
        self.InsBox_ListTitle = tkinter.Label(self.F_InsBox, text="Instructions")
        self.InsBox_ListTitle.pack(side=tkinter.TOP)
        # Putting the scrollbar on the right
        self.instructionsBoxScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.instructionsBox = tkinter.Text(self.F_InsBox, width=130, height=20)
        self.instructions = """1) Please choose associated input file below this window, and press "Load File".
    - This will populate the list boxes in the next tabs with time periods of data that are to be calibrated.
    - Tabulated results can be saved as a CSV or XLS file through this tab.
    - Please ensure the file extension is entered as part of the file name (Windows)
    - Checkbox options are available if disgarded data is desired in the output file.
2) [NO Data] Upon selecting a calibration period from the box, the other parameter boxes will be populated with assosciated values.
    - The "Default Values" will remain as the values from the input files.
    - The "New Values" can be changed by the user.
    - The "Update" and "Reset" buttons allow the "Applied" value to be switched between the "Default" and New Value".
    - The "Applied Values" will be the ones used for calibration.
3) [Span Cycles] Upon selecting a Span Cycle from the box, the other parameter boxes will be populated with assosciated values.
    - These values are the same as the ones appearing in the [NO Data] tab, and are updated simultaneously from either tabs.
    - Checkboxes are also available to plot the NO2 and NOX data over the span cycle for comparisons.
4) [Time Series] Customized time ranges can be chosen for display to inspect data.
    - All detected Span cycles will be populated in the 'Accepted Span Cycle Periods' box.
    - These can be disgarded using the buttons if they are deemed inapppropriate.
    - Disgarded span cycles can also be added back for analysis using the button provided.
    - Changes to the list of accepted cycle periods are immediately updated in the [NO Data] and [Span Cycles] tab.
5) [Data Validation] Customized time ranges can be chosen for display to inspect data.
    - All loaded data points are flagged as 'Validated' by default
    - A separate validation time range can be chosen to change this validation status.
    - The validation status can be changed via the buttons provided.
    - Each entry of invalidated time ranges will appear in the list box, it does not matter if they over lap.
    - Checkboxes are available to display the validation status of the data in the chosen display time range.
    - Entries of invalidated time range can be removed via the button, the invalidated status will only apply to the data in the absolute time range from all entries.
    - Please note that invalidating data over a span cycle on this tab will not exclude the span cycle being used for calibration, they are handled independently.
    
    
Author: Jason Tam
"""
        self.instructionsBox.insert(tkinter.INSERT, self.instructions)
        self.instructionsBox.config(state=tkinter.DISABLED)
        self.instructionsBox.bind("<1>", lambda event: self.instructionsBox.focus_set())
        self.instructionsBox.pack()
        
        # Linking between the scollbar and the list box
        self.instructionsBoxScrollbar['command'] = self.instructionsBox.yview
        self.instructionsBox['yscrollcommand'] = self.instructionsBoxScrollbar.set
        
        self.F_InsBox.pack(side=tkinter.TOP)
        
        # Add frame for path to raw data file
        self.F_RawData = tkinter.Frame(self.tab_DataSource)
        self.rawFilePathBox = tkinter.Entry(self.F_RawData, width=80)
        #self.addFilePathBox(self.F_RawData, self.rawFilePathBox, "Path to Raw data file", self.filePaths['RAWDATAFILE'])
        self.addFilePathBox(self.F_RawData, self.rawFilePathBox, "Path to Raw data file", '')

        # Add frame for Update Raw Files list button
        self.F_loadFileButton = tkinter.Frame(self.F_RawData)

        # Define button for updating the raw files list
        self.loadFileBut = tkinter.Button(self.F_loadFileButton, text="Load File", fg="blue", command=lambda: self.loadAllFiles())

        # Adding the update files button to the GUI
        self.loadFileBut.pack(side=tkinter.TOP, expand=tkinter.YES)
        
        self.F_loadFileButton.pack(side=tkinter.LEFT)
        
        # Add frame for saving components
        
        ###################################################
        
        # Add frame for path to save results file
        self.F_OutputFile = tkinter.Frame(self.tab_DataSource)
        self.outputFilePathBox = tkinter.Entry(self.F_OutputFile, width=80)
        
        self.addFilePathBox(self.F_OutputFile, self.outputFilePathBox, "Path to results CSV file",'','save','CSV')
        
        self.F_saveOptions = tkinter.Frame(self.tab_DataSource)

        ############# Save Option Checkboxes ################
        
        self.F_SaveResult_CheckBoxes = tkinter.Frame(self.F_saveOptions)
        
        self.SaveResult_Check_InvalidatedData = tkinter.IntVar()
        self.SaveResult_Check_InvalidatedDataBox = tkinter.Checkbutton(self.F_SaveResult_CheckBoxes, text="Invalidated Data", fg="red", variable=self.SaveResult_Check_InvalidatedData)

        self.SaveResult_Check_InvalidatedDataBox.pack(side=tkinter.LEFT)

        self.F_SaveResult_CheckBoxes.pack(side=tkinter.LEFT)
        
        # Add frame for save results file button
        self.F_saveFileButton = tkinter.Frame(self.F_saveOptions)

        # Define button for save results file
        self.saveCSVFileBut = tkinter.Button(self.F_saveFileButton, text="Save results to CSV file", fg="green", command=lambda: self.saveToFile(self.outputFilePathBox, 'DataCSV'))

        # Adding the save results file button to the GUI
        self.saveCSVFileBut.pack(side=tkinter.TOP, expand=tkinter.YES)

        self.F_saveFileButton.pack(side=tkinter.LEFT)
        self.F_saveOptions.pack()#side=tkinter.LEFT)

        ###################################################
        
        # Add frame for path to save results file
        self.F_OutputSpanDataFile = tkinter.Frame(self.tab_DataSource)
        self.outputSpanDataFilePathBox = tkinter.Entry(self.F_OutputSpanDataFile, width=80)
        
        self.addFilePathBox(self.F_OutputSpanDataFile, self.outputSpanDataFilePathBox, "Path to Span Cycle Data CSV file",'','save','CSV')
        
        self.F_spanDataSaveOptions = tkinter.Frame(self.tab_DataSource)
        
        # Save Options checkboxes for output Span file
        self.F_SpanSaveResult_CheckBoxes = tkinter.Frame(self.F_spanDataSaveOptions)
        
        self.SpanSaveResult_Check_DisgardedSpanCycle = tkinter.IntVar()
        self.SpanSaveResult_Check_DisgardedSpanCycleBox = tkinter.Checkbutton(self.F_SpanSaveResult_CheckBoxes, text="Disgarded Span Cycles", fg="red", variable=self.SpanSaveResult_Check_DisgardedSpanCycle)
        
        self.SpanSaveResult_Check_DisgardedSpanCycleBox.pack(side=tkinter.LEFT)
        
        self.F_SpanSaveResult_CheckBoxes.pack(side=tkinter.LEFT)
        
        # Add frame for save results file button
        self.F_saveSpanDataFileButton = tkinter.Frame(self.F_spanDataSaveOptions)

        # Define button for save results file
        self.saveSpanDataCSVFileBut = tkinter.Button(self.F_saveSpanDataFileButton, text="Save Span cycle data to CSV file", fg="green", command=lambda: self.saveToFile(self.outputSpanDataFilePathBox, 'SpanCSV'))

        # Adding the save results file button to the GUI
        self.saveSpanDataCSVFileBut.pack(side=tkinter.TOP, expand=tkinter.YES)

        self.F_saveSpanDataFileButton.pack(side=tkinter.LEFT)
        self.F_spanDataSaveOptions.pack()#side=tkinter.LEFT)
        
        ###################################################
        
        # Add frame for path to save XLS file
        self.F_OutputXLSDataFile = tkinter.Frame(self.tab_DataSource)
        self.outputXLSDataFilePathBox = tkinter.Entry(self.F_OutputXLSDataFile, width=80)
        
        self.addFilePathBox(self.F_OutputXLSDataFile, self.outputXLSDataFilePathBox, "Path to XLS file",'','save', 'XLS')
        
        self.F_XLSDataSaveOptions = tkinter.Frame(self.tab_DataSource)
        
        # Save Options checkboxes for output XLS file
        self.F_XLSSaveResult_CheckBoxes = tkinter.Frame(self.F_XLSDataSaveOptions)
        
        self.XLSSaveResult_Check_InvalidatedData = tkinter.IntVar()
        self.XLSSaveResult_Check_InvalidatedDataBox = tkinter.Checkbutton(self.F_XLSSaveResult_CheckBoxes, text="Invalidated Data", fg="red", variable=self.XLSSaveResult_Check_InvalidatedData)
        self.XLSSaveResult_Check_DisgardedSpanCycle = tkinter.IntVar()
        self.XLSSaveResult_Check_DisgardedSpanCycleBox = tkinter.Checkbutton(self.F_XLSSaveResult_CheckBoxes, text="Disgarded Span Cycles", fg="red", variable=self.XLSSaveResult_Check_DisgardedSpanCycle)
        
        self.XLSSaveResult_Check_InvalidatedDataBox.pack(side=tkinter.LEFT)
        self.XLSSaveResult_Check_DisgardedSpanCycleBox.pack(side=tkinter.LEFT)
        
        self.F_XLSSaveResult_CheckBoxes.pack(side=tkinter.LEFT)
        
        # Add frame for save XLS file button
        self.F_saveXLSDataFileButton = tkinter.Frame(self.F_XLSDataSaveOptions)

        # Define button for save XLS file
        self.saveXLSDataCSVFileBut = tkinter.Button(self.F_saveXLSDataFileButton, text="Save results and Span cycle data to XLS file", fg="green", command=lambda: self.saveToFile(self.outputXLSDataFilePathBox, 'XLS'))

        # Adding the save XLS file button to the GUI
        self.saveXLSDataCSVFileBut.pack(side=tkinter.TOP, expand=tkinter.YES)

        self.F_saveXLSDataFileButton.pack(side=tkinter.LEFT)
        self.F_XLSDataSaveOptions.pack()#side=tkinter.LEFT)
        
        ##################################################################
        #### Second tab
        ##################################################################
        
        self.valueCellWidth = 15
                
        self.F_NODataPlotOpt = tkinter.Frame(self.tab_NOData)
        
        ########### Span and Zero Start Values ############
        
        # Add frame for Span and Zero Values
        self.F_SpanZeroStart = tkinter.Frame(self.F_NODataPlotOpt)

        # Add frame for Span Value
        self.F_SpanTargetStart = tkinter.Frame(self.F_SpanZeroStart)
        
        # Add Frame for SpanTarget Title
        self.F_SpanTargetTitleStart = tkinter.Frame(self.F_SpanTargetStart)
        self.SpanTargetBoxTitleStart = tkinter.Label(self.F_SpanTargetTitleStart, text="Span Target Start Values")
        self.SpanTargetBoxTitleStart.pack()
        self.F_SpanTargetTitleStart.pack(side=tkinter.TOP)
        
        self.F_SpanTargetValuesStart = tkinter.Frame(self.F_SpanTargetStart)
        
        self.F_SpanTargetValDefBoxStart = tkinter.Frame(self.F_SpanTargetValuesStart)
        self.F_SpanTargetValNewBoxStart = tkinter.Frame(self.F_SpanTargetValuesStart)
        self.F_SpanTargetValAppBoxStart = tkinter.Frame(self.F_SpanTargetValuesStart)
        
        self.SpanTargetValDefBoxStart = tkinter.Entry(self.F_SpanTargetValDefBoxStart, width=self.valueCellWidth)
        self.SpanTargetValNewBoxStart = tkinter.Entry(self.F_SpanTargetValNewBoxStart, width=self.valueCellWidth)
        self.SpanTargetValAppBoxStart = tkinter.Entry(self.F_SpanTargetValAppBoxStart, width=self.valueCellWidth)

        self.addParamBox(self.F_SpanTargetValDefBoxStart, self.SpanTargetValDefBoxStart, "Default Start Value", 'blue')
        self.addParamBox(self.F_SpanTargetValNewBoxStart, self.SpanTargetValNewBoxStart, "New Start Value", 'red')
        self.addParamBox(self.F_SpanTargetValAppBoxStart, self.SpanTargetValAppBoxStart, "Applied Start Value", 'green')
        
        self.F_SpanTargetValDefBoxStart.pack(side=tkinter.LEFT)
        self.F_SpanTargetValNewBoxStart.pack(side=tkinter.LEFT)
        self.F_SpanTargetValAppBoxStart.pack(side=tkinter.LEFT)
        self.F_SpanTargetValuesStart.pack()
        self.F_SpanTargetStart.pack()
        
        # Add frame for Span Value
        self.F_SpanStart = tkinter.Frame(self.F_SpanZeroStart)
        
        # Add Frame for Span Title
        self.F_SpanTitleStart = tkinter.Frame(self.F_SpanStart)
        self.SpanBoxTitleStart = tkinter.Label(self.F_SpanTitleStart, text="Span Start Values")
        self.SpanBoxTitleStart.pack()
        self.F_SpanTitleStart.pack(side=tkinter.TOP)
        
        self.F_SpanValuesStart = tkinter.Frame(self.F_SpanStart)
        
        self.F_SpanValDefBoxStart = tkinter.Frame(self.F_SpanValuesStart)
        self.F_SpanValNewBoxStart = tkinter.Frame(self.F_SpanValuesStart)
        self.F_SpanValAppBoxStart = tkinter.Frame(self.F_SpanValuesStart)
        
        self.SpanValDefBoxStart = tkinter.Entry(self.F_SpanValDefBoxStart, width=self.valueCellWidth)
        self.SpanValNewBoxStart = tkinter.Entry(self.F_SpanValNewBoxStart, width=self.valueCellWidth)
        self.SpanValAppBoxStart = tkinter.Entry(self.F_SpanValAppBoxStart, width=self.valueCellWidth)

        self.addParamBox(self.F_SpanValDefBoxStart, self.SpanValDefBoxStart, "Default Start Value", 'blue')
        self.addParamBox(self.F_SpanValNewBoxStart, self.SpanValNewBoxStart, "New Start Value", 'red')
        self.addParamBox(self.F_SpanValAppBoxStart, self.SpanValAppBoxStart, "Applied Start Value", 'green')
        
        self.F_SpanValDefBoxStart.pack(side=tkinter.LEFT)
        self.F_SpanValNewBoxStart.pack(side=tkinter.LEFT)
        self.F_SpanValAppBoxStart.pack(side=tkinter.LEFT)
        self.F_SpanValuesStart.pack()
        self.F_SpanStart.pack()

        # Add frame for Zero Value
        self.F_ZeroStart = tkinter.Frame(self.F_SpanZeroStart)

        # Add Frame for Zero Title
        self.F_ZeroTitleStart = tkinter.Frame(self.F_ZeroStart)
        self.ZeroBoxTitleStart = tkinter.Label(self.F_ZeroTitleStart, text="Zero Start Values")
        self.ZeroBoxTitleStart.pack()
        self.F_ZeroTitleStart.pack(side=tkinter.TOP)
        
        self.F_ZeroValuesStart = tkinter.Frame(self.F_ZeroStart)
        
        self.F_ZeroValDefBoxStart = tkinter.Frame(self.F_ZeroValuesStart)
        self.F_ZeroValNewBoxStart = tkinter.Frame(self.F_ZeroValuesStart)
        self.F_ZeroValAppBoxStart = tkinter.Frame(self.F_ZeroValuesStart)
        
        self.ZeroValDefBoxStart = tkinter.Entry(self.F_ZeroValDefBoxStart, width=self.valueCellWidth)
        self.ZeroValNewBoxStart = tkinter.Entry(self.F_ZeroValNewBoxStart, width=self.valueCellWidth)
        self.ZeroValAppBoxStart = tkinter.Entry(self.F_ZeroValAppBoxStart, width=self.valueCellWidth)
        
        self.addParamBox(self.F_ZeroValDefBoxStart, self.ZeroValDefBoxStart, "Default Start Value", 'blue')
        self.addParamBox(self.F_ZeroValNewBoxStart, self.ZeroValNewBoxStart, "New Start Value", 'red')
        self.addParamBox(self.F_ZeroValAppBoxStart, self.ZeroValAppBoxStart, "Applied Start Value", 'green')
        
        self.F_ZeroValDefBoxStart.pack(side=tkinter.LEFT)
        self.F_ZeroValNewBoxStart.pack(side=tkinter.LEFT)
        self.F_ZeroValAppBoxStart.pack(side=tkinter.LEFT)
        self.F_ZeroValuesStart.pack()
        self.F_ZeroStart.pack()
        
        ########### Button to loadSpan and Zero Values ############
        
        # Add frame for Update Raw Files list button
        self.F_loadSpanZeroButtonStart = tkinter.Frame(self.F_SpanZeroStart)
        
        # Define button for updating the raw files list
        self.updateSpanZeroButStart = tkinter.Button(self.F_loadSpanZeroButtonStart, text="Update Start Parameters", fg="red", command=lambda: self.updateSpanZeroValues('Start'))

        # Adding the update files button to the GUI
        self.updateSpanZeroButStart.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        # Define button for updating the raw files list
        self.resetSpanZeroButStart = tkinter.Button(self.F_loadSpanZeroButtonStart, text="Reset Start Parameters", fg="green", command=lambda: self.updateSpanZeroValues('Start',True))

        # Adding the update files button to the GUI
        self.resetSpanZeroButStart.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        self.F_loadSpanZeroButtonStart.pack()
        
        ###############################################
        
        # Add frame for Uninspected File List
        self.F_Dates = tkinter.Frame(self.F_NODataPlotOpt)
        
        ########### List Box for Periods ############
        
        self.F_DateListBox = tkinter.Frame(self.F_Dates)

        # Add scrollbar
        self.dateListScrollbar = tkinter.Scrollbar(self.F_DateListBox)

        # Add box to list the files
        self.dateListBox = tkinter.Listbox(self.F_DateListBox,width=35, height=10, exportselection=0)
        self.dateListTitle = tkinter.Label(self.F_DateListBox, text="Sampling Dates")
        self.dateListTitle.pack(side=tkinter.TOP)

        # Putting the scrollbar on the right
        self.dateListScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Putting the list box to the left
        self.dateListBox.pack()#side=tkinter.LEFT, fill=tkinter.Y)
        self.F_DateListBox.pack()
        
        # Linking between the scollbar and the list box
        self.dateListScrollbar['command'] = self.dateListBox.yview
        self.dateListBox['yscrollcommand'] = self.dateListScrollbar.set

        # Run function automatically when a selection is made
        self.dateListBox.bind('<<ListboxSelect>>', self.onListBoxSelect)

        ########### Plot Buttons ############
        
        # Add frame for plot button
        self.F_plotButtons = tkinter.Frame(self.F_Dates)
        self.plotButton = tkinter.Button(self.F_plotButtons, text="Plot", command=lambda: self.plotData(self.NOData_canvas,self.NOData_ax))
        self.plotButton.pack(side=tkinter.LEFT)
        
        # Add plot button
        self.popPlotButton = tkinter.Button(self.F_plotButtons, text="Pop-out Plot", command=lambda: self.plotDataPop())
        self.popPlotButton.pack(side=tkinter.LEFT)
        
        # Define button for clearing the selection
        self.dataClearSelBut = tkinter.Button(self.F_plotButtons, text="Clear Selection", fg="blue", command=lambda: self.clearListBoxSelect('Data'))
        self.dataClearSelBut.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        ########### Span and Zero End Values ############
        
        # Add frame for Span and Zero Values
        self.F_SpanZeroEnd = tkinter.Frame(self.F_NODataPlotOpt)

        # Add frame for Span Value
        self.F_SpanTargetEnd = tkinter.Frame(self.F_SpanZeroEnd)
        
        # Add Frame for SpanTarget Title
        self.F_SpanTargetTitleEnd = tkinter.Frame(self.F_SpanTargetEnd)
        self.SpanTargetBoxTitleEnd = tkinter.Label(self.F_SpanTargetTitleEnd, text="Span Target End Values")
        self.SpanTargetBoxTitleEnd.pack()
        self.F_SpanTargetTitleEnd.pack(side=tkinter.TOP)
        
        self.F_SpanTargetValuesEnd = tkinter.Frame(self.F_SpanTargetEnd)
        
        self.F_SpanTargetValDefBoxEnd = tkinter.Frame(self.F_SpanTargetValuesEnd)
        self.F_SpanTargetValNewBoxEnd = tkinter.Frame(self.F_SpanTargetValuesEnd)
        self.F_SpanTargetValAppBoxEnd = tkinter.Frame(self.F_SpanTargetValuesEnd)
        
        self.SpanTargetValDefBoxEnd = tkinter.Entry(self.F_SpanTargetValDefBoxEnd, width=self.valueCellWidth)
        self.SpanTargetValNewBoxEnd = tkinter.Entry(self.F_SpanTargetValNewBoxEnd, width=self.valueCellWidth)
        self.SpanTargetValAppBoxEnd = tkinter.Entry(self.F_SpanTargetValAppBoxEnd, width=self.valueCellWidth)

        self.addParamBox(self.F_SpanTargetValDefBoxEnd, self.SpanTargetValDefBoxEnd, "Default End Value", 'blue')
        self.addParamBox(self.F_SpanTargetValNewBoxEnd, self.SpanTargetValNewBoxEnd, "New End Value", 'red')
        self.addParamBox(self.F_SpanTargetValAppBoxEnd, self.SpanTargetValAppBoxEnd, "Applied End Value", 'green')
        
        self.F_SpanTargetValDefBoxEnd.pack(side=tkinter.LEFT)
        self.F_SpanTargetValNewBoxEnd.pack(side=tkinter.LEFT)
        self.F_SpanTargetValAppBoxEnd.pack(side=tkinter.LEFT)
        self.F_SpanTargetValuesEnd.pack()
        self.F_SpanTargetEnd.pack()
        
        # Add frame for Span Value
        self.F_SpanEnd = tkinter.Frame(self.F_SpanZeroEnd)
        
        # Add Frame for Span Title
        self.F_SpanTitleEnd = tkinter.Frame(self.F_SpanEnd)
        self.SpanBoxTitleEnd = tkinter.Label(self.F_SpanTitleEnd, text="Span End Values")
        self.SpanBoxTitleEnd.pack()
        self.F_SpanTitleEnd.pack(side=tkinter.TOP)
        
        self.F_SpanValuesEnd = tkinter.Frame(self.F_SpanEnd)
        
        self.F_SpanValDefBoxEnd = tkinter.Frame(self.F_SpanValuesEnd)
        self.F_SpanValNewBoxEnd = tkinter.Frame(self.F_SpanValuesEnd)
        self.F_SpanValAppBoxEnd = tkinter.Frame(self.F_SpanValuesEnd)
        
        self.SpanValDefBoxEnd = tkinter.Entry(self.F_SpanValDefBoxEnd, width=self.valueCellWidth)
        self.SpanValNewBoxEnd = tkinter.Entry(self.F_SpanValNewBoxEnd, width=self.valueCellWidth)
        self.SpanValAppBoxEnd = tkinter.Entry(self.F_SpanValAppBoxEnd, width=self.valueCellWidth)
        
        self.addParamBox(self.F_SpanValDefBoxEnd, self.SpanValDefBoxEnd, "Default End Value", 'blue')
        self.addParamBox(self.F_SpanValNewBoxEnd, self.SpanValNewBoxEnd, "New End Value", 'red')
        self.addParamBox(self.F_SpanValAppBoxEnd, self.SpanValAppBoxEnd, "Applied End Value", 'green')
        
        self.F_SpanValDefBoxEnd.pack(side=tkinter.LEFT)
        self.F_SpanValNewBoxEnd.pack(side=tkinter.LEFT)
        self.F_SpanValAppBoxEnd.pack(side=tkinter.LEFT)
        self.F_SpanValuesEnd.pack()
        self.F_SpanEnd.pack()
        

        # Add frame for Zero Value
        self.F_ZeroEnd = tkinter.Frame(self.F_SpanZeroEnd)

        # Add Frame for Zero Title
        self.F_ZeroTitleEnd = tkinter.Frame(self.F_ZeroEnd)
        self.ZeroBoxTitleEnd = tkinter.Label(self.F_ZeroTitleEnd, text="Zero End Values")
        self.ZeroBoxTitleEnd.pack()
        self.F_ZeroTitleEnd.pack(side=tkinter.TOP)
        
        self.F_ZeroValuesEnd = tkinter.Frame(self.F_ZeroEnd)
        
        self.F_ZeroValNewBoxEnd = tkinter.Frame(self.F_ZeroValuesEnd)
        self.F_ZeroValDefBoxEnd = tkinter.Frame(self.F_ZeroValuesEnd)
        self.F_ZeroValAppBoxEnd = tkinter.Frame(self.F_ZeroValuesEnd)
        
        self.ZeroValDefBoxEnd = tkinter.Entry(self.F_ZeroValDefBoxEnd, width=self.valueCellWidth)
        self.ZeroValNewBoxEnd = tkinter.Entry(self.F_ZeroValNewBoxEnd, width=self.valueCellWidth)
        self.ZeroValAppBoxEnd = tkinter.Entry(self.F_ZeroValAppBoxEnd, width=self.valueCellWidth)
        
        self.addParamBox(self.F_ZeroValDefBoxEnd, self.ZeroValDefBoxEnd, "Default End Value", 'blue')
        self.addParamBox(self.F_ZeroValNewBoxEnd, self.ZeroValNewBoxEnd, "New End Value", 'red')
        self.addParamBox(self.F_ZeroValAppBoxEnd, self.ZeroValAppBoxEnd, "Applied End Value", 'green')
        
        self.F_ZeroValDefBoxEnd.pack(side=tkinter.LEFT)
        self.F_ZeroValNewBoxEnd.pack(side=tkinter.LEFT)
        self.F_ZeroValAppBoxEnd.pack(side=tkinter.LEFT)
        self.F_ZeroValuesEnd.pack()
        self.F_ZeroEnd.pack()
        
        ########### Button to load Span and Zero Values ############
        
        # Add frame for Update Raw Files list button
        self.F_loadSpanZeroButtonEnd = tkinter.Frame(self.F_SpanZeroEnd)
        
        # Define button for updating the raw files list
        self.updateSpanZeroButEnd = tkinter.Button(self.F_loadSpanZeroButtonEnd, text="Update End Parameters", fg="red", command=lambda: self.updateSpanZeroValues('End'))

        # Adding the update files button to the GUI
        self.updateSpanZeroButEnd.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        # Define button for updating the raw files list
        self.resetSpanZeroButEnd = tkinter.Button(self.F_loadSpanZeroButtonEnd, text="Reset End Parameters", fg="green", command=lambda: self.updateSpanZeroValues('End',True))

        # Adding the update files button to the GUI
        self.resetSpanZeroButEnd.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        self.F_loadSpanZeroButtonEnd.pack()
        
        ############ Plot ################
        
        # Add frame for plot
        self.F_NOData_plot = tkinter.Frame(self.tab_NOData)
        
        self.NODataFigWidth = 12
        self.NODataFigHeight = 5
        
        self.NOData_fig = Figure(figsize=(self.NODataFigWidth,self.NODataFigHeight), dpi = 100)
        self.NOData_fig_x0 = 0.05
        self.NOData_fig_y0 = 0.2
        self.NOData_fig_x1 = 0.9
        self.NOData_fig_y1 = 0.7
        self.NOData_ax = self.NOData_fig.add_axes([self.NOData_fig_x0,self.NOData_fig_y0,self.NOData_fig_x1,self.NOData_fig_y1])
        self.NOData_canvas = FigureCanvasTkAgg(self.NOData_fig, self.F_NOData_plot)
        self.NOData_canvas.get_tk_widget().pack()
        self.NOData_canvas.draw()
        
        # Pack F_Dates to the left of tab_NOData
        self.F_NODataPlotOpt.pack(side=tkinter.TOP)
        self.F_plotButtons.pack()
        self.F_SpanZeroStart.pack(side=tkinter.LEFT)
        self.F_Dates.pack(side=tkinter.LEFT)#, fill=tkinter.X)
        self.F_SpanZeroEnd.pack(side=tkinter.LEFT)

        self.F_NOData_plot.pack()#side=tkinter.LEFT, fill=tkinter.BOTH)
        
        ##################################################################
        #### Third tab
        ##################################################################

        # Add frame for Span Cycle Plot Options
        self.F_SpanCycleOpt = tkinter.Frame(self.tab_SpanCycles)
        
        # Add frame for listing Span Cycles
        self.F_SpanCycleDates = tkinter.Frame(self.F_SpanCycleOpt)
        
        ########### List Box for Periods ############
        
        self.F_SpanCycleDateListBox = tkinter.Frame(self.F_SpanCycleDates)

        # Add scrollbar
        self.SpanCycleDateListScrollbar = tkinter.Scrollbar(self.F_SpanCycleDateListBox)

        # Add box to list the files
        self.SpanCycleDateListBox = tkinter.Listbox(self.F_SpanCycleDateListBox,width=35, height=10, exportselection=0)
        self.SpanCycleDateListTitle = tkinter.Label(self.F_SpanCycleDateListBox, text="Span Cycle Periods")
        self.SpanCycleDateListTitle.pack(side=tkinter.TOP)

        # Putting the scrollbar on the right
        self.SpanCycleDateListScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Putting the list box to the left
        self.SpanCycleDateListBox.pack()#side=tkinter.LEFT, fill=tkinter.Y)
        self.F_SpanCycleDateListBox.pack()
        
        # Linking between the scollbar and the list box
        self.SpanCycleDateListScrollbar['command'] = self.SpanCycleDateListBox.yview
        self.SpanCycleDateListBox['yscrollcommand'] = self.SpanCycleDateListScrollbar.set

        # Run function automatically when a selection is made
        self.SpanCycleDateListBox.bind('<<ListboxSelect>>', self.onSpanCycleListBoxSelect)
        
        self.F_SpanCycleDates.pack(side=tkinter.LEFT)
        self.F_SpanCycleOpt.pack(side=tkinter.TOP)
        
        ############# Plot Option Checkboxes ################
        
        self.F_SpanCycle_plotOptions = tkinter.Frame(self.F_SpanCycleOpt)
        self.F_SpanCycle_CheckBoxes = tkinter.Frame(self.F_SpanCycle_plotOptions)
        self.SpanCycle_Check_NO = tkinter.IntVar()
        self.SpanCycle_Check_NOBox = tkinter.Checkbutton(self.F_SpanCycle_CheckBoxes, text="NO", variable=self.SpanCycle_Check_NO)
        self.SpanCycle_Check_NO2 = tkinter.IntVar()
        self.SpanCycle_Check_NO2Box = tkinter.Checkbutton(self.F_SpanCycle_CheckBoxes, text="NO2", variable=self.SpanCycle_Check_NO2)
        self.SpanCycle_Check_NOX = tkinter.IntVar()
        self.SpanCycle_Check_NOXBox = tkinter.Checkbutton(self.F_SpanCycle_CheckBoxes, text="NOX", variable=self.SpanCycle_Check_NOX)
        
        self.SpanCycle_Check_NOBox.pack(side=tkinter.LEFT)
        self.SpanCycle_Check_NO2Box.pack(side=tkinter.LEFT)
        self.SpanCycle_Check_NOXBox.pack(side=tkinter.LEFT)
        self.F_SpanCycle_CheckBoxes.pack()

        
        ########### Plot Buttons ############
        
        # Add frame for plot button
        self.F_SpanCyclePlotButtons = tkinter.Frame(self.F_SpanCycle_plotOptions)
        
        # Add plot button
        self.SpanCyclePlotButton = tkinter.Button(self.F_SpanCyclePlotButtons, text="Plot", command=lambda: self.plotSpanData(self.SpanCycle_canvas,self.SpanCycle_ax))
        self.SpanCyclePlotButton.pack(side=tkinter.LEFT)
        
        # Add pop-plot button
        self.SpanCyclePopPlotButton = tkinter.Button(self.F_SpanCyclePlotButtons, text="Pop-out Plot", command=lambda: self.plotSpanDataPop())
        self.SpanCyclePopPlotButton.pack(side=tkinter.LEFT)
        
        # Define button for clearing the selection
        self.SpanCycledataClearSelBut = tkinter.Button(self.F_SpanCyclePlotButtons, text="Clear Selection", fg="blue", command=lambda: self.clearListBoxSelect('Span'))
        self.SpanCycledataClearSelBut.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        self.F_SpanCycle_plotOptions.pack(side=tkinter.LEFT)        
        self.F_SpanCyclePlotButtons.pack()#side=tkinter.LEFT)
        
        ########### Span and Zero Cycle Values ############
        
        # Add frame for Span and Zero Values
        self.F_SpanZeroCycle = tkinter.Frame(self.F_SpanCycleOpt)

        # Add frame for Span Value
        self.F_SpanTargetCycle = tkinter.Frame(self.F_SpanZeroCycle)
        
        # Add Frame for SpanTarget Title
        self.F_SpanTargetTitleCycle = tkinter.Frame(self.F_SpanTargetCycle)
        self.SpanTargetBoxTitleCycle = tkinter.Label(self.F_SpanTargetTitleCycle, text="Span Target Values")
        self.SpanTargetBoxTitleCycle.pack()
        self.F_SpanTargetTitleCycle.pack(side=tkinter.TOP)
        
        self.F_SpanTargetValuesCycle = tkinter.Frame(self.F_SpanTargetCycle)
        
        self.F_SpanTargetValDefBoxCycle = tkinter.Frame(self.F_SpanTargetValuesCycle)
        self.F_SpanTargetValNewBoxCycle = tkinter.Frame(self.F_SpanTargetValuesCycle)
        self.F_SpanTargetValAppBoxCycle = tkinter.Frame(self.F_SpanTargetValuesCycle)
        
        self.SpanTargetValDefBoxCycle = tkinter.Entry(self.F_SpanTargetValDefBoxCycle, width=self.valueCellWidth)
        self.SpanTargetValNewBoxCycle = tkinter.Entry(self.F_SpanTargetValNewBoxCycle, width=self.valueCellWidth)
        self.SpanTargetValAppBoxCycle = tkinter.Entry(self.F_SpanTargetValAppBoxCycle, width=self.valueCellWidth)

        self.addParamBox(self.F_SpanTargetValDefBoxCycle, self.SpanTargetValDefBoxCycle, "Default Value", 'blue')
        self.addParamBox(self.F_SpanTargetValNewBoxCycle, self.SpanTargetValNewBoxCycle, "New Value", 'red')
        self.addParamBox(self.F_SpanTargetValAppBoxCycle, self.SpanTargetValAppBoxCycle, "Applied Value", 'green')
        
        self.F_SpanTargetValDefBoxCycle.pack(side=tkinter.LEFT)
        self.F_SpanTargetValNewBoxCycle.pack(side=tkinter.LEFT)
        self.F_SpanTargetValAppBoxCycle.pack(side=tkinter.LEFT)
        self.F_SpanTargetValuesCycle.pack()
        self.F_SpanTargetCycle.pack()
        
        # Add frame for Span Value
        self.F_SpanCycle = tkinter.Frame(self.F_SpanZeroCycle)
        
        # Add Frame for Span Title
        self.F_SpanTitleCycle = tkinter.Frame(self.F_SpanCycle)
        self.SpanBoxTitleCycle = tkinter.Label(self.F_SpanTitleCycle, text="Span Values")
        self.SpanBoxTitleCycle.pack()
        self.F_SpanTitleCycle.pack(side=tkinter.TOP)
        
        self.F_SpanValuesCycle = tkinter.Frame(self.F_SpanCycle)
        
        self.F_SpanValDefBoxCycle = tkinter.Frame(self.F_SpanValuesCycle)
        self.F_SpanValNewBoxCycle = tkinter.Frame(self.F_SpanValuesCycle)
        self.F_SpanValAppBoxCycle = tkinter.Frame(self.F_SpanValuesCycle)
        
        self.SpanValDefBoxCycle = tkinter.Entry(self.F_SpanValDefBoxCycle, width=self.valueCellWidth)
        self.SpanValNewBoxCycle = tkinter.Entry(self.F_SpanValNewBoxCycle, width=self.valueCellWidth)
        self.SpanValAppBoxCycle = tkinter.Entry(self.F_SpanValAppBoxCycle, width=self.valueCellWidth)
        
        self.addParamBox(self.F_SpanValDefBoxCycle, self.SpanValDefBoxCycle, "Default Value", 'blue')
        self.addParamBox(self.F_SpanValNewBoxCycle, self.SpanValNewBoxCycle, "New Value", 'red')
        self.addParamBox(self.F_SpanValAppBoxCycle, self.SpanValAppBoxCycle, "Applied Value", 'green')
        
        self.F_SpanValDefBoxCycle.pack(side=tkinter.LEFT)
        self.F_SpanValNewBoxCycle.pack(side=tkinter.LEFT)
        self.F_SpanValAppBoxCycle.pack(side=tkinter.LEFT)
        self.F_SpanValuesCycle.pack()
        self.F_SpanCycle.pack()
        

        # Add frame for Zero Value
        self.F_ZeroCycle = tkinter.Frame(self.F_SpanZeroCycle)

        # Add Frame for Zero Title
        self.F_ZeroTitleCycle = tkinter.Frame(self.F_ZeroCycle)
        self.ZeroBoxTitleCycle = tkinter.Label(self.F_ZeroTitleCycle, text="Zero Values")
        self.ZeroBoxTitleCycle.pack()
        self.F_ZeroTitleCycle.pack(side=tkinter.TOP)
        
        self.F_ZeroValuesCycle = tkinter.Frame(self.F_ZeroCycle)
        
        self.F_ZeroValNewBoxCycle = tkinter.Frame(self.F_ZeroValuesCycle)
        self.F_ZeroValDefBoxCycle = tkinter.Frame(self.F_ZeroValuesCycle)
        self.F_ZeroValAppBoxCycle = tkinter.Frame(self.F_ZeroValuesCycle)
        
        self.ZeroValDefBoxCycle = tkinter.Entry(self.F_ZeroValDefBoxCycle, width=self.valueCellWidth)
        self.ZeroValNewBoxCycle = tkinter.Entry(self.F_ZeroValNewBoxCycle, width=self.valueCellWidth)
        self.ZeroValAppBoxCycle = tkinter.Entry(self.F_ZeroValAppBoxCycle, width=self.valueCellWidth)
        
        self.addParamBox(self.F_ZeroValDefBoxCycle, self.ZeroValDefBoxCycle, "Default Value", 'blue')
        self.addParamBox(self.F_ZeroValNewBoxCycle, self.ZeroValNewBoxCycle, "New Value", 'red')
        self.addParamBox(self.F_ZeroValAppBoxCycle, self.ZeroValAppBoxCycle, "Applied Value", 'green')
        
        self.F_ZeroValDefBoxCycle.pack(side=tkinter.LEFT)
        self.F_ZeroValNewBoxCycle.pack(side=tkinter.LEFT)
        self.F_ZeroValAppBoxCycle.pack(side=tkinter.LEFT)
        self.F_ZeroValuesCycle.pack()
        self.F_ZeroCycle.pack()
        
        ########### Button to loadSpan and Zero Values ############
        
        # Add frame for Update Raw Files list button
        self.F_loadSpanZeroButtonCycle = tkinter.Frame(self.F_SpanZeroCycle)
        
        # Define button for updating the raw files list
        self.updateSpanZeroButCycle = tkinter.Button(self.F_loadSpanZeroButtonCycle, text="Update Parameters", fg="red", command=lambda: self.updateSpanZeroValues('Cycle'))

        # Adding the update files button to the GUI
        self.updateSpanZeroButCycle.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        # Define button for updating the raw files list
        self.resetSpanZeroButCycle = tkinter.Button(self.F_loadSpanZeroButtonCycle, text="Reset Parameters", fg="green", command=lambda: self.updateSpanZeroValues('Cycle',True))

        # Adding the update files button to the GUI
        self.resetSpanZeroButCycle.pack(side=tkinter.LEFT, expand=tkinter.YES)
        
        self.F_loadSpanZeroButtonCycle.pack()     
        
        self.F_SpanZeroCycle.pack(side=tkinter.LEFT)
        
        ############ Plot ################
        
        # Add frame for plot
        self.F_SpanCycle_plot = tkinter.Frame(self.tab_SpanCycles)
        self.F_SpanCycle_fig = tkinter.Frame(self.F_SpanCycle_plot)
        
        self.SpanCycleFigWidth = 12
        self.SpanCycleFigHeight = 5
        
        self.SpanCycle_fig = Figure(figsize=(self.SpanCycleFigWidth,self.SpanCycleFigHeight), dpi = 100)
        self.SpanCycle_fig_x0 = 0.05
        self.SpanCycle_fig_y0 = 0.2
        self.SpanCycle_fig_x1 = 0.9
        self.SpanCycle_fig_y1 = 0.7
        self.SpanCycle_ax = self.SpanCycle_fig.add_axes([self.SpanCycle_fig_x0,self.SpanCycle_fig_y0,self.SpanCycle_fig_x1,self.SpanCycle_fig_y1])
        self.SpanCycle_canvas = FigureCanvasTkAgg(self.SpanCycle_fig,self.F_SpanCycle_fig)

        self.SpanCycle_canvas.get_tk_widget().pack()
        self.SpanCycle_canvas.draw()
        
        # Pack F_Dates to the left of tab_NOData

        self.F_SpanCycle_fig.pack()
        self.F_SpanCycle_plot.pack()
        
        ##################################################################
        #### Forth tab
        ##################################################################
        
        # Create frame for start and end dates selection
        self.F_TimeSeriesPlotOpt = tkinter.Frame(self.tab_TimeSeries)
        
        ############# Drop boxes ################
        
        # Create frame for start and end dates selection
        self.F_TS_StartAndEndDates = tkinter.Frame(self.F_TimeSeriesPlotOpt)
        self.startAndEndDateTitle = tkinter.Label(self.F_TS_StartAndEndDates, text="Please choose a time range")
        self.startAndEndDateTitle.pack(side=tkinter.TOP)
        
        self.timeSeriesDropBoxWidth = 10
        
        self.F_TimeSeriesStart = tkinter.Frame(self.F_TS_StartAndEndDates)
        
        # Create frame for start date selection
        self.F_TS_StartDate = tkinter.Frame(self.F_TimeSeriesStart)
        
        self.TS_startDateTitle = tkinter.Label(self.F_TS_StartDate, text="Start Date")
        self.TS_startDateTitle.pack(side=tkinter.TOP)
        
        self.TS_startDateString = tkinter.StringVar(self.F_TS_StartDate)
        self.TS_startDateString.set("") # default value
        self.TS_startDateDropDown = tkinter.OptionMenu(self.F_TS_StartDate, self.TS_startDateString,"")
        self.TS_startDateDropDown.config(width=self.timeSeriesDropBoxWidth)
        
        # Create frame for start hour selection
        self.F_TS_StartHour = tkinter.Frame(self.F_TimeSeriesStart)
        
        self.TS_startHourTitle = tkinter.Label(self.F_TS_StartHour, text="Start Hour")
        self.TS_startHourTitle.pack(side=tkinter.TOP)
        
        self.TS_startHourString = tkinter.StringVar(self.F_TS_StartHour)
        self.TS_startHourString.set("")
        self.TS_startHourDropDown = tkinter.OptionMenu(self.F_TS_StartHour, self.TS_startHourString, "")
        self.TS_startHourDropDown.config(width=self.timeSeriesDropBoxWidth)
        
        # Create frame for start min selection
        self.F_TS_StartMin = tkinter.Frame(self.F_TimeSeriesStart)
        
        self.TS_startMinTitle = tkinter.Label(self.F_TS_StartMin, text="Start Min")
        self.TS_startMinTitle.pack(side=tkinter.TOP)
        
        self.TS_startMinString = tkinter.StringVar(self.F_TS_StartMin)
        self.TS_startMinString.set("")
        self.TS_startMinDropDown = tkinter.OptionMenu(self.F_TS_StartMin, self.TS_startMinString, "")
        self.TS_startMinDropDown.config(width=self.timeSeriesDropBoxWidth)
        
        self.F_TimeSeriesEnd = tkinter.Frame(self.F_TS_StartAndEndDates)
        
        # Create frame for end date selection
        self.F_EndDate = tkinter.Frame(self.F_TimeSeriesEnd)
        
        self.TS_endDateTitle = tkinter.Label(self.F_EndDate, text="End Date")
        self.TS_endDateTitle.pack(side=tkinter.TOP)
        
        self.TS_endDateString = tkinter.StringVar(self.F_EndDate)
        self.TS_endDateString.set("")
        self.TS_endDateDropDown = tkinter.OptionMenu(self.F_EndDate, self.TS_endDateString, "")
        self.TS_endDateDropDown.config(width=self.timeSeriesDropBoxWidth)
        
        # Create frame for end hour selection
        self.F_EndHour = tkinter.Frame(self.F_TimeSeriesEnd)
        
        self.TS_endHourTitle = tkinter.Label(self.F_EndHour, text="End Hour")
        self.TS_endHourTitle.pack(side=tkinter.TOP)
        
        self.TS_endHourString = tkinter.StringVar(self.F_EndHour)
        self.TS_endHourString.set("")
        self.TS_endHourDropDown = tkinter.OptionMenu(self.F_EndHour, self.TS_endHourString, "")
        self.TS_endHourDropDown.config(width=self.timeSeriesDropBoxWidth)
        
        # Create frame for end min selection
        self.F_EndMin = tkinter.Frame(self.F_TimeSeriesEnd)
        
        self.TS_endMinTitle = tkinter.Label(self.F_EndMin, text="End Min")
        self.TS_endMinTitle.pack(side=tkinter.TOP)
        
        self.TS_endMinString = tkinter.StringVar(self.F_EndMin)
        self.TS_endMinString.set("")
        self.TS_endMinDropDown = tkinter.OptionMenu(self.F_EndMin, self.TS_endMinString, "")
        self.TS_endMinDropDown.config(width=self.timeSeriesDropBoxWidth)
        
        self.TS_startDateDropDown.pack()
        self.TS_startHourDropDown.pack()
        self.TS_startMinDropDown.pack()
        self.TS_endDateDropDown.pack()
        self.TS_endHourDropDown.pack()
        self.TS_endMinDropDown.pack()
        
        self.F_TimeSeriesStart.pack()
        self.F_TimeSeriesEnd.pack()
        
        self.F_TS_StartDate.pack(side=tkinter.LEFT)
        self.F_TS_StartHour.pack(side=tkinter.LEFT)
        self.F_TS_StartMin.pack(side=tkinter.LEFT)
        self.F_EndDate.pack(side=tkinter.LEFT)
        self.F_EndHour.pack(side=tkinter.LEFT)
        self.F_EndMin.pack(side=tkinter.LEFT)
        
        self.F_TS_StartAndEndDates.pack(side=tkinter.LEFT)

        ############# Plot Option Checkboxes ################
        
        self.F_TimeSeries_plotOptions = tkinter.Frame(self.F_TS_StartAndEndDates)
        self.F_TimeSeries_CheckBoxes = tkinter.Frame(self.F_TimeSeries_plotOptions)
        self.TS_Check_NO = tkinter.IntVar()
        self.TS_Check_NOBox = tkinter.Checkbutton(self.F_TimeSeries_CheckBoxes, text="NO", variable=self.TS_Check_NO)
        self.TS_Check_NO2 = tkinter.IntVar()
        self.TS_Check_NO2Box = tkinter.Checkbutton(self.F_TimeSeries_CheckBoxes, text="NO2", variable=self.TS_Check_NO2)
        self.TS_Check_NOX = tkinter.IntVar()
        self.TS_Check_NOXBox = tkinter.Checkbutton(self.F_TimeSeries_CheckBoxes, text="NOX", variable=self.TS_Check_NOX)
        self.TS_Check_AcceptedSpanCycles = tkinter.IntVar()
        self.TS_Check_AcceptedSpanCyclesBox = tkinter.Checkbutton(self.F_TimeSeries_CheckBoxes, text="Accepted Cycles", fg="green", variable=self.TS_Check_AcceptedSpanCycles)
        self.TS_Check_RejectedSpanCycles = tkinter.IntVar()
        self.TS_Check_RejectedSpanCyclesBox = tkinter.Checkbutton(self.F_TimeSeries_CheckBoxes, text="Disgarded Cycles", fg="red", variable=self.TS_Check_RejectedSpanCycles)
        
        self.TS_Check_NOBox.pack(side=tkinter.LEFT)
        self.TS_Check_NO2Box.pack(side=tkinter.LEFT)
        self.TS_Check_NOXBox.pack(side=tkinter.LEFT)
        self.TS_Check_AcceptedSpanCyclesBox.pack(side=tkinter.LEFT)
        self.TS_Check_RejectedSpanCyclesBox.pack(side=tkinter.LEFT)
        self.F_TimeSeries_CheckBoxes.pack()
        
        ########### Plot Buttons ############
        
        # Add frame for plot button
        self.F_TimeSeriesPlotButtons = tkinter.Frame(self.F_TimeSeries_plotOptions)
        
        # Add plot button
        self.TimeSeriesPlotButton = tkinter.Button(self.F_TimeSeriesPlotButtons, text="Plot", command=lambda: self.plotTimeSeriesData(self.TimeSeries_canvas,self.TimeSeries_ax, 'TimeSeries'))
        self.TimeSeriesPlotButton.pack(side=tkinter.LEFT)
        
        # Add pop-plot button
        self.TimeSeriesPopPlotButton = tkinter.Button(self.F_TimeSeriesPlotButtons, text="Pop-out Plot", command=lambda: self.plotTimeSeriesDataPop('TimeSeries'))
        self.TimeSeriesPopPlotButton.pack(side=tkinter.LEFT)
        
        self.F_TimeSeriesPlotButtons.pack()#side=tkinter.LEFT)
        self.F_TimeSeries_plotOptions.pack()#side=tkinter.LEFT)
        self.F_TimeSeriesPlotOpt.pack()
        
        # Add frame for listing Span Cycles
        self.F_TS_SpanCycleDates = tkinter.Frame(self.F_TimeSeriesPlotOpt)
        
        ########### List Box for Periods ############
        
        self.F_TS_SpanCycleDateListBox = tkinter.Frame(self.F_TS_SpanCycleDates)

        # Add scrollbar
        self.TS_SpanCycleDateListScrollbar = tkinter.Scrollbar(self.F_TS_SpanCycleDateListBox)

        # Add box to list the files
        self.TS_SpanCycleDateListBox = tkinter.Listbox(self.F_TS_SpanCycleDateListBox,width=35, height=10, exportselection=0)
        self.TS_SpanCycleDateListTitle = tkinter.Label(self.F_TS_SpanCycleDateListBox, text="Accepted Span Cycle Periods")
        self.TS_SpanCycleDateListTitle.pack(side=tkinter.TOP)

        # Putting the scrollbar on the right
        self.TS_SpanCycleDateListScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Putting the list box to the left
        self.TS_SpanCycleDateListBox.pack()#side=tkinter.LEFT, fill=tkinter.Y)
        self.F_TS_SpanCycleDateListBox.pack()
        
        # Linking between the scollbar and the list box
        self.TS_SpanCycleDateListScrollbar['command'] = self.TS_SpanCycleDateListBox.yview
        self.TS_SpanCycleDateListBox['yscrollcommand'] = self.TS_SpanCycleDateListScrollbar.set

        # Run function automatically when a selection is made
        #self.TS_SpanCycleDateListBox.bind('<<ListboxSelect>>', self.onSpanCycleListBoxSelect)
        
        self.F_TS_SpanCycleDates.pack(side=tkinter.LEFT)

        ########### Buttons to keep/disgard Span Cycle Periods ############

        # Add frame for buttons to keep/disgard Span Cycle Periods
        self.F_SpanCycleReview = tkinter.Frame(self.F_TimeSeriesPlotOpt)
        
        # Define button for accepting and rejecting Span Cycle Periods

        self.spanCycleRejectButton = tkinter.Button(self.F_SpanCycleReview,
                                    text="Disgard ->",
                                    fg="red",
                                    command=lambda: self.rejectCycle(self.TS_SpanCycleDateListBox.curselection()))
        self.spanCycleAcceptButton = tkinter.Button(self.F_SpanCycleReview,
                                    text="<- Accept",
                                    fg="green",
                                    command=lambda: self.acceptCycle(self.TS_Dis_SpanCycleDateListBox.curselection()))
        self.spanCycleRejectButton.pack()
        self.spanCycleAcceptButton.pack()
        self.F_SpanCycleReview.pack(side=tkinter.LEFT)
        
        # Add frame for listing Disgarded Span Cycles
        self.F_TS_Dis_SpanCycleDates = tkinter.Frame(self.F_TimeSeriesPlotOpt)
        
        ########### List Box for Disgarded Periods ############
        
        self.F_TS_Dis_SpanCycleDateListBox = tkinter.Frame(self.F_TS_Dis_SpanCycleDates)

        # Add scrollbar
        self.TS_Dis_SpanCycleDateListScrollbar = tkinter.Scrollbar(self.F_TS_Dis_SpanCycleDateListBox)

        # Add box to list the files
        self.TS_Dis_SpanCycleDateListBox = tkinter.Listbox(self.F_TS_Dis_SpanCycleDateListBox,width=35, height=10, exportselection=0)
        self.TS_Dis_SpanCycleDateListTitle = tkinter.Label(self.F_TS_Dis_SpanCycleDateListBox, text="Disgarded Span Cycle Periods")
        self.TS_Dis_SpanCycleDateListTitle.pack(side=tkinter.TOP)

        # Putting the scrollbar on the right
        self.TS_Dis_SpanCycleDateListScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Putting the list box to the left
        self.TS_Dis_SpanCycleDateListBox.pack()#side=tkinter.LEFT, fill=tkinter.Y)
        self.F_TS_Dis_SpanCycleDateListBox.pack()
        
        # Linking between the scollbar and the list box
        self.TS_Dis_SpanCycleDateListScrollbar['command'] = self.TS_Dis_SpanCycleDateListBox.yview
        self.TS_Dis_SpanCycleDateListBox['yscrollcommand'] = self.TS_Dis_SpanCycleDateListScrollbar.set

        # Run function automatically when a selection is made
        #self.TS_Dis_SpanCycleDateListBox.bind('<<ListboxSelect>>', self.onSpanCycleListBoxSelect)
        
        self.F_TS_Dis_SpanCycleDates.pack(side=tkinter.LEFT)
        
        ############ Plot ################
        
        # Add frame for plot
        self.F_TimeSeries_plot = tkinter.Frame(self.tab_TimeSeries)
        self.F_TimeSeries_fig = tkinter.Frame(self.F_TimeSeries_plot)
        
        self.TimeSeriesFigWidth = 12
        self.TimeSeriesFigHeight = 5
        
        self.TimeSeries_fig = Figure(figsize=(self.TimeSeriesFigWidth,self.TimeSeriesFigHeight), dpi = 100)
        self.TimeSeries_fig_x0 = 0.05
        self.TimeSeries_fig_y0 = 0.2
        self.TimeSeries_fig_x1 = 0.9
        self.TimeSeries_fig_y1 = 0.7
        self.TimeSeries_ax = self.TimeSeries_fig.add_axes([self.TimeSeries_fig_x0,self.TimeSeries_fig_y0,self.TimeSeries_fig_x1,self.TimeSeries_fig_y1])
        self.TimeSeries_canvas = FigureCanvasTkAgg(self.TimeSeries_fig,self.F_TimeSeries_fig)

        self.TimeSeries_canvas.get_tk_widget().pack()
        self.TimeSeries_canvas.draw()
        
        # Pack F_Dates to the left of tab_TimeSeries
        self.F_TimeSeries_fig.pack()
        self.F_TimeSeries_plot.pack()
        
        ##################################################################
        #### Fifth tab
        ##################################################################
        
        self.F_DV_Opt = tkinter.Frame(self.tab_DataValidation)
        
        # Create frame for start and end dates selection
        self.F_DV_TimeSeriesPlotOpt = tkinter.Frame(self.F_DV_Opt)
        
        ############# Drop boxes for display ################
        
        self.F_DV_SelectDates = tkinter.Frame(self.F_DV_TimeSeriesPlotOpt)
        
        # Create frame for start and end dates selection
        self.F_DV_StartAndEndDates = tkinter.Frame(self.F_DV_SelectDates)
        self.DV_startAndEndDateTitle = tkinter.Label(self.F_DV_StartAndEndDates, text="Please choose a display time range")
        self.DV_startAndEndDateTitle.pack(side=tkinter.TOP)
        
        self.DV_timeSeriesDropBoxWidth = 10
        
        self.F_DV_TimeSeriesStart = tkinter.Frame(self.F_DV_StartAndEndDates)
        
        # Create frame for start date selection
        self.F_DV_StartDate = tkinter.Frame(self.F_DV_TimeSeriesStart)
        
        self.DV_startDateTitle = tkinter.Label(self.F_DV_StartDate, text="Start Date")
        self.DV_startDateTitle.pack(side=tkinter.TOP)
        
        self.DV_startDateString = tkinter.StringVar(self.F_DV_StartDate)
        self.DV_startDateString.set("") # default value
        self.DV_startDateDropDown = tkinter.OptionMenu(self.F_DV_StartDate, self.DV_startDateString,"")
        self.DV_startDateDropDown.config(width=self.DV_timeSeriesDropBoxWidth)
        
        # Create frame for start hour selection
        self.F_DV_StartHour = tkinter.Frame(self.F_DV_TimeSeriesStart)
        
        self.DV_startHourTitle = tkinter.Label(self.F_DV_StartHour, text="Start Hour")
        self.DV_startHourTitle.pack(side=tkinter.TOP)
        
        self.DV_startHourString = tkinter.StringVar(self.F_DV_StartHour)
        self.DV_startHourString.set("")
        self.DV_startHourDropDown = tkinter.OptionMenu(self.F_DV_StartHour, self.DV_startHourString, "")
        self.DV_startHourDropDown.config(width=self.DV_timeSeriesDropBoxWidth)
        
        # Create frame for start min selection
        self.F_DV_StartMin = tkinter.Frame(self.F_DV_TimeSeriesStart)
        
        self.DV_startMinTitle = tkinter.Label(self.F_DV_StartMin, text="Start Min")
        self.DV_startMinTitle.pack(side=tkinter.TOP)
        
        self.DV_startMinString = tkinter.StringVar(self.F_DV_StartMin)
        self.DV_startMinString.set("")
        self.DV_startMinDropDown = tkinter.OptionMenu(self.F_DV_StartMin, self.DV_startMinString, "")
        self.DV_startMinDropDown.config(width=self.DV_timeSeriesDropBoxWidth)
        
        self.F_DV_TimeSeriesEnd = tkinter.Frame(self.F_DV_StartAndEndDates)
        
        # Create frame for end date selection
        self.F_DV_EndDate = tkinter.Frame(self.F_DV_TimeSeriesEnd)
        
        self.DV_endDateTitle = tkinter.Label(self.F_DV_EndDate, text="End Date")
        self.DV_endDateTitle.pack(side=tkinter.TOP)
        
        self.DV_endDateString = tkinter.StringVar(self.F_DV_EndDate)
        self.DV_endDateString.set("")
        self.DV_endDateDropDown = tkinter.OptionMenu(self.F_DV_EndDate, self.DV_endDateString, "")
        self.DV_endDateDropDown.config(width=self.DV_timeSeriesDropBoxWidth)
        
        # Create frame for end hour selection
        self.F_DV_EndHour = tkinter.Frame(self.F_DV_TimeSeriesEnd)
        
        self.DV_endHourTitle = tkinter.Label(self.F_DV_EndHour, text="End Hour")
        self.DV_endHourTitle.pack(side=tkinter.TOP)
        
        self.DV_endHourString = tkinter.StringVar(self.F_DV_EndHour)
        self.DV_endHourString.set("")
        self.DV_endHourDropDown = tkinter.OptionMenu(self.F_DV_EndHour, self.DV_endHourString, "")
        self.DV_endHourDropDown.config(width=self.DV_timeSeriesDropBoxWidth)
        
        # Create frame for end min selection
        self.F_DV_EndMin = tkinter.Frame(self.F_DV_TimeSeriesEnd)
        
        self.DV_endMinTitle = tkinter.Label(self.F_DV_EndMin, text="End Min")
        self.DV_endMinTitle.pack(side=tkinter.TOP)
        
        self.DV_endMinString = tkinter.StringVar(self.F_DV_EndMin)
        self.DV_endMinString.set("")
        self.DV_endMinDropDown = tkinter.OptionMenu(self.F_DV_EndMin, self.DV_endMinString, "")
        self.DV_endMinDropDown.config(width=self.DV_timeSeriesDropBoxWidth)
        
        self.DV_startDateDropDown.pack()
        self.DV_startHourDropDown.pack()
        self.DV_startMinDropDown.pack()
        self.DV_endDateDropDown.pack()
        self.DV_endHourDropDown.pack()
        self.DV_endMinDropDown.pack()
        
        self.F_DV_TimeSeriesStart.pack()
        self.F_DV_TimeSeriesEnd.pack()
        
        self.F_DV_StartDate.pack(side=tkinter.LEFT)
        self.F_DV_StartHour.pack(side=tkinter.LEFT)
        self.F_DV_StartMin.pack(side=tkinter.LEFT)
        self.F_DV_EndDate.pack(side=tkinter.LEFT)
        self.F_DV_EndHour.pack(side=tkinter.LEFT)
        self.F_DV_EndMin.pack(side=tkinter.LEFT)
        
        self.F_DV_StartAndEndDates.pack(side=tkinter.LEFT)

        ############# Plot Option Checkboxes ################
        
        self.F_DV_TimeSeries_plotOptions = tkinter.Frame(self.F_DV_StartAndEndDates)
        self.F_DV_TimeSeries_CheckBoxes = tkinter.Frame(self.F_DV_TimeSeries_plotOptions)
        
        self.DV_Check_ValidatedData = tkinter.IntVar()
        self.DV_Check_ValidatedDataBox = tkinter.Checkbutton(self.F_DV_TimeSeries_CheckBoxes, text="Validated Data", fg="blue", variable=self.DV_Check_ValidatedData)
        self.DV_Check_InvalidatedData = tkinter.IntVar()
        self.DV_Check_InvalidatedDataBox = tkinter.Checkbutton(self.F_DV_TimeSeries_CheckBoxes, text="Invalidated Data", fg="red", variable=self.DV_Check_InvalidatedData)

        self.DV_Check_ValidatedDataBox.pack(side=tkinter.LEFT)
        self.DV_Check_InvalidatedDataBox.pack(side=tkinter.LEFT)

        self.F_DV_TimeSeries_CheckBoxes.pack()
        
        ########### Plot Buttons ############
        
        # Add frame for plot button
        self.F_DV_TimeSeriesPlotButtons = tkinter.Frame(self.F_DV_TimeSeriesPlotOpt)
        
        # Add plot button
        self.DV_TimeSeriesPlotButton = tkinter.Button(self.F_DV_TimeSeriesPlotButtons, text="Plot", command=lambda: self.plotTimeSeriesData(self.DV_TimeSeries_canvas,self.DV_TimeSeries_ax,'DataValidation'))
        self.DV_TimeSeriesPlotButton.pack(side=tkinter.LEFT)
        
        # Add pop-plot button
        self.DV_TimeSeriesPopPlotButton = tkinter.Button(self.F_DV_TimeSeriesPlotButtons, text="Pop-out Plot", command=lambda: self.plotTimeSeriesDataPop('DataValidation'))
        self.DV_TimeSeriesPopPlotButton.pack(side=tkinter.LEFT)
        

        self.F_DV_TimeSeries_plotOptions.pack()#side=tkinter.LEFT)
        self.F_DV_SelectDates.pack()
        self.F_DV_TimeSeriesPlotButtons.pack()#side=tkinter.LEFT)
        self.F_DV_TimeSeriesPlotOpt.pack(side=tkinter.LEFT)
        self.F_DV_Opt.pack()
        
        ############# Drop boxes for Data Validation ################
        
        # Create frame for start and end dates selection
        self.F_DV_InvData_StartAndEndDates = tkinter.Frame(self.F_DV_SelectDates)
        self.DV_InvData_startAndEndDateTitle = tkinter.Label(self.F_DV_InvData_StartAndEndDates, text="Please choose a time range for validation")
        self.DV_InvData_startAndEndDateTitle.pack(side=tkinter.TOP)
        
        self.DV_InvData_timeSeriesDropBoxWidth = 10
        
        self.F_DV_InvData_TimeSeriesStart = tkinter.Frame(self.F_DV_InvData_StartAndEndDates)
        
        # Create frame for start date selection
        self.F_DV_InvData_StartDate = tkinter.Frame(self.F_DV_InvData_TimeSeriesStart)
        
        self.DV_InvData_startDateTitle = tkinter.Label(self.F_DV_InvData_StartDate, text="Start Date")
        self.DV_InvData_startDateTitle.pack(side=tkinter.TOP)
        
        self.DV_InvData_startDateString = tkinter.StringVar(self.F_DV_InvData_StartDate)
        self.DV_InvData_startDateString.set("") # default value
        self.DV_InvData_startDateDropDown = tkinter.OptionMenu(self.F_DV_InvData_StartDate, self.DV_InvData_startDateString,"")
        self.DV_InvData_startDateDropDown.config(width=self.DV_InvData_timeSeriesDropBoxWidth)
        
        # Create frame for start hour selection
        self.F_DV_InvData_StartHour = tkinter.Frame(self.F_DV_InvData_TimeSeriesStart)
        
        self.DV_InvData_startHourTitle = tkinter.Label(self.F_DV_InvData_StartHour, text="Start Hour")
        self.DV_InvData_startHourTitle.pack(side=tkinter.TOP)
        
        self.DV_InvData_startHourString = tkinter.StringVar(self.F_DV_InvData_StartHour)
        self.DV_InvData_startHourString.set("")
        self.DV_InvData_startHourDropDown = tkinter.OptionMenu(self.F_DV_InvData_StartHour, self.DV_InvData_startHourString, "")
        self.DV_InvData_startHourDropDown.config(width=self.DV_InvData_timeSeriesDropBoxWidth)
        
        # Create frame for start min selection
        self.F_DV_InvData_StartMin = tkinter.Frame(self.F_DV_InvData_TimeSeriesStart)
        
        self.DV_InvData_startMinTitle = tkinter.Label(self.F_DV_InvData_StartMin, text="Start Min")
        self.DV_InvData_startMinTitle.pack(side=tkinter.TOP)
        
        self.DV_InvData_startMinString = tkinter.StringVar(self.F_DV_InvData_StartMin)
        self.DV_InvData_startMinString.set("")
        self.DV_InvData_startMinDropDown = tkinter.OptionMenu(self.F_DV_InvData_StartMin, self.DV_InvData_startMinString, "")
        self.DV_InvData_startMinDropDown.config(width=self.DV_InvData_timeSeriesDropBoxWidth)
        
        self.F_DV_InvData_TimeSeriesEnd = tkinter.Frame(self.F_DV_InvData_StartAndEndDates)
        
        # Create frame for end date selection
        self.F_DV_InvData_EndDate = tkinter.Frame(self.F_DV_InvData_TimeSeriesEnd)
        
        self.DV_InvData_endDateTitle = tkinter.Label(self.F_DV_InvData_EndDate, text="End Date")
        self.DV_InvData_endDateTitle.pack(side=tkinter.TOP)
        
        self.DV_InvData_endDateString = tkinter.StringVar(self.F_DV_InvData_EndDate)
        self.DV_InvData_endDateString.set("")
        self.DV_InvData_endDateDropDown = tkinter.OptionMenu(self.F_DV_InvData_EndDate, self.DV_InvData_endDateString, "")
        self.DV_InvData_endDateDropDown.config(width=self.DV_InvData_timeSeriesDropBoxWidth)
        
        # Create frame for end hour selection
        self.F_DV_InvData_EndHour = tkinter.Frame(self.F_DV_InvData_TimeSeriesEnd)
        
        self.DV_InvData_endHourTitle = tkinter.Label(self.F_DV_InvData_EndHour, text="End Hour")
        self.DV_InvData_endHourTitle.pack(side=tkinter.TOP)
        
        self.DV_InvData_endHourString = tkinter.StringVar(self.F_DV_InvData_EndHour)
        self.DV_InvData_endHourString.set("")
        self.DV_InvData_endHourDropDown = tkinter.OptionMenu(self.F_DV_InvData_EndHour, self.DV_InvData_endHourString, "")
        self.DV_InvData_endHourDropDown.config(width=self.DV_InvData_timeSeriesDropBoxWidth)
        
        # Create frame for end min selection
        self.F_DV_InvData_EndMin = tkinter.Frame(self.F_DV_InvData_TimeSeriesEnd)
        
        self.DV_InvData_endMinTitle = tkinter.Label(self.F_DV_InvData_EndMin, text="End Min")
        self.DV_InvData_endMinTitle.pack(side=tkinter.TOP)
        
        self.DV_InvData_endMinString = tkinter.StringVar(self.F_DV_InvData_EndMin)
        self.DV_InvData_endMinString.set("")
        self.DV_InvData_endMinDropDown = tkinter.OptionMenu(self.F_DV_InvData_EndMin, self.DV_InvData_endMinString, "")
        self.DV_InvData_endMinDropDown.config(width=self.DV_InvData_timeSeriesDropBoxWidth)
        
        self.DV_InvData_startDateDropDown.pack()
        self.DV_InvData_startHourDropDown.pack()
        self.DV_InvData_startMinDropDown.pack()
        self.DV_InvData_endDateDropDown.pack()
        self.DV_InvData_endHourDropDown.pack()
        self.DV_InvData_endMinDropDown.pack()
        
        self.F_DV_InvData_TimeSeriesStart.pack()
        self.F_DV_InvData_TimeSeriesEnd.pack()
        
        self.F_DV_InvData_StartDate.pack(side=tkinter.LEFT)
        self.F_DV_InvData_StartHour.pack(side=tkinter.LEFT)
        self.F_DV_InvData_StartMin.pack(side=tkinter.LEFT)
        self.F_DV_InvData_EndDate.pack(side=tkinter.LEFT)
        self.F_DV_InvData_EndHour.pack(side=tkinter.LEFT)
        self.F_DV_InvData_EndMin.pack(side=tkinter.LEFT)
        
        self.F_DV_InvData_StartAndEndDates.pack(side=tkinter.LEFT)

        ############# Plot Option Checkboxes ################
        
        self.F_DV_InvData_TimeSeries_plotOptions = tkinter.Frame(self.F_DV_InvData_StartAndEndDates)
        self.F_DV_InvData_TimeSeries_CheckBoxes = tkinter.Frame(self.F_DV_InvData_TimeSeries_plotOptions)
        
        self.DV_InvData_Check_ShowRange = tkinter.IntVar()
        self.DV_InvData_Check_ShowRangeBox = tkinter.Checkbutton(self.F_DV_InvData_TimeSeries_CheckBoxes, text="Show range", fg="darkviolet", variable=self.DV_InvData_Check_ShowRange)

        self.DV_InvData_Check_ShowRangeBox.pack(side=tkinter.LEFT)
        self.F_DV_InvData_TimeSeries_plotOptions.pack()
        self.F_DV_InvData_TimeSeries_CheckBoxes.pack()
        
        ########### Buttons to keep/disgard data Periods ############
        
        self.F_DV_actions = tkinter.Frame(self.F_DV_Opt)

        # Add frame for buttons to keep/disgard data Periods
        self.F_DV_dataReview = tkinter.Frame(self.F_DV_actions)
        
        # Define button for validating and invalidating data Periods

        self.DV_dataRejectButton = tkinter.Button(self.F_DV_dataReview,
                                    text="Invalidate ->",
                                    fg="red",
                                    command=lambda: self.invalidateData())
        self.DV_dataAcceptButton = tkinter.Button(self.F_DV_dataReview,
                                    text="<- Validate",
                                    fg="blue",
                                    command=lambda: self.validateData())
        self.DV_dataRejectButton.pack()
        self.DV_dataAcceptButton.pack()
        self.F_DV_dataReview.pack(side=tkinter.LEFT)
        
        # Add frame for listing Invalidated data periods
        self.F_DV_InvDataDates = tkinter.Frame(self.F_DV_actions)
        
        ########### List Box for Invalidated Periods ############
        
        self.F_DV_InvDataDateListBox = tkinter.Frame(self.F_DV_InvDataDates)

        # Add scrollbar
        self.DV_InvDataDateListScrollbar = tkinter.Scrollbar(self.F_DV_InvDataDateListBox)

        # Add box to list the files
        self.DV_InvDataDateListBox = tkinter.Listbox(self.F_DV_InvDataDateListBox,width=35, height=10, exportselection=0)
        self.DV_InvDataDateListTitle = tkinter.Label(self.F_DV_InvDataDateListBox, text="Invalidated Data Periods")
        self.DV_InvDataDateListTitle.pack(side=tkinter.TOP)

        # Putting the scrollbar on the right
        self.DV_InvDataDateListScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Putting the list box to the left
        self.DV_InvDataDateListBox.pack()#side=tkinter.LEFT, fill=tkinter.Y)
        self.F_DV_InvDataDateListBox.pack()
        
        # Linking between the scollbar and the list box
        self.DV_InvDataDateListScrollbar['command'] = self.DV_InvDataDateListBox.yview
        self.DV_InvDataDateListBox['yscrollcommand'] = self.DV_InvDataDateListScrollbar.set

        # Run function automatically when a selection is made
        #self.DV_InvDataDateListBox.bind('<<ListboxSelect>>', self.onSpanCycleListBoxSelect)
        
        self.F_DV_InvDataDates.pack(side=tkinter.LEFT)
        self.F_DV_actions.pack(side=tkinter.LEFT)
        ############ Plot ################
        
        # Add frame for plot
        self.F_DV_TimeSeries_plot = tkinter.Frame(self.tab_DataValidation)
        self.F_DV_TimeSeries_fig = tkinter.Frame(self.F_DV_TimeSeries_plot)
        
        self.DV_TimeSeriesFigWidth = 12
        self.DV_TimeSeriesFigHeight = 5
        
        self.DV_TimeSeries_fig = Figure(figsize=(self.DV_TimeSeriesFigWidth,self.DV_TimeSeriesFigHeight), dpi = 100)
        self.DV_TimeSeries_fig_x0 = 0.05
        self.DV_TimeSeries_fig_y0 = 0.2
        self.DV_TimeSeries_fig_x1 = 0.9
        self.DV_TimeSeries_fig_y1 = 0.7
        self.DV_TimeSeries_ax = self.DV_TimeSeries_fig.add_axes([self.DV_TimeSeries_fig_x0,self.DV_TimeSeries_fig_y0,self.DV_TimeSeries_fig_x1,self.DV_TimeSeries_fig_y1])
        self.DV_TimeSeries_canvas = FigureCanvasTkAgg(self.DV_TimeSeries_fig,self.F_DV_TimeSeries_fig)

        self.DV_TimeSeries_canvas.get_tk_widget().pack()
        self.DV_TimeSeries_canvas.draw()
        
        # Pack F_Dates to the left of tab_DataValidation
        self.F_DV_TimeSeries_fig.pack()
        self.F_DV_TimeSeries_plot.pack()
        
        ##################################################
        
        ##################################################
        
        self.nb.pack()
        self.topFrame.pack()
        self.mainFrame.pack()
        
        self.F_BottomButtons = tkinter.Frame(master)
        self.close_button = tkinter.Button(self.F_BottomButtons, text="Close", command=self.on_closing)
        self.close_button.pack()
        self.F_BottomButtons.pack()

        # Runs on_closing function when close window x button is pressed
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.clearListBoxSelect()
        
        return

###################################################################
###################################################################
    
    def onListBoxSelect(self, evt):
        
        self.loadSpanZeroValues()

        return
    
###################################################################
###################################################################
    
    def onSpanCycleListBoxSelect(self, evt):
        
        self.loadSpanZeroCycleValues()

        return
    
###################################################################
###################################################################
    
    def clearListBoxSelect(self, tab='All'):
        
        
        if tab == 'All' or tab == 'Data':
            self.dateListBox.selection_clear(0, 'end')

            self.NOData_ax.clear()
            self.NOData_canvas.draw()

            self.clearCellValue(self.SpanTargetValDefBoxStart, readOnly=True)
            self.clearCellValue(self.SpanValDefBoxStart, readOnly=True)
            self.clearCellValue(self.ZeroValDefBoxStart, readOnly=True)
            self.clearCellValue(self.SpanTargetValNewBoxStart)
            self.clearCellValue(self.SpanValNewBoxStart)
            self.clearCellValue(self.ZeroValNewBoxStart)
            self.clearCellValue(self.SpanTargetValAppBoxStart, readOnly=True)
            self.clearCellValue(self.SpanValAppBoxStart, readOnly=True)
            self.clearCellValue(self.ZeroValAppBoxStart, readOnly=True)

            self.clearCellValue(self.SpanTargetValDefBoxEnd, readOnly=True)
            self.clearCellValue(self.SpanValDefBoxEnd, readOnly=True)
            self.clearCellValue(self.ZeroValDefBoxEnd, readOnly=True)
            self.clearCellValue(self.SpanTargetValNewBoxEnd)
            self.clearCellValue(self.SpanValNewBoxEnd)
            self.clearCellValue(self.ZeroValNewBoxEnd)
            self.clearCellValue(self.SpanTargetValAppBoxEnd, readOnly=True)
            self.clearCellValue(self.SpanValAppBoxEnd, readOnly=True)
            self.clearCellValue(self.ZeroValAppBoxEnd, readOnly=True)

        if tab == 'All' or tab == 'Span':
            
            self.SpanCycleDateListBox.selection_clear(0, 'end')
            
            self.SpanCycle_ax.clear()
            self.SpanCycle_canvas.draw()
            
            self.clearCellValue(self.SpanTargetValDefBoxCycle, readOnly=True)
            self.clearCellValue(self.SpanValDefBoxCycle, readOnly=True)
            self.clearCellValue(self.ZeroValDefBoxCycle, readOnly=True)
            self.clearCellValue(self.SpanTargetValNewBoxCycle)
            self.clearCellValue(self.SpanValNewBoxCycle)
            self.clearCellValue(self.ZeroValNewBoxCycle)
            self.clearCellValue(self.SpanTargetValAppBoxCycle, readOnly=True)
            self.clearCellValue(self.SpanValAppBoxCycle, readOnly=True)
            self.clearCellValue(self.ZeroValAppBoxCycle, readOnly=True)
        
        return

###################################################################
###################################################################
    
    def clearCellValue(self, box, readOnly=False):
        
        if readOnly == True:
            box.config(state='normal')
            
        box.delete(0, 'end')
            
        if readOnly == True:
            box.config(state='readonly')
        
        return
    
###################################################################
###################################################################

    def getFilePaths(self, configFilePath):
        
        configDict = {}

        with open(configFilePath) as f:
            for line in f:
                if line[0] != '#' :
                    line = line.strip()
                    if line.find(':') != -1 :
                        (key, val) = line.split(':')
                        configDict[key.upper()] = val
        
        return configDict

###################################################################
###################################################################

    def addParamBox(self, subFrame, textBox, label, colour):
        # Add text entry for path to raw data file
        
        textBoxTitle = tkinter.Label(subFrame, text=label, fg=colour)

        # Putting the list box to the left
        textBoxTitle.pack(side=tkinter.TOP)
        textBox.pack()

        subFrame.pack()
        
        return
    
###################################################################
###################################################################

    def addFilePathBox(self, subFrame, textBox, label, filepath='', function='open', option=''):
        # Add text entry for path to raw data file
        #filePathBox = tkinter.Entry(textBox, width=80)
        filePathBoxTitle = tkinter.Label(subFrame, text=label)
        textBox.insert(0, filepath)
        if function=='open':
            filePathBrowseBut = tkinter.Button(subFrame, text="Browse", command=lambda: self.chooseFile(textBox))
        else:
            filePathBrowseBut = tkinter.Button(subFrame, text="Browse", command=lambda: self.chooseSaveFile(textBox, option))

        # Putting the list box to the left
        filePathBoxTitle.pack(side=tkinter.TOP)
        textBox.pack(side=tkinter.LEFT, fill=tkinter.Y)
        filePathBrowseBut.pack(side=tkinter.LEFT, fill=tkinter.Y)
        
        subFrame.pack()
        
        return

###################################################################
###################################################################

    def fillListBoxes(self):
        
        ##### Data Cycles ######

        self.dateListBox.delete(0,self.dateListBox.size()-1)

        self.dataCycleArray = []

        for i in range(1,len(self.spanStartArray)):
            dailyStartDateTimeObj = self.spanEndArray[i-1]
            dailyEndDateTimeObj = self.spanStartArray[i]
            dailyStartDateTimeString = dailyStartDateTimeObj.strftime('%Y-%m-%d %H:%M:%S')
            dailyEndDateTimeString = dailyEndDateTimeObj.strftime('%Y-%m-%d %H:%M:%S')
            self.dataCycleArray.append(dailyStartDateTimeString + " - " + dailyEndDateTimeString)

        for i in range(0,len(self.dataCycleArray)):
            self.dateListBox.insert(tkinter.END, self.dataCycleArray[i])

        ##### Span Cycles ######

        self.SpanCycleDateListBox.delete(0,self.SpanCycleDateListBox.size()-1)
        self.TS_SpanCycleDateListBox.delete(0,self.TS_SpanCycleDateListBox.size()-1)

        self.spanCycleArray = []

        for i in range(0,len(self.spanStartArray)):
            spanStartDateTimeObj = self.spanStartArray[i]
            spanEndDateTimeObj = self.spanEndArray[i]
            spanStartDateTimeString = spanStartDateTimeObj.strftime('%Y-%m-%d %H:%M:%S')
            spanEndDateTimeString = spanEndDateTimeObj.strftime('%Y-%m-%d %H:%M:%S')
            self.spanCycleArray.append(spanStartDateTimeString + " - " + spanEndDateTimeString)

        for i in range(0,len(self.spanCycleArray)):
            self.SpanCycleDateListBox.insert(tkinter.END, self.spanCycleArray[i])
            self.TS_SpanCycleDateListBox.insert(tkinter.END, self.spanCycleArray[i])
        
        return

###################################################################
###################################################################
    
    def loadAllFiles(self):
    
        if self.loadFiles():
            
            loadStartTime = time.time()
            
            self.NOxCalib = NOxCalibration(self.rawDataFileName)
            self.DF_RawData = self.NOxCalib.getRawDataDF()
            self.DF_RawData['validated'] = True
            self.DF_SpanCycle = self.NOxCalib.getSpanCycleDF()
            
            self.DF_SpanCycleNew = self.DF_SpanCycle.copy()
            self.DF_SpanCycleApp = self.DF_SpanCycle.copy()

            self.Def_spanStartArray = list(set(self.DF_SpanCycle['spanStartTimes']))
            self.Def_spanEndArray = list(set(self.DF_SpanCycle['spanEndTimes']))
            
            self.spanStartArray = list(set(self.DF_SpanCycle['spanStartTimes']))
            self.spanEndArray = list(set(self.DF_SpanCycle['spanEndTimes']))
            
            self.spanStartArray.sort()
            self.spanEndArray.sort()
            
            self.fillListBoxes()
                
            # Checking all the plot options
            self.SpanCycle_Check_NOBox.select()
        
            ##### Time Series ######
            
            self.startTime = self.DF_RawData['dateTimeObj'].min()
            self.endTime = self.DF_RawData['dateTimeObj'].max()
            
            self.dateStringArrayAll = self.DF_RawData['dateString'].values
            self.hourStringArrayAll = self.DF_RawData['hourString'].values
            self.minStringArrayAll = self.DF_RawData['minString'].values
            
            self.dateStringArray = list(set(self.dateStringArrayAll))
            self.hourStringArray = list(set(self.hourStringArrayAll))
            self.minStringArray = list(set(self.minStringArrayAll))
            
            self.dateStringArray.sort()
            self.hourStringArray.sort()
            self.minStringArray.sort()
            
            # Clear existing content from dropdown boxes
            self.TS_startDateDropDown["menu"].delete(0, "end")
            self.TS_startHourDropDown["menu"].delete(0, "end")
            self.TS_startMinDropDown["menu"].delete(0, "end")
            self.TS_endDateDropDown["menu"].delete(0, "end")
            self.TS_endHourDropDown["menu"].delete(0, "end")
            self.TS_endMinDropDown["menu"].delete(0, "end")
            
            # Clear plots
            self.TimeSeries_ax.clear()
            self.TimeSeries_canvas.draw()

            # Inserting each date into the date drop down boxes
            for i in range(0, len(self.dateStringArray)):
                dateString = self.dateStringArray[i]
                self.TS_startDateDropDown["menu"].add_command(label=dateString, command=lambda value=dateString: self.TS_startDateString.set(value))
                self.TS_endDateDropDown["menu"].add_command(label=dateString, command=lambda value=dateString: self.TS_endDateString.set(value))
                self.DV_startDateDropDown["menu"].add_command(label=dateString, command=lambda value=dateString: self.DV_startDateString.set(value))
                self.DV_endDateDropDown["menu"].add_command(label=dateString, command=lambda value=dateString: self.DV_endDateString.set(value))
                self.DV_InvData_startDateDropDown["menu"].add_command(label=dateString, command=lambda value=dateString: self.DV_InvData_startDateString.set(value))
                self.DV_InvData_endDateDropDown["menu"].add_command(label=dateString, command=lambda value=dateString: self.DV_InvData_endDateString.set(value))
            
            # Inserting each date into the hour drop down boxes
            for i in range(0, len(self.hourStringArray)):
                hourString = self.hourStringArray[i]
                self.TS_startHourDropDown["menu"].add_command(label=hourString, command=lambda value=hourString: self.TS_startHourString.set(value))
                self.TS_endHourDropDown["menu"].add_command(label=hourString, command=lambda value=hourString: self.TS_endHourString.set(value))
                self.DV_startHourDropDown["menu"].add_command(label=hourString, command=lambda value=hourString: self.DV_startHourString.set(value))
                self.DV_endHourDropDown["menu"].add_command(label=hourString, command=lambda value=hourString: self.DV_endHourString.set(value))
                self.DV_InvData_startHourDropDown["menu"].add_command(label=hourString, command=lambda value=hourString: self.DV_InvData_startHourString.set(value))
                self.DV_InvData_endHourDropDown["menu"].add_command(label=hourString, command=lambda value=hourString: self.DV_InvData_endHourString.set(value))
            
            # Inserting each hour into the Hourly AVG list box
            for i in range(0, len(self.minStringArray)):
                minString = self.minStringArray[i]
                self.TS_startMinDropDown["menu"].add_command(label=minString, command=lambda value=minString: self.TS_startMinString.set(value))
                self.TS_endMinDropDown["menu"].add_command(label=minString, command=lambda value=minString: self.TS_endMinString.set(value))  
                self.DV_startMinDropDown["menu"].add_command(label=minString, command=lambda value=minString: self.DV_startMinString.set(value))
                self.DV_endMinDropDown["menu"].add_command(label=minString, command=lambda value=minString: self.DV_endMinString.set(value))
                self.DV_InvData_startMinDropDown["menu"].add_command(label=minString, command=lambda value=minString: self.DV_InvData_startMinString.set(value))
                self.DV_InvData_endMinDropDown["menu"].add_command(label=minString, command=lambda value=minString: self.DV_InvData_endMinString.set(value))
            
            # Setting default values (first and last) into the time series drop boxes
            startDate = self.dateStringArray[0]
            startHour = self.hourStringArray[0]
            startMin = self.minStringArray[0]
            endDate = self.dateStringArray[len(self.dateStringArray)-1]
            endHour = self.hourStringArray[len(self.hourStringArray)-1]
            endMin = self.minStringArray[len(self.minStringArray)-1]
            
            self.TS_startDateString.set(startDate)
            self.TS_startHourString.set(startHour)
            self.TS_startMinString.set(startMin)
            self.TS_endDateString.set(endDate)
            self.TS_endHourString.set(endHour)
            self.TS_endMinString.set(endMin)
            
            self.DV_startDateString.set(startDate)
            self.DV_startHourString.set(startHour)
            self.DV_startMinString.set(startMin)
            self.DV_endDateString.set(endDate)
            self.DV_endHourString.set(endHour)
            self.DV_endMinString.set(endMin)
            
            self.DV_InvData_startDateString.set(startDate)
            self.DV_InvData_startHourString.set(startHour)
            self.DV_InvData_startMinString.set(startMin)
            self.DV_InvData_endDateString.set(endDate)
            self.DV_InvData_endHourString.set(endHour)
            self.DV_InvData_endMinString.set(endMin)
            
            # Checking some plot options
            self.TS_Check_NOBox.select()
            self.DV_Check_ValidatedDataBox.select()
            
            self.plotTimeSeriesData(self.TimeSeries_canvas,self.TimeSeries_ax,'TimeSeries')
            self.plotTimeSeriesData(self.DV_TimeSeries_canvas,self.DV_TimeSeries_ax,'DataValidation')
            
            loadEndTime = time.time()

            print("Loading time: " + repr(loadEndTime-loadStartTime))
            
            messagebox.showinfo("Load Successful", "Files loaded successfully")
            
        return
    
###################################################################
###################################################################
    
    def loadFiles(self):
        
        if path.exists(self.rawFilePathBox.get()):
            self.rawDataFileName = self.rawFilePathBox.get()
        else:
            messagebox.showinfo("Path Invalid", "Path to raw data file is invalid")
            return False

        return True
    
###################################################################
###################################################################

    def updateSpanZeroValues(self, params, reset=False):
        
        if reset == False:
            self.newSpanTargetValStart = self.SpanTargetValNewBoxStart.get()
            self.newSpanValStart = self.SpanValNewBoxStart.get()
            self.newZeroValStart = self.ZeroValNewBoxStart.get()
            self.newSpanTargetValEnd = self.SpanTargetValNewBoxEnd.get()
            self.newSpanValEnd = self.SpanValNewBoxEnd.get()
            self.newZeroValEnd = self.ZeroValNewBoxEnd.get()
            self.newSpanTargetValCycle = self.SpanTargetValNewBoxCycle.get()
            self.newSpanValCycle = self.SpanValNewBoxCycle.get()
            self.newZeroValCycle = self.ZeroValNewBoxCycle.get()
        else:
            self.newSpanTargetValStart = self.SpanTargetValDefBoxStart.get()
            self.newSpanValStart = self.SpanValDefBoxStart.get()
            self.newZeroValStart = self.ZeroValDefBoxStart.get()
            self.newSpanTargetValEnd = self.SpanTargetValDefBoxEnd.get()
            self.newSpanValEnd = self.SpanValDefBoxEnd.get()
            self.newZeroValEnd = self.ZeroValDefBoxEnd.get()
            self.newSpanTargetValCycle = self.SpanTargetValDefBoxCycle.get()
            self.newSpanValCycle = self.SpanValDefBoxCycle.get()
            self.newZeroValCycle = self.ZeroValDefBoxCycle.get()
        
        dateListBoxindexList = self.dateListBox.curselection()
        
        if len(dateListBoxindexList)>0:
            periodString = self.dateListBox.get(dateListBoxindexList[0])
            startDateTimeString = periodString.split(" - ")[0]
            endDateTimeString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateTimeString,'%Y-%m-%d %H:%M:%S')
            startDateString = startDateTimeString.split(" ")[0]
            endDateTimeObject = dt.datetime.strptime(endDateTimeString,'%Y-%m-%d %H:%M:%S')
            endDateString = endDateTimeString.split(" ")[0]
            
            if reset == False:
                
                if params == 'Start':
                    
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanEndTimes'] == startDateTimeObject),  'spanTarget'] = self.newSpanTargetValStart
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanEndTimes'] == startDateTimeObject),  'spanVal'] = self.newSpanValStart
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanEndTimes'] == startDateTimeObject),  'zeroVal'] = self.newZeroValStart
                    
                if params == 'End':
                    
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == endDateTimeObject),  'spanTarget'] = self.newSpanTargetValEnd
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == endDateTimeObject),  'spanVal'] = self.newSpanValEnd
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == endDateTimeObject),  'zeroVal'] = self.newZeroValEnd
                    
            if params == 'Start':
                
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanEndTimes'] == startDateTimeObject),  'spanTarget'] = self.newSpanTargetValStart
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanEndTimes'] == startDateTimeObject),  'spanVal'] = self.newSpanValStart
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanEndTimes'] == startDateTimeObject),  'zeroVal'] = self.newZeroValStart
                
            if params == 'End':
                
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == endDateTimeObject),  'spanTarget'] = self.newSpanTargetValEnd
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == endDateTimeObject),  'spanVal'] = self.newSpanValEnd
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == endDateTimeObject),  'zeroVal'] = self.newZeroValEnd
            
        spanCycleDateListBoxindexList = self.SpanCycleDateListBox.curselection()
        
        if len(spanCycleDateListBoxindexList)>0:
            periodString = self.SpanCycleDateListBox.get(spanCycleDateListBoxindexList[0])
            startDateTimeString = periodString.split(" - ")[0]
            endDateTimeString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateTimeString,'%Y-%m-%d %H:%M:%S')
            startDateString = startDateTimeString.split(" ")[0]
            endDateTimeObject = dt.datetime.strptime(endDateTimeString,'%Y-%m-%d %H:%M:%S')
            endDateString = endDateTimeString.split(" ")[0]
            
            if reset == False:
                
                if params == 'Cycle':
                    
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleNew['spanEndTimes'] == endDateTimeObject),  'spanTarget'] = self.newSpanTargetValCycle
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleNew['spanEndTimes'] == endDateTimeObject),  'spanVal'] = self.newSpanValCycle
                    self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleNew['spanEndTimes'] == endDateTimeObject),  'zeroVal'] = self.newZeroValCycle        
                    
            if params == 'Cycle':
                
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleApp['spanEndTimes'] == endDateTimeObject),  'spanTarget'] = self.newSpanTargetValCycle
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleApp['spanEndTimes'] == endDateTimeObject),  'spanVal'] = self.newSpanValCycle
                self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleApp['spanEndTimes'] == endDateTimeObject),  'zeroVal'] = self.newZeroValCycle
            
        self.loadSpanZeroValues()
        self.loadSpanZeroCycleValues()
        
        return
    
###################################################################
###################################################################

    def loadSpanZeroCycleValues(self):
        
        spanCycleDateListBoxindexList = self.SpanCycleDateListBox.curselection()
        
        if len(spanCycleDateListBoxindexList)>0:
            periodString = self.SpanCycleDateListBox.get(spanCycleDateListBoxindexList[0])
            startDateTimeString = periodString.split(" - ")[0]
            endDateTimeString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateTimeString,'%Y-%m-%d %H:%M:%S')
            startDateString = startDateTimeString.split(" ")[0]
            endDateTimeObject = dt.datetime.strptime(endDateTimeString,'%Y-%m-%d %H:%M:%S')
            endDateString = endDateTimeString.split(" ")[0]

            spanTargetDefValueCycle = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycle['spanEndTimes'] == endDateTimeObject)]['spanTarget'].values[0]
            spanTargetNewValueCycle = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleNew['spanEndTimes'] == endDateTimeObject)]['spanTarget'].values[0]
            spanTargetAppValueCycle = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleApp['spanEndTimes'] == endDateTimeObject)]['spanTarget'].values[0]
            
            spanDefValueCycle = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycle['spanEndTimes'] == endDateTimeObject)]['spanVal'].values[0]
            spanNewValueCycle = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleNew['spanEndTimes'] == endDateTimeObject)]['spanVal'].values[0]
            spanAppValueCycle = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleApp['spanEndTimes'] == endDateTimeObject)]['spanVal'].values[0]

            zeroDefValueCycle = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycle['spanEndTimes'] == endDateTimeObject)]['zeroVal'].values[0]
            zeroNewValueCycle = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleNew['spanEndTimes'] == endDateTimeObject)]['zeroVal'].values[0]
            zeroAppValueCycle = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycleApp['spanEndTimes'] == endDateTimeObject)]['zeroVal'].values[0]
        
            self.updateCellValue(self.SpanTargetValDefBoxCycle, spanTargetDefValueCycle, readOnly=True)            
            self.updateCellValue(self.SpanValDefBoxCycle, spanDefValueCycle, readOnly=True)
            self.updateCellValue(self.ZeroValDefBoxCycle, zeroDefValueCycle, readOnly=True)
            self.updateCellValue(self.SpanTargetValNewBoxCycle, spanTargetNewValueCycle)
            self.updateCellValue(self.SpanValNewBoxCycle, spanNewValueCycle)
            self.updateCellValue(self.ZeroValNewBoxCycle, zeroNewValueCycle)
            self.updateCellValue(self.SpanTargetValAppBoxCycle, spanTargetAppValueCycle, readOnly=True)
            self.updateCellValue(self.SpanValAppBoxCycle, spanAppValueCycle, readOnly=True)
            self.updateCellValue(self.ZeroValAppBoxCycle, zeroAppValueCycle, readOnly=True)
        
        return

###################################################################
###################################################################
        
    def loadSpanZeroValues(self):
        
        dateListBoxindexList = self.dateListBox.curselection()
        
        if len(dateListBoxindexList)>0:
            periodString = self.dateListBox.get(dateListBoxindexList[0])
            startDateTimeString = periodString.split(" - ")[0]
            endDateTimeString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateTimeString,'%Y-%m-%d %H:%M:%S')
            startDateString = startDateTimeString.split(" ")[0]
            endDateTimeObject = dt.datetime.strptime(endDateTimeString,'%Y-%m-%d %H:%M:%S')
            endDateString = endDateTimeString.split(" ")[0]

            spanTargetDefValueStart = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanEndTimes'] == startDateTimeObject)]['spanTarget'].values[0]
            spanTargetDefValueEnd = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanStartTimes'] == endDateTimeObject)]['spanTarget'].values[0]
            spanTargetNewValueStart = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanEndTimes'] == startDateTimeObject)]['spanTarget'].values[0]
            spanTargetNewValueEnd = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == endDateTimeObject)]['spanTarget'].values[0]
            spanTargetAppValueStart = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanEndTimes'] == startDateTimeObject)]['spanTarget'].values[0]
            spanTargetAppValueEnd = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == endDateTimeObject)]['spanTarget'].values[0]
            
            spanDefValueStart = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanEndTimes'] == startDateTimeObject)]['spanVal'].values[0]
            spanDefValueEnd = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanStartTimes'] == endDateTimeObject)]['spanVal'].values[0]
            spanNewValueStart = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanEndTimes'] == startDateTimeObject)]['spanVal'].values[0]
            spanNewValueEnd = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == endDateTimeObject)]['spanVal'].values[0]
            spanAppValueStart = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanEndTimes'] == startDateTimeObject)]['spanVal'].values[0]
            spanAppValueEnd = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == endDateTimeObject)]['spanVal'].values[0]

            zeroDefValueStart = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanEndTimes'] == startDateTimeObject)]['zeroVal'].values[0]
            zeroDefValueEnd = self.DF_SpanCycle.loc[(self.DF_SpanCycle['spanStartTimes'] == endDateTimeObject)]['zeroVal'].values[0]
            zeroNewValueStart = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanEndTimes'] == startDateTimeObject)]['zeroVal'].values[0]
            zeroNewValueEnd = self.DF_SpanCycleNew.loc[(self.DF_SpanCycleNew['spanStartTimes'] == endDateTimeObject)]['zeroVal'].values[0]
            zeroAppValueStart = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanEndTimes'] == startDateTimeObject)]['zeroVal'].values[0]
            zeroAppValueEnd = self.DF_SpanCycleApp.loc[(self.DF_SpanCycleApp['spanStartTimes'] == endDateTimeObject)]['zeroVal'].values[0]
            
            self.updateCellValue(self.SpanTargetValDefBoxStart, spanTargetDefValueStart, readOnly=True)            
            self.updateCellValue(self.SpanValDefBoxStart, spanDefValueStart, readOnly=True)
            self.updateCellValue(self.ZeroValDefBoxStart, zeroDefValueStart, readOnly=True)
            self.updateCellValue(self.SpanTargetValNewBoxStart, spanTargetNewValueStart)
            self.updateCellValue(self.SpanValNewBoxStart, spanNewValueStart)
            self.updateCellValue(self.ZeroValNewBoxStart, zeroNewValueStart)
            self.updateCellValue(self.SpanTargetValAppBoxStart, spanTargetAppValueStart, readOnly=True)
            self.updateCellValue(self.SpanValAppBoxStart, spanAppValueStart, readOnly=True)
            self.updateCellValue(self.ZeroValAppBoxStart, zeroAppValueStart, readOnly=True)
            
            self.updateCellValue(self.SpanTargetValDefBoxEnd, spanTargetDefValueEnd, readOnly=True)    
            self.updateCellValue(self.SpanValDefBoxEnd, spanDefValueEnd, readOnly=True)
            self.updateCellValue(self.ZeroValDefBoxEnd, zeroDefValueEnd, readOnly=True)
            self.updateCellValue(self.SpanTargetValNewBoxEnd, spanTargetNewValueEnd)
            self.updateCellValue(self.SpanValNewBoxEnd, spanNewValueEnd)
            self.updateCellValue(self.ZeroValNewBoxEnd, zeroNewValueEnd)
            self.updateCellValue(self.SpanTargetValAppBoxEnd, spanTargetAppValueEnd, readOnly=True)
            self.updateCellValue(self.SpanValAppBoxEnd, spanAppValueEnd, readOnly=True)
            self.updateCellValue(self.ZeroValAppBoxEnd, zeroAppValueEnd, readOnly=True)

        return

###################################################################
###################################################################

    def updateCellValue(self, box, value, readOnly=False):
        
        if readOnly == True:
            box.config(state='normal')
            
        box.delete(0, 'end')
        box.insert(0, value)
            
        if readOnly == True:
            box.config(state='readonly')
        
        return

###################################################################
###################################################################
    
    def getFileArray(self, inputFile, delimiter):
    # Converts contents of input file in formats similar to CSVs into a string array

        # Open input file
        processFile = open(inputFile, 'r')

        # Read all the lines in the file
        lines = processFile.readlines()

        # Initialize output array
        contentArray = []

        # Loop through the lines
        for i in range(0,len(lines)):

            # Strip the regex line dividers from each single line
            line = repr(lines[i].rstrip('\r\n'))

            # Split the single line with the input delimited into an array
            arrayLine = line.split(delimiter)

            # Loop though each value of the line array and remove unnecessary strings
            for i in range(0,len(arrayLine)):
                arrayLine[i] = arrayLine[i].replace("'", "")
                arrayLine[i] = arrayLine[i].replace("[", "")
                arrayLine[i] = arrayLine[i].replace("]", "")

            # Append to output array
            contentArray.append(arrayLine)

        processFile.close()

        return contentArray
    
###################################################################
###################################################################
        
    def plotDataPop(self, calib=True):
        
        figWidth = 12
        figHeight = 5
        
        fig = plt.figure(figsize=(figWidth,figHeight), dpi = 100)
        fig_x0 = 0.1
        fig_y0 = 0.2
        fig_x1 = 0.8
        fig_y1 = 0.7
        ax = fig.add_axes([fig_x0,fig_y0,fig_x1,fig_y1])
        canvas = fig.canvas
        self.plotData(canvas, ax, calib, pop=True)
        
        return

###################################################################
###################################################################
        
    def plotData(self, canvas, ax, calib=True, pop=False):
        
        dateListBoxindexList = self.dateListBox.curselection()
        
        if len(dateListBoxindexList)>0:
            periodString = self.dateListBox.get(dateListBoxindexList[0])
            startDateString = periodString.split(" - ")[0]
            endDateString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateString,'%Y-%m-%d %H:%M:%S')
            endDateTimeObject = dt.datetime.strptime(endDateString,'%Y-%m-%d %H:%M:%S')
            
            DF_plot = self.DF_RawData[(self.DF_RawData['dateTimeObj'] >= startDateTimeObject) & (self.DF_RawData['dateTimeObj'] <= endDateTimeObject)]
            
            # For plotting Raw Data
            timeArray = list(DF_plot['dateTimeObj'])
            dataArray = list(DF_plot['NO'])
            
            # For plotting calibrated values
            timeArrayLength = 0
            timeArrayIndex = []
            calibratedDataArray = []
            
            for i in range(0,len(timeArray)):
                timeArrayLength = timeArrayLength + 1
                timeArrayIndex.append(timeArrayLength)
                
            ax.clear()
            
            hfmt = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M')
            ax.xaxis.set_major_formatter(hfmt)
            
            ax.plot(timeArray, dataArray, 'b-', label='NO Conc.')
            
            if len(self.SpanValAppBoxStart.get())>0 and len(self.ZeroValAppBoxStart.get())>0 and len(self.SpanValAppBoxEnd.get())>0 and len(self.ZeroValAppBoxEnd.get())>0 and calib==True:
                spanTargetValStart = float(self.SpanTargetValAppBoxStart.get())
                spanValStart = float(self.SpanValAppBoxStart.get())
                zeroValStart = float(self.ZeroValAppBoxStart.get())
                spanTargetValEnd = float(self.SpanTargetValAppBoxEnd.get())
                spanValEnd = float(self.SpanValAppBoxEnd.get())
                zeroValEnd = float(self.ZeroValAppBoxEnd.get())
                for i in range(0,len(timeArray)):
                    calibratedValue = self.calibrateVal(dataArray[i], spanTargetValStart, spanValStart, zeroValStart, timeArrayIndex[i], timeArrayLength, spanTargetValEnd, spanValEnd, zeroValEnd)
                    calibratedDataArray.append(calibratedValue)
                ax.plot(timeArray,calibratedDataArray, 'r-', label='Calibrated')
            
            ax.set_title('CO Data - ' + periodString)
            ax.legend(shadow=True, fancybox=True)
                
            canvas.figure.autofmt_xdate()
            
            if pop==False:
                canvas.draw()
            else:
                canvas.set_window_title(periodString)
            
        return
###################################################################
###################################################################
        
    def plotSpanDataPop(self):
        
        figWidth = 12
        figHeight = 5
        
        fig = plt.figure(figsize=(figWidth,figHeight), dpi = 100)
        fig_x0 = 0.05
        fig_y0 = 0.2
        fig_x1 = 0.9
        fig_y1 = 0.7
        ax = fig.add_axes([fig_x0,fig_y0,fig_x1,fig_y1])
        canvas = fig.canvas
        self.plotSpanData(canvas, ax, pop=True)
        
        return
    
###################################################################
###################################################################
        
    def plotSpanData(self, canvas, ax, calib=True, pop=False):
        
        dateListBoxindexList = self.SpanCycleDateListBox.curselection()
        
        if len(dateListBoxindexList)>0:
            periodString = self.SpanCycleDateListBox.get(dateListBoxindexList[0])
            startDateString = periodString.split(" - ")[0]
            endDateString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateString,'%Y-%m-%d %H:%M:%S')
            endDateTimeObject = dt.datetime.strptime(endDateString,'%Y-%m-%d %H:%M:%S')

            DF_plot = self.DF_RawData[(self.DF_RawData['dateTimeObj'] >= startDateTimeObject) & (self.DF_RawData['dateTimeObj'] <= endDateTimeObject)]
            DF_SpanCycle = self.DF_SpanCycle[(self.DF_SpanCycle['spanStartTimes'] == startDateTimeObject) & (self.DF_SpanCycle['spanEndTimes'] == endDateTimeObject)]

            maxTimeArray = list(set(DF_SpanCycle['MaxTime']))
            maxValArray = list(set(DF_SpanCycle['spanVal']))
            
            ax.clear()
            
            hfmt = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M')
            ax.xaxis.set_major_formatter(hfmt)
            
            if self.SpanCycle_Check_NO.get():
                ax.plot(DF_plot['dateTimeObj'], DF_plot['NO'], color='blue', label='NO')
                ax.plot(maxTimeArray[0], maxValArray[0], 'bx', label='Max Span')

            if self.SpanCycle_Check_NO2.get():
                ax.plot(DF_plot['dateTimeObj'], DF_plot['NO2'], color='magenta', label='NO2')

            if self.SpanCycle_Check_NOX.get():
                ax.plot(DF_plot['dateTimeObj'], DF_plot['NOX'], color='lightseagreen', label='NOX')
                
            ax.set_title(periodString)
            ax.legend(shadow=True, fancybox=True)
                
            canvas.figure.autofmt_xdate()
            
            if pop==False:
                canvas.draw()
            else:
                canvas.set_window_title(periodString)
            
        return
    
###################################################################
###################################################################

    def calibrateVal(self, inputVal, spanTargetValStart, spanValStart, zeroValStart, timeIndex, timeLength, spanTargetValEnd, spanValEnd, zeroValEnd):

        offSetStep = (zeroValEnd-zeroValStart)/timeLength
        offSetInc = timeIndex*offSetStep
        offSetApplied = zeroValStart + offSetInc
        offSetCalib = float(inputVal) - offSetApplied
        KFac = spanTargetValStart/spanValStart
        nextKFac = spanTargetValEnd/spanValEnd
        KFactStep = (nextKFac-KFac)/timeLength
        KFacInc = timeIndex*KFactStep
        KFactApplied = KFac + KFacInc
        calibratedVal = offSetCalib*KFactApplied
        
        return calibratedVal
    
###################################################################
###################################################################

    def plotTimeSeriesDataPop(self, plotTab):
        
        timeSeriesPlotsWidth = 12
        timeSeriesPlotsHeight = 5
        
        timeSeries_fig = plt.figure(figsize=(timeSeriesPlotsWidth,timeSeriesPlotsHeight), dpi = 100)
        timeSeries_fig_x0 = 0.05
        timeSeries_fig_y0 = 0.2
        timeSeries_fig_x1 = 0.9
        timeSeries_fig_y1 = 0.7
        timeSeries_ax = timeSeries_fig.add_axes([timeSeries_fig_x0,timeSeries_fig_y0,timeSeries_fig_x1,timeSeries_fig_y1])
        timeSeries_canvas = timeSeries_fig.canvas
        self.plotTimeSeriesData(timeSeries_canvas, timeSeries_ax, plotTab, True)

        return
###################################################################
###################################################################
    
    def plotTimeSeriesData(self,canvas,ax,plotTab,pop=False):

        ax.clear()
        
        hfmt = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M')
        ax.xaxis.set_major_formatter(hfmt)
        
        if plotTab == 'TimeSeries':
            startDate = self.TS_startDateString.get()
            startHour = self.TS_startHourString.get()
            startMin = self.TS_startMinString.get()
            endDate = self.TS_endDateString.get()
            endHour = self.TS_endHourString.get()
            endMin = self.TS_endMinString.get()
            Check_NO = self.TS_Check_NO.get()
            Check_NO2 = self.TS_Check_NO2.get()
            Check_NOX = self.TS_Check_NOX.get()
            Check_AcceptedSpanCycles = self.TS_Check_AcceptedSpanCycles.get()
            Check_RejectedSpanCycles = self.TS_Check_RejectedSpanCycles.get()
            acceptedCyclesList = self.TS_SpanCycleDateListBox.get(0,'end')
            rejectedCyclesList = self.TS_Dis_SpanCycleDateListBox.get(0,'end')
            
        else:
            startDate = self.DV_startDateString.get()
            startHour = self.DV_startHourString.get()
            startMin = self.DV_startMinString.get()
            endDate = self.DV_endDateString.get()
            endHour = self.DV_endHourString.get()
            endMin = self.DV_endMinString.get()
            
            InvData_startDate = self.DV_InvData_startDateString.get()
            InvData_startHour = self.DV_InvData_startHourString.get()
            InvData_startMin = self.DV_InvData_startMinString.get()
            InvData_endDate = self.DV_InvData_endDateString.get()
            InvData_endHour = self.DV_InvData_endHourString.get()
            InvData_endMin = self.DV_InvData_endMinString.get()
            
            Check_ValidatedData = self.DV_Check_ValidatedData.get()
            Check_InvalidatedData = self.DV_Check_InvalidatedData.get()
            Check_ShowRange = self.DV_InvData_Check_ShowRange.get()
            
            
        startDateTimeString = startDate + " " + startHour + ":" + startMin
        endDateTimeString = endDate + " " + endHour + ":" + endMin
        
        startDateTimeObj = dt.datetime.strptime(startDateTimeString,'%Y-%m-%d %H:%M')
        endDateTimeObj = dt.datetime.strptime(endDateTimeString,'%Y-%m-%d %H:%M')
        
        dateString = startDateTimeString + " - " + endDateTimeString
        
        DF_plot = self.DF_RawData.loc[(self.DF_RawData['dateTimeObj'] >= startDateTimeObj) & (self.DF_RawData['dateTimeObj'] <= endDateTimeObj)]

        if plotTab == 'TimeSeries':
            if Check_NO:
                ax.plot(DF_plot['dateTimeObj'], DF_plot['NO'], color='blue', label='NO')

            if Check_NO2:
                ax.plot(DF_plot['dateTimeObj'], DF_plot['NO2'], color='magenta', label='NO2')

            if Check_NOX:
                ax.plot(DF_plot['dateTimeObj'], DF_plot['NOX'], color='lightseagreen', label='NOX')

            if Check_AcceptedSpanCycles:
                acceptedCycles = acceptedCyclesList
                for i in range(0,len(acceptedCycles)):
                    cycleStart = acceptedCycles[i].split(" - ")[0]
                    cycleEnd = acceptedCycles[i].split(" - ")[1]
                    cycleStartDateTimeObj = dt.datetime.strptime(cycleStart,'%Y-%m-%d %H:%M:%S')
                    cycleEndDateTimeObj = dt.datetime.strptime(cycleEnd,'%Y-%m-%d %H:%M:%S')
                    DF_plot_accepted_filt = DF_plot[(DF_plot['dateTimeObj'] >= cycleStartDateTimeObj) & (DF_plot['dateTimeObj'] <= cycleEndDateTimeObj)]
                    if i == 0:
                        ax.plot(DF_plot_accepted_filt['dateTimeObj'], DF_plot_accepted_filt['NO'], color='green', label='Accepted Cycles')    
                    else:
                        ax.plot(DF_plot_accepted_filt['dateTimeObj'], DF_plot_accepted_filt['NO'], color='green', label='_nolegend_')


            if Check_RejectedSpanCycles:
                rejectedCycles = rejectedCyclesList
                for i in range(0,len(rejectedCycles)):
                    cycleStart = rejectedCycles[i].split(" - ")[0]
                    cycleEnd = rejectedCycles[i].split(" - ")[1]
                    cycleStartDateTimeObj = dt.datetime.strptime(cycleStart,'%Y-%m-%d %H:%M:%S')
                    cycleEndDateTimeObj = dt.datetime.strptime(cycleEnd,'%Y-%m-%d %H:%M:%S')
                    DF_plot_rejected_filt = DF_plot[(DF_plot['dateTimeObj'] >= cycleStartDateTimeObj) & (DF_plot['dateTimeObj'] <= cycleEndDateTimeObj)]
                    if i == 0:
                        ax.plot(DF_plot_rejected_filt['dateTimeObj'], DF_plot_rejected_filt['NO'], color='red', label='Rejected Cycles')    
                    else:
                        ax.plot(DF_plot_rejected_filt['dateTimeObj'], DF_plot_rejected_filt['NO'], color='red', label='_nolegend_')
        else:
            
            if Check_ValidatedData:
                ax.plot(DF_plot.loc[DF_plot['validated'] == True]['dateTimeObj'], DF_plot.loc[DF_plot['validated'] == True]['NO'], color='blue', label='Validated')
                
            if Check_InvalidatedData:
                invalidatedDataRangeList = self.DV_InvDataDateListBox.get(0,'end')
                if len(invalidatedDataRangeList)>0:
                    rangeIsInList = False
                    for i in range(0,len(invalidatedDataRangeList)):

                        periodString = invalidatedDataRangeList[i]
                        startDateString = periodString.split(" - ")[0]
                        endDateString = periodString.split(" - ")[1]
                        startDateTimeObject = dt.datetime.strptime(startDateString,'%Y-%m-%d %H:%M')
                        endDateTimeObject = dt.datetime.strptime(endDateString,'%Y-%m-%d %H:%M')
                        DF_InvData = DF_plot.loc[(DF_plot['dateTimeObj'] >= startDateTimeObject) & (DF_plot['dateTimeObj'] <= endDateTimeObject)]
                        if i == 0:
                            ax.plot(DF_InvData['dateTimeObj'], DF_InvData['NO'], color='red', label='Invalidated')
                        else:
                            ax.plot(DF_InvData['dateTimeObj'], DF_InvData['NO'], color='red', label='_nolegend_')
                
            if Check_ShowRange:
                InvData_startDateTimeString = InvData_startDate + " " + InvData_startHour + ":" + InvData_startMin
                InvData_endDateTimeString = InvData_endDate + " " + InvData_endHour + ":" + InvData_endMin

                InvData_startDateTimeObj = dt.datetime.strptime(InvData_startDateTimeString,'%Y-%m-%d %H:%M')
                InvData_endDateTimeObj = dt.datetime.strptime(InvData_endDateTimeString,'%Y-%m-%d %H:%M')
                
                DF_ShowRange = DF_plot.loc[(DF_plot['dateTimeObj'] >= InvData_startDateTimeObj) & (DF_plot['dateTimeObj'] <= InvData_endDateTimeObj)]
                
                ax.plot(DF_ShowRange['dateTimeObj'], DF_ShowRange['NO'], color='darkviolet', label='Selected Range')
                
        ax.set_title(dateString)
        ax.legend()

        canvas.figure.autofmt_xdate()
        
        if pop==False:
            canvas.draw()
        else:
            canvas.set_window_title(dateString)
        
        return
    
###################################################################
###################################################################

    def saveOutputDF(self, outputFilePath, option):
        
        saveStartTime = time.time()
        
        # Gather data and span/zero values to be applied
        DF_ouput = self.DF_RawData[['dateTimeObj', 'NO', 'validated']]
        DF_SpanCyclesApp = self.DF_SpanCycleApp.copy()
        
        # Exclude rejected span cycles
        DF_AcceptedSpanCycles = pd.DataFrame({'spanCycleStart':self.spanStartArray, 'spanCycleEnd':self.spanEndArray})
        DF_SpanCycles_All = pd.merge(DF_SpanCyclesApp, DF_AcceptedSpanCycles, left_on='spanStartTimes', right_on='spanCycleStart', how='left', sort=False)
        DF_SpanCycles_All['Status'] = DF_SpanCycles_All['spanCycleStart'].apply(lambda x: True if pd.notnull(x) else False)
        
        # Reorder the columns for output
        DF_SpanCycles_All = DF_SpanCycles_All[['spanStartTimes', 'spanEndTimes', 'spanCycleStart', 'spanCycleEnd', 'zeroVal', 'spanVal', 'MaxTime', 'spanTarget', 'Status']]
        
        DF_SpanCycle = DF_SpanCycles_All[DF_SpanCycles_All['spanCycleStart'].isnull()==False]
        
        # To turn off the 'SettingWithCopyWarning:' warning
        DF_SpanCycle.is_copy = False
        
        
        # Gather finalised data periods to calibrate
        dataCycleStart = []
        dataCycleEnd = []
        minDiff = [] # Number of minutes between span cycles for calibration caluclation
        
        for i in range(0,len(self.dataCycleArray)):
            periodString = self.dataCycleArray[i]
            startDateTimeString = periodString.split(" - ")[0]
            endDateTimeString = periodString.split(" - ")[1]
            
            startDateString = startDateTimeString.split(" ")[0]
            startTimeString = startDateTimeString.split(" ")[1]
            startHourMinString = startTimeString.split(":")[0]+":"+startTimeString.split(":")[1]
            startCycleString = startDateString+" "+startHourMinString

            endDateString = endDateTimeString.split(" ")[0]
            endTimeString = endDateTimeString.split(" ")[1]
            endHourMinString = endTimeString.split(":")[0]+":"+endTimeString.split(":")[1]
            endCycleString = endDateString+" "+endHourMinString
            
            startDateTimeObject = dt.datetime.strptime(startCycleString,'%Y-%m-%d %H:%M')
            endDateTimeObject = dt.datetime.strptime(endCycleString,'%Y-%m-%d %H:%M')
            
            dataCycleStart.append(startDateTimeObject)
            dataCycleEnd.append(endDateTimeObject)
            minDiff.append((endDateTimeObject - startDateTimeObject).total_seconds() / 60.0)

        dataCyclePeriods = pd.DataFrame({'dataCycleStart':dataCycleStart, 'dataCycleEnd':dataCycleEnd, 'minDiff':minDiff})
        
        # Getting rid of the seconds to match times
        DF_SpanCycle['spanStart'] = DF_SpanCycle['spanStartTimes'].apply(lambda x: self.dateTimeObjStripSeconds(x))
        DF_SpanCycle['spanEnd'] = DF_SpanCycle['spanEndTimes'].apply(lambda x: self.dateTimeObjStripSeconds(x))
        
        
        # Joining the finialised data periods to span/zero data from accepted span cycles
        DF_cycleStart = pd.merge(dataCyclePeriods, DF_SpanCycle, left_on='dataCycleStart', right_on='spanEnd', how='left', sort=False)
        
        # Remove unnecessary columns and rename appropriately
        DF_cycleEnd = pd.merge(DF_cycleStart, DF_SpanCycle, left_on='dataCycleEnd', right_on='spanStart', how='left', sort=False)
        DF_cycleEnd = DF_cycleEnd.rename(columns={'zeroVal_x':'zeroVal', 'zeroVal_y':'zeroValEnd', 'spanVal_x':'spanVal', 'spanVal_y':'spanValEnd', 'spanTarget_x':'spanTarget', 'spanTarget_y':'spanTargetEnd'})
        DF_cycleEnd = DF_cycleEnd.drop('spanEndTimes_y', axis=1)
        DF_cycleEnd = DF_cycleEnd.drop('spanStartTimes_x', axis=1)
        DF_cycleEnd = DF_cycleEnd.drop('dataCycleStart', axis=1)
        DF_cycleEnd = DF_cycleEnd.drop('dataCycleEnd', axis=1)
        DF_cycleEnd = DF_cycleEnd.drop('spanStart_x', axis=1)
        DF_cycleEnd = DF_cycleEnd.drop('spanEnd_x', axis=1)
        DF_cycleEnd = DF_cycleEnd.drop('spanStart_y', axis=1)
        DF_cycleEnd = DF_cycleEnd.drop('spanEnd_y', axis=1)
        DF_cycleEnd = DF_cycleEnd.rename(columns={'MaxTime_x':'MaxTime_Start', 'MaxTime_y':'MaxTime_End', 'spanEndTimes_x':'dataCycleStart', 'spanStartTimes_y':'dataCycleEnd'})
        
        #print DF_cycleEnd
        
        # Joining the finalised config of span cycles and data periods to raw data
        query = """
                SELECT
                    datetime(DF_ouput.dateTimeObj) AS DateTime
                    , DF_ouput.NO AS NO
                    , DF_ouput.validated AS validated
                    , datetime(DF_cycleEnd.dataCycleStart) AS dataCycleStart
                    , datetime(DF_cycleEnd.dataCycleEnd) AS dataCycleEnd
                    , DF_cycleEnd.minDiff AS minDiff
                    , DF_cycleEnd.spanTarget AS spanTarget
                    , DF_cycleEnd.spanTargetEnd AS spanTargetEnd
                    , DF_cycleEnd.spanVal AS spanVal
                    , DF_cycleEnd.spanValEnd AS spanValEnd
                    , DF_cycleEnd.zeroVal AS zeroVal
                    , DF_cycleEnd.zeroValEnd AS zeroValEnd
                FROM
                    DF_ouput 
                LEFT OUTER JOIN
                    DF_cycleEnd
                ON
                    DF_ouput.dateTimeObj > DF_cycleEnd.dataCycleStart AND DF_ouput.dateTimeObj < DF_cycleEnd.dataCycleEnd
                ORDER BY
                    DF_ouput.dateTimeObj;
                """
        
        DF_QueryResult = sqldf(query, locals())
        
        # Calculate the size of time step increment for calibration
        DF_QueryResult['timeIndex'] = 0
        prevTimeIndex = 0
        for index, row in DF_QueryResult.iterrows():
            timeIndex = 0
            if row['zeroValEnd'] is not None:
                if isinstance(row['zeroValEnd'], unicode):
                    zeroValEnd = float(row['zeroValEnd'])
                else:
                    zeroValEnd = row['zeroValEnd']
                
                if math.isnan(zeroValEnd)==False:
                    timeIndex = prevTimeIndex + 1
                    DF_QueryResult.set_value(index,'timeIndex',timeIndex)
            else:
                prevTimeIndex = 0
                
            prevTimeIndex = timeIndex

        # Calculate calibrated values
        DF_QueryResult['calibrated_NO'] = DF_QueryResult['NO']
        for index, row in DF_QueryResult.iterrows():
            if row['zeroValEnd'] is not None:

                NO = float(row['NO'])
                spanTarget = float(row['spanTarget'])
                spanVal = float(row['spanVal'])
                zeroVal = float(row['zeroVal'])
                timeIndex = float(row['timeIndex'])
                minDiff = float(row['minDiff'])
                spanTargetEnd = float(row['spanTargetEnd'])
                spanValEnd = float(row['spanValEnd'])
                zeroValEnd = float(row['zeroValEnd'])
                
                if math.isnan(zeroValEnd)==False:
                    calval = self.calibrateVal(NO, spanTarget, spanVal, zeroVal, timeIndex, minDiff, spanTargetEnd, spanValEnd, zeroValEnd)
                    DF_QueryResult.set_value(index,'calibrated_NO',calval)
                
        # Saving file to output
        
        if option=='XLS':
            if self.XLSSaveResult_Check_InvalidatedData.get():
                DF_CalibratedResult = DF_QueryResult[['DateTime', 'NO', 'calibrated_NO', 'validated']]
            else:
                DF_QueryResult = DF_QueryResult[DF_QueryResult['validated']==True]
                DF_CalibratedResult = DF_QueryResult[['DateTime', 'NO', 'calibrated_NO']]
                
            if self.XLSSaveResult_Check_DisgardedSpanCycle.get():
                DF_SpanCycle_Output = DF_SpanCycles_All[['spanStartTimes', 'spanEndTimes', 'zeroVal', 'spanVal', 'MaxTime', 'spanTarget', 'Status']]
            else:
                DF_SpanCycle_Output = DF_SpanCycles_All[DF_SpanCycles_All['Status']==True]
                DF_SpanCycle_Output = DF_SpanCycle_Output[['spanStartTimes', 'spanEndTimes', 'zeroVal', 'spanVal', 'MaxTime', 'spanTarget']]
                
            writer = pd.ExcelWriter(outputFilePath)
            DF_CalibratedResult.to_excel(writer,'Calibrated Results', index=False)
            DF_SpanCycle_Output.to_excel(writer,'Span Cycle Data', index=False)
            writer.save()

        
        if option=='DataCSV':

            if self.SaveResult_Check_InvalidatedData.get():
                DF_CalibratedResult = DF_QueryResult[['DateTime', 'NO', 'calibrated_NO', 'validated']]
            else:
                DF_QueryResult = DF_QueryResult[DF_QueryResult['validated']==True]
                DF_CalibratedResult = DF_QueryResult[['DateTime', 'NO', 'calibrated_NO']]
                
            DF_CalibratedResult.to_csv(outputFilePath, sep=',', index=False)
        
        if option=='SpanCSV':

            if self.SpanSaveResult_Check_DisgardedSpanCycle.get():
                DF_SpanCycle_Output = DF_SpanCycles_All[['spanStartTimes', 'spanEndTimes', 'zeroVal', 'spanVal', 'MaxTime', 'spanTarget', 'Status']]
            else:
                DF_SpanCycle_Output = DF_SpanCycles_All[DF_SpanCycles_All['Status']==True]
                DF_SpanCycle_Output = DF_SpanCycle_Output[['spanStartTimes', 'spanEndTimes', 'zeroVal', 'spanVal', 'MaxTime', 'spanTarget']]
                
            DF_SpanCycle_Output.to_csv(outputFilePath, sep=',', index=False)                
        
        saveEndTime = time.time()
        print("Saving time: " + repr(saveEndTime-saveStartTime))
        return

###################################################################
###################################################################

    def dateTimeObjStripSeconds(self,dateTimeObj):
        
        dateTimeString = dateTimeObj.strftime('%Y-%m-%d %H:%M:%S')
        dateString = dateTimeString.split(" ")[0]
        timeString = dateTimeString.split(" ")[1]
        hourString = timeString.split(":") [0]
        minString = timeString.split(":") [1]
        outTimeString = dateString + " " + hourString + ":" + minString
        trimmedDateTimeObj = dt.datetime.strptime(outTimeString,'%Y-%m-%d %H:%M')
        
        return trimmedDateTimeObj
    
###################################################################
###################################################################
    
    def saveToFile(self, textBox, option):
        
        outputFilePath = textBox.get()
        #outputFilePath = 'test.csv'

        if hasattr(self,'NOxCalib'):
            if len(outputFilePath) == 0:
                messagebox.showinfo("Choose Output File", "Please choose an output file")
                self.chooseFile(textBox)
            else:
                if path.exists(outputFilePath):
                    result = messagebox.askyesno("Overwrite existing file", "Are you sure you would like to overwrite an existing file?")
                    if result == True:
                        self.saveOutputDF(outputFilePath, option)
                        messagebox.showinfo("Save successful", "Output file saved successfully.")
                    else:
                        self.chooseFile(textBox)
                else:
                    self.saveOutputDF(outputFilePath,option)
                    messagebox.showinfo("Save successful", "Output file saved successfully.")
        else:
            messagebox.showinfo("Load file and results", "Please load file and results")
        
        return
    
###################################################################
###################################################################

    def acceptCycle(self,indexList):

        if len(indexList)>0:
            selectedCycle = self.TS_Dis_SpanCycleDateListBox.get(indexList[0])
            
            periodString = self.TS_Dis_SpanCycleDateListBox.get(indexList[0])
            startDateString = periodString.split(" - ")[0]
            endDateString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateString,'%Y-%m-%d %H:%M:%S')
            endDateTimeObject = dt.datetime.strptime(endDateString,'%Y-%m-%d %H:%M:%S')
            
            
            self.spanStartArray.append(startDateTimeObject)
            self.spanEndArray.append(endDateTimeObject)
            
            self.spanStartArray.sort()
            self.spanEndArray.sort()
            
            self.TS_Dis_SpanCycleDateListBox.delete(indexList)
        
            self.fillListBoxes()
            self.plotTimeSeriesData(self.TimeSeries_canvas,self.TimeSeries_ax,'TimeSeries')
        
        return

###################################################################
###################################################################

    def rejectCycle(self,indexList):
        
        if len(indexList)>0:
            selectedCycle = self.TS_SpanCycleDateListBox.get(indexList[0])
            
            periodString = self.TS_SpanCycleDateListBox.get(indexList[0])
            startDateString = periodString.split(" - ")[0]
            endDateString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateString,'%Y-%m-%d %H:%M:%S')
            endDateTimeObject = dt.datetime.strptime(endDateString,'%Y-%m-%d %H:%M:%S')
            
            spanStartArray = []
            spanEndArray = []
            
            for i in range(0,len(self.spanStartArray)):
                if self.spanStartArray[i] != startDateTimeObject and self.spanEndArray[i] != endDateTimeObject:
                    spanStartArray.append(self.spanStartArray[i])
                    spanEndArray.append(self.spanEndArray[i])
                    
            self.spanStartArray = spanStartArray
            self.spanEndArray = spanEndArray
            
            self.TS_Dis_SpanCycleDateListBox.insert(tkinter.END, selectedCycle)
            
            self.fillListBoxes()
            self.plotTimeSeriesData(self.TimeSeries_canvas,self.TimeSeries_ax,'TimeSeries')
            
        return

###################################################################
###################################################################

    def validateData(self):
        
        dataRangeListBoxIndexList = self.DV_InvDataDateListBox.curselection()
        
        if len(dataRangeListBoxIndexList)>0:
            periodString = self.DV_InvDataDateListBox.get(dataRangeListBoxIndexList[0])
            startDateString = periodString.split(" - ")[0]
            endDateString = periodString.split(" - ")[1]
            startDateTimeObject = dt.datetime.strptime(startDateString,'%Y-%m-%d %H:%M')
            endDateTimeObject = dt.datetime.strptime(endDateString,'%Y-%m-%d %H:%M')
            self.DF_RawData.loc[(self.DF_RawData['dateTimeObj'] >= startDateTimeObject) & (self.DF_RawData['dateTimeObj'] <= endDateTimeObject),  'validated'] = True
        
        self.DV_InvDataDateListBox.delete(dataRangeListBoxIndexList)
        self.plotTimeSeriesData(self.DV_TimeSeries_canvas,self.DV_TimeSeries_ax,'DataValidation')
        
        return
    
###################################################################
###################################################################

    def invalidateData(self):
        
        startDate = self.DV_InvData_startDateString.get()
        startHour = self.DV_InvData_startHourString.get()
        startMin = self.DV_InvData_startMinString.get()
        endDate = self.DV_InvData_endDateString.get()
        endHour = self.DV_InvData_endHourString.get()
        endMin = self.DV_InvData_endMinString.get()
        
        startDateTimeString = startDate + " " + startHour + ":" + startMin
        endDateTimeString = endDate + " " + endHour + ":" + endMin
        
        startDateTimeObj = dt.datetime.strptime(startDateTimeString,'%Y-%m-%d %H:%M')
        endDateTimeObj = dt.datetime.strptime(endDateTimeString,'%Y-%m-%d %H:%M')
        
        if startDateTimeObj >= endDateTimeObj:
            self.timeRangeWarning()
            
        else:
        
            dateString = startDateTimeString + " - " + endDateTimeString

            invalidatedDataRangeList = self.DV_InvDataDateListBox.get(0,'end')
            
            if len(invalidatedDataRangeList)>0:
                rangeIsInList = False
                for i in range(0,len(invalidatedDataRangeList)):
                    if invalidatedDataRangeList[i] == dateString:
                        rangeIsInList = True
                        break
                if rangeIsInList == False:
                    self.DV_InvDataDateListBox.insert(tkinter.END, dateString)
                    
            else:
                self.DV_InvDataDateListBox.insert(tkinter.END, dateString)
                
            # Update the validation status of the associated rows in the main dataframe
            updatedInvalidatedDataRangeList = self.DV_InvDataDateListBox.get(0,'end')
            
            timeRangeStartArray = []
            timeRangeEndArray = []
            
            self.DF_RawData['validated'] = True
            
            for i in range(0,len(updatedInvalidatedDataRangeList)):
                timeRangeString = updatedInvalidatedDataRangeList[i]
                startTimeRange = timeRangeString.split(" - ")[0]
                endTimeRange = timeRangeString.split(" - ")[1]
                startTimeRangeObj = dt.datetime.strptime(startTimeRange,'%Y-%m-%d %H:%M')
                endTimeRangeObj = dt.datetime.strptime(endTimeRange,'%Y-%m-%d %H:%M')
                timeRangeStartArray.append(startTimeRangeObj)
                timeRangeEndArray.append(endTimeRangeObj)
                self.DF_RawData.loc[(self.DF_RawData['dateTimeObj'] >= startTimeRangeObj) & (self.DF_RawData['dateTimeObj'] <= endTimeRangeObj),  'validated'] = False
            
            self.plotTimeSeriesData(self.DV_TimeSeries_canvas,self.DV_TimeSeries_ax,'DataValidation')
        
        return

###################################################################
###################################################################

    def timeRangeWarning(self):
    
        messagebox.showinfo("Time range warning", "Please ensure the selected start time is before the selected end time.")
        
        return 
    
###################################################################
###################################################################

    def cloneArray(self,inputArray):
        
        outputArray = []
        
        for i in range(0,len(inputArray)):
            lineArray = inputArray[i]
            outputArray.append(lineArray)
        
        return outputArray

###################################################################
###################################################################

    def chooseFile(self,textEntryBox):

        currentStringlength = len(textEntryBox.get())
        filename = askopenfilename()
        textEntryBox.delete(0,currentStringlength)
        textEntryBox.insert(0,filename)
        
        return
###################################################################
###################################################################

    def chooseSaveFile(self,textEntryBox,option):

        if option=='CSV':
            saveFileType = [('CSV File', '*.csv')]
        else:
            saveFileType = [('XLS File', '*.xls')]
        
        currentStringlength = len(textEntryBox.get())
        filename = asksaveasfilename(filetypes=saveFileType)
        textEntryBox.delete(0,currentStringlength)
        textEntryBox.insert(0,filename)
        
        return
###################################################################
###################################################################
    
    def chooseDir(self,textEntryBox):

        currentStringlength = len(textEntryBox.get())
        dirname = askdirectory()
        textEntryBox.delete(0,currentStringlength)
        textEntryBox.insert(0,dirname)
        
        return
    
###################################################################
###################################################################
    
    def on_closing(self):

        if messagebox.askokcancel("Quit", "Sure you want to quit?"):
            self.master.destroy()
            sys.exit()

        return

###################################################################
###################################################################
###################################################################
###################################################################

# Set plot style
sns.set_style("darkgrid")

# Paint the GUI
GUI = tkinter.Tk()

my_GUI = NOxCalibrationGUI(GUI)

# Run the whole GUI
GUI.mainloop()