# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 10:54:35 2018

@author: bartonjo

Functions to explore and save analyzed Keithley I/V data.

The Keithley software saves data with files named with the date and 
time. When recording data from the Keithley, a file is written by the 
user that has the file name and the description of the data set in a 
csv file that can be read by the functions below.  Here is an example 
of the first few lines of this notes file:

filename,description
2018_2_16_10_3_48.csv, First -3V bias test with no ops
2018_2_16_10_8_24.csv, test with no ops
2018_2_16_10_11_9.csv, test with no ops
2018_2_16_11_8_16.csv, test during power test shot 175463 during 14-21s

This notes file will be essential in discerning what the data show and
helping the user of these function determine convenient labels for each
data set. It is assumed this notes file is in the same directory as the
raw data given by the Keithley software. 

******Typical workflow steps:
(1) Set string variables assigned to the path and the file that 
describes each data-file.  Also, initialize this file.
In: path = '/Users/bartonjo/PyFiles/H-sensor/data/Diode Test -3Vbias/' 
In: notesname = 'bias test descriptions.csv'
In: runfile('h_sensor_acq.py')

(2) Obtain the notesname file in a dataframe called notes and all the
data in a list of dataframes contined in dfs.  The function will prompt
the user to define simple labels for each data set found in the 
notesname file. View the first few lines of the notes dataframe and the
first few lines of the first element of the dfs dataframe list.
In: notes, dfs = get_all_raw_ivs(path, notesname)
In: notes.head()
In: dfs[0].head()

(3) Explore the notes dataframe in order to find what files you want 
to analyze.
In: notes.head()
In: notes.tail()
In: notes.description.iloc[30:34]
In: notes.description.iloc[39]
In: notes.filename.iloc[39]
etc.

(4) Before plotting the specific files you want to analyze, determine
what indexes are needed to slice the dfs dataframe list.
In: dfs_indexes(dfs, istart=19)
In: n = [20,21,22,23,24,25,26,27,28]
In: m = [39,32,29,30,31,34,33,35,38,36,37]

(5) Create new dataframe lists from the slicing lists (n and m above).
In: dfn = slice_dfs(dfs,n)
In: dfm = slice_dfs(dfs,m)

(6) Plot the data from the sliced list and display the notes on these
files.
In: plt.figure()
In: plot_dfs(dfn, xdata='t_s', ydata='i', yfactor=1e6)
In: notes.iloc[n]
In: plt.figure()
In: plot_dfs(dfm, xdata='t_s', yfactor=1e6)
In: notes.iloc[m]
In: notes.description.iloc[31]

(7) Save these sliced dataframe lists with their simple labels, so they
can be called up again easily.
In: save_dfs(dfn, 'lp_rack_tests.h5')
In: save_dfs(dfm, 'dimes_loc_tests.h5')

(8) Read in the saved dataframes from hdf5 files and put them into a 
dataframe list as before. You can also load in the notes file again, if
necessary. Repeat steps 3-7 as needed.
In: dflp = read_ivs('lp_rack_tests.h5')
In: dfds = read_ivs('dimes_loc_tests.h5')
In: notes = get_notes(path+notesname)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_sensor_data(path, fname, label):
    '''
    Input the file name (fname) & path and return a dataframe from the 
    csv file.  Assume the column names and orders are always the same, 
    given by the Keithley acquisition software.
    '''
    # Initialize column names
    oldnames = ['Smu1_Time(1)(1)','Smu1_V(1)(1)','Smu1_I(1)(1)']
    newnames = ['t_s','v','i']
    # Import the data from the csv file
    sdata = pd.read_csv(path+fname, usecols=oldnames)
    sdata.columns = newnames
    sdata['fname'] = fname  # keep the file name with the data
    sdata['label'] = label
    return sdata

def get_notes(notespath):
    '''
    Return a dataframe of the csv notes file relating the cryptic 
    filename assigned by the Keithley software to the description of 
    the measurement.
    '''
    return pd.read_csv(notespath)

def get_all_raw_ivs(path, notesname):
    '''
    Input a directory path in the path variable. 
    
    Return the csv file with notesname. It contains the 
    notes about certain files. (This file may not have notes on every 
    file!)
    
    The user is required to give a simple label for each data file in 
    the provied path.
    
    Return all the dataframes obtained from the directory as well.
    '''
    # get the notes file (assumed csv)
    try:
        notes = get_notes(path+notesname)
    except:
        print('no notes for this directory')
        notes = 0
    
    # loop through directory and get dataframes from each csv data file
    dfs = []  #initialize dataframe list
    for file in os.listdir(path):
        if file.endswith('.csv'):
            try:
                if file in str(notes.filename):
                    n = notes.index[notes.filename == file][0]
                    print('\n' + notes.filename[n])
                    print(notes.description[n])
                    s = 'Provide a short label for this data:  '
                    label = input(s)
                else:
                    label = 'not in notes'
                dfs.append(get_sensor_data(path, file, label))
            except:
                continue
    
    return notes, dfs


def plot_dfs(dfs,xdata='t_s',ydata='i', yfactor=1, points=False):
    '''
    Plot I vs V or I vs time or V vs time for all dataframes in the 
    dfs dataframe list.
    
    dfs has columns i, v, and t_s for current (A), voltage (V) and 
    time (seconds), respectively.
    '''
    label = {'v':'V [V]', 't_s':'Time [s]'}
    if len(dfs) > 50:
        l = range(1)
        d = []
        d.append(dfs)
        dfs = d
    else:
        l = range(len(dfs))
    for i in l:
        if ydata == 'i':
            if yfactor == 1:
                label['i'] = 'I [A]'
            elif yfactor == 1e6:
                label['i'] = r'I [$\mu$A]'
            elif yfactor == 1e9:
                label['i'] = 'I [nA]'
            else:
                print('NOTE: y-axis units are muliplied by ', yfactor)
            if points==False:
                plt.plot(dfs[i][xdata][:], dfs[i][ydata][:]*yfactor,
                             label=dfs[i].label[0])
            else:
                plt.plot(dfs[i][xdata][:], dfs[i][ydata][:]*yfactor,
                         '-s', label=dfs[i].label[0])
        else:
            if points==False:
                plt.plot(dfs[i][xdata][:], dfs[i][ydata][:],
                             label=dfs[i].label[0])
            else:
                plt.plot(dfs[i][xdata][:], dfs[i][ydata][:],
                         '-s', label=dfs[i].label[0])
    plt.ylabel(label[ydata])
    plt.xlabel(label[xdata])
    plt.legend(loc='best', fontsize=10)
    plt.show()
    
def slice_dfs(dfs,n):
    '''
    Return a dataframe list taken from arbitrary elements from dfs. 
    The variable n is a list of the arbitrary elements that will slice 
    dfs. (e.g. n = [3, 6, 7, 10, 13, 18])
    '''
    newdfs = []
    for i in range(len(n)):
        newdfs.append(dfs[n[i]])
    return newdfs

def dfs_indexes(dfs, istart=0, iend=0):
    '''
    Print out the dfs index next to its filename, so that it is easier
    to connect the notes to the dfs dataframe list.
    
    If you only want to show part of the dfs list, then give a
    starting index = istart and/or and ending index = iend. 
    '''
    if (iend == 0) or (iend < istart):
        iend = len(dfs)
    for i in range(len(dfs)):
        if (i >= istart) and (i <= iend):
            print(i, '  ', dfs[i].label[0], '  ', dfs[i].fname[0])
    
def save_dfs(dfs, filename):
    '''
    Save specific files with more intuitive file names, using 
    their simple labels.
    
    n is a list of dfs indexes that identify the dataframes you want to
    save.

    dfs is the dataframe list.

    filename is the hdf5 file name where all the data will be saved.
    '''
    for i in range(len(dfs)):
        dfs[i].to_hdf(filename,dfs[i].label[0])  # the label is the key
        print('Saved ' + dfs[i].label[0] + ' dataframe to ' + filename)
    
def read_ivs(filename):
    '''
    Read in the hdf5 file that has multiple dataframes (i.e. multiple
    keys) and return a list of dataframes called dfs.
    '''
    dfs = []  # initialize list
    store = pd.HDFStore(filename)
    for key in store.keys():
        dfs.append(pd.read_hdf(filename, key=key))
    return dfs
    
    
    