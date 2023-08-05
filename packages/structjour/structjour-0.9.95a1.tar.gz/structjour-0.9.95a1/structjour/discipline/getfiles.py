'''
Created this module to mess with my own saved objects which needed updating as
structjour evolved. Its currenlty not used for anything but some of this might
be useful starting point. The load from xl stuff for example. Saving and loading
everything from DB now. But Edits done in excel have no current path to the db.
'''

import logging
import os
import pickle
import re
import sys

import pandas as pd

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from structjour.discipline.disciplined import getTradeSummary, getTradeTable
from structjour.view.dailycontrol import DailyControl


app = QApplication(sys.argv)


class manageSavedStuff:
    '''
    Manage the qt saves and the excel exports. Load one from the other
    '''

    def __init__(self, settings):
        self.settings = settings
        self.basedir = self.settings.value('journal')
        self.dasInfile = self.settings.value('dasInfile')
        self.ibInfile = self.settings.value('ibInfile')

        Year = '%Y'
        month = '%m'
        MONTH = '%B'
        day = '%d'
        DAY = '%A'
        scheme = self.settings.value('scheme')
        self.frmt = scheme.format(Year=Year, month=month, MONTH=MONTH, day=day, DAY=DAY)

    def getIbInfiles(self, indir):
        '''
        Using the glob for ib files in settings, search for ib files in the directory indir
        '''
        sglob = self.ibInfile

        rgx = re.sub('{\\*}', '.*', sglob)
        rgx = rgx + '$'
        d = indir

        # What should turn red here????
        if not d or not os.path.exists(d):
            logging.info(f'Cannot locate directory "{d}".')
            return None
        fs = list()
        for f in os.listdir(d):
            x = re.search((rgx), f)
            if x:
                fs.append(x.string)

        return fs

    def getSaveName(self, infile, theDate):
        '''
        Get the save name for infile. The format is taken from sumcontrol.getSaveName and needs to
        remain in sync.
        '''
        savename = f'''.{infile}{theDate.strftime('%A_%m%d')}.zst'''
        return savename

    def loadEverything(self, xlname, key):
        ldf, ts, fpentries = getTradeSummary(xlname, key)
        dframe, notes = getTradeTable(xlname, key)
        return ldf, ts, fpentries, dframe, notes

    def pickleADay(self, ts, entries, df, fname, note, key):
        '''Pickle ts, entries and df. Save note to the db'''
        d, fname = os.path.split(fname)
        if not os.path.exists(d):
            os.mkdir(d)
        fname, x = os.path.splitext(fname)
        fname = f'.{fname}.zst'
        fname = os.path.join(d, fname)
        with open(fname, "wb") as f:
            pickle.dump((ts, entries, df), f)

        dc = DailyControl(key)
        dc.commitNote(note)

    def pickleEmAll(self, tslist, fpentries, dframelist, fnameslist, dailynoteslist, keylist):
        'Utility to save a bunch of days'
        for ts, entries, df, fname, note, key in zip(tslist, fpentries, dframelist, fnameslist, dailynoteslist, keylist):
            self.pickleADay(ts, entries, df, fname, note, key)

    def loadXlFileAsTS(self, sumList):
        '''
        Deprecated
        Utility to load up the tradeSummary objects from the exported excel file and pickle them.
        Deprecated; the pickled objects are going away and in the DB exclusive storage, don't want
        to load to databse from a secondary source like an Excel file. This should morph to a
        emergency utility to load lost info into structjour and try to sync to db info if any.
        Finally let the user load it to DB.
        '''

        ldflist = list()
        dframelist = list()
        dailynoteslist = list()
        fpentrieslist = list()
        tslist = list()
        fnameslist = list()
        keylist = list()
        # srf = SumReqFields()
        for key in sumList:
            outdirfrmt = self.frmt + 'out/'
            outdir = key.strftime(outdirfrmt)
            outdir = os.path.join(self.basedir, outdir)
            for objs in sumList[key]:
                for xlfile in objs[1]:
                    if not objs[2]:
                        for xl in objs[1]:
                            logging.debug(xlfile)

                            xlname = os.path.join(outdir, xl)
                            ldf, ts, fpentries, dframe, notes = self.loadEverything(xlname, key)

                            ldflist.append(ldf)
                            tslist.append(ts)
                            fpentrieslist.append(fpentries)
                            dailynoteslist.append(notes)
                            dframelist.append(dframe)
                            fnameslist.append(xlname)
                            keylist.append(key)
        self.pickleEmAll(tslist, fpentrieslist, dframelist, fnameslist, dailynoteslist, keylist)

        return ldflist, tslist, dailynoteslist, fpentrieslist, dframelist, fnameslist, keylist

    def gatherDailySumList(self, begin):
        '''
        Utility
        Gets a dictionary of all input file and all saved files associated with each input file.
        Relies on the structjour file layout implemented using the 'scheme' and 'journal' settings.
        :begin: Earliest input file day
        '''
        if not os.path.exists(self.basedir):
            return
        os.chdir(self.basedir)
        # prefix=prefix

        now = pd.Timestamp.today()
        theDate = begin
        delt = pd.Timedelta(days=1)

        sumfiles = dict()

        while now >= theDate:
            indir = theDate.strftime(self.frmt)
            infiles = list()
            indir = os.path.join(self.basedir, indir)
            filesfordate = list()
            if os.path.exists(indir):
                fnames = os.listdir(indir)
                infiles.extend(self.getIbInfiles(indir))
                if self.dasInfile in fnames:
                    infiles.append(self.dasInfile)

                for inf in infiles:

                    # dirname = theDate.strftime('_%Y%m_%B/_%m%d_%A/out/')
                    dirname = os.path.join(indir, 'out/')
                    outdir = os.path.join(self.basedir, dirname)
                    xlfiles = []
                    if os.path.exists(outdir):
                        os.chdir(outdir)
                        fnames = os.listdir()
                        inf = os.path.splitext(inf)[0]
                        savedfile = self.getSaveName(inf, theDate)
                        for f in fnames:
                            if f.startswith(inf) and f.endswith('.xlsx'):
                                xlfiles.append(f)
                        if savedfile not in fnames:
                            savedfile = ''
                    filesfordate.append([inf, xlfiles, savedfile])
            sumfiles[theDate] = filesfordate
            theDate = theDate + delt
        return sumfiles


def main():
    settings = QSettings('zero_substance', 'structjour')
    begin = pd.Timestamp('2018-10-25')

    t = manageSavedStuff(settings)
    t.gatherDailySumList(begin)
    # everything = t.loadXlFileAsTS(l)
    # df = get


if __name__ == '__main__':
    main()
