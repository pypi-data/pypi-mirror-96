# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
'''
Populate the Qt forms. Generally layoutforms populates the trade summaries for QT and layoutsheets
populates the form entries for excel.

Created on April 14, 2019

@author: Mike Petersen
'''

import datetime as dt
import logging
import os
import pickle

import numpy as np
import pandas as pd

from structjour.definetrades import DefineTrades
from structjour.stock.utilities import qtime2pd

from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.dailynotescrud import DailyNotesCrud
from structjour.thetradeobject import SumReqFields, runSummaries, setTradeSummaryHeaders


# pylint: disable=C0103, C1801

class LayoutForms:
    '''
    Run theTradeObject summaries to get the tto DataFrame and populate
    the trade form for each trade.
    '''

    def __init__(self, sc, jf, df):
        '''
        Initialize the obect and create a Widget dictionary using the same keys as the keys to the
        tto object to populate the data.
        '''
        self.jf = jf
        self.df = df
        if self.df is not None:
            self.pickleitnow()
        self.ts = dict()
        self.entries = dict()
        rc = SumReqFields()
        self.timeFormat = '%H:%M:%S'

        self.sc = sc
        self.tradeSummaries = None

        # Widget Dictionary. Keys are same keys for TheTradeObject.TheTrade object
        wd = dict()
        wd[rc.name] = sc.ui.title
        wd[rc.acct] = sc.ui.account
        wd[rc.strat] = sc.ui.strategy
        # wd[rc.link1] = sc.ui.link
        wd[rc.pl] = sc.ui.pl
        wd[rc.start] = sc.ui.start
        wd[rc.dur] = sc.ui.dur
        wd[rc.shares] = sc.ui.pos
        wd[rc.mktval] = sc.ui.mkt
        wd[rc.targ] = sc.ui.targ
        wd[rc.targdiff] = sc.ui.targDiff
        wd[rc.stoploss] = sc.ui.stop
        wd[rc.sldiff] = sc.ui.stopDiff
        wd[rc.rr] = sc.ui.rr
        wd[rc.realrr] = sc.ui.realRR
        wd[rc.maxloss] = sc.ui.maxLoss
        wd[rc.mstkval] = sc.ui.lost
        wd[rc.mstknote] = sc.ui.sumNote
        wd[rc.entry1] = sc.ui.entry1
        wd[rc.entry2] = sc.ui.entry2
        wd[rc.entry3] = sc.ui.entry3
        wd[rc.entry4] = sc.ui.entry4
        wd[rc.entry5] = sc.ui.entry5
        wd[rc.entry6] = sc.ui.entry6
        wd[rc.entry7] = sc.ui.entry7
        wd[rc.entry8] = sc.ui.entry8
        wd[rc.exit1] = sc.ui.exit1
        wd[rc.exit2] = sc.ui.exit2
        wd[rc.exit3] = sc.ui.exit3
        wd[rc.exit4] = sc.ui.exit4
        wd[rc.exit5] = sc.ui.exit5
        wd[rc.exit6] = sc.ui.exit6
        wd[rc.exit7] = sc.ui.exit7
        wd[rc.exit8] = sc.ui.exit8
        wd[rc.time1] = sc.ui.time1
        wd[rc.time2] = sc.ui.time2
        wd[rc.time3] = sc.ui.time3
        wd[rc.time4] = sc.ui.time4
        wd[rc.time5] = sc.ui.time5
        wd[rc.time6] = sc.ui.time6
        wd[rc.time7] = sc.ui.time7
        wd[rc.time8] = sc.ui.time8
        wd[rc.eshare1] = sc.ui.share1
        wd[rc.eshare2] = sc.ui.share2
        wd[rc.eshare3] = sc.ui.share3
        wd[rc.eshare4] = sc.ui.share4
        wd[rc.eshare5] = sc.ui.share5
        wd[rc.eshare6] = sc.ui.share6
        wd[rc.eshare7] = sc.ui.share7
        wd[rc.eshare8] = sc.ui.share8
        wd[rc.diff1] = sc.ui.diff1
        wd[rc.diff2] = sc.ui.diff2
        wd[rc.diff3] = sc.ui.diff3
        wd[rc.diff4] = sc.ui.diff4
        wd[rc.diff5] = sc.ui.diff5
        wd[rc.diff6] = sc.ui.diff6
        wd[rc.diff7] = sc.ui.diff7
        wd[rc.diff8] = sc.ui.diff8
        wd[rc.pl1] = sc.ui.pl1
        wd[rc.pl2] = sc.ui.pl2
        wd[rc.pl3] = sc.ui.pl3
        wd[rc.pl4] = sc.ui.pl4
        wd[rc.pl5] = sc.ui.pl5
        wd[rc.pl6] = sc.ui.pl6
        wd[rc.pl7] = sc.ui.pl7
        wd[rc.pl8] = sc.ui.pl8
        wd[rc.explain] = sc.ui.explain
        wd[rc.notes] = sc.ui.notes

        self.rc = rc
        self.wd = wd
        self.imageNames = None
        self.sc.loadLayoutForms(self)

#######

    def getStoredTradeName(self):
        '''
        The name for the pickled transaction based trades table for the current, active statement.
        {outdir}/.{infile}.zst
        '''
        name = f'.trades{self.jf.theDate.strftime(self.jf.dayformat)}.zst'
        fname = os.path.normpath(os.path.join(self.jf.outdir, name))
        return fname

    def pickleitnow(self):
        '''
        Store the transaction based Dataframe as (getStoredTradeName()) for the input file just
        after it was loaded from file.
        '''
        fname = self.getStoredTradeName()
        d, name = os.path.split(fname)
        if not os.path.exists(d):
            os.makedirs(d)
        with open(fname, "wb") as f:
            pickle.dump(self.df, f)

    def saveTheTradeObject(self, name):
        from structjour.statements.statementcrud import TradeCrud
        if not self.ts or not self.entries:
            return
        ibdb = StatementDB()
        tcrud = TradeCrud()
        self.ts = ibdb.updateTradeSummariesSA(self.ts)
        # self.ts = ibdb.updateTradeSummaries(self.ts)
        # tcrud.updateTradeSummaries(self.ts)
        self.sc.ui.useDatabase.setChecked(True)

    def loadTradesFromDB(self, theDate=None):
        '''
        User tweak-- if DAS or IB import files are checked when the load button is clicked,
        Change the selected radio to useDatabase and return. Update will show if there are
        any DB trades to load.
        '''
        if self.sc.ui.dasImport.isChecked() or self.sc.ui.ibImport.isChecked():
            self.sc.ui.useDatabase.setChecked(True)
            self.sc.dbDefault(True)
            return 1

        ibdb = StatementDB()
        df = ibdb.getStatement(theDate)
        tu = DefineTrades('DB')
        self.df, ldf = tu.processDBTrades(df)

        ts, self.entries = ibdb.getTradeSummariesSA(theDate)
        if not ts:
            logging.info(f"No user data has been saved for {theDate.strftime('%A %B %d')}.")
            return None
        self.ts = setTradeSummaryHeaders(ts)

        logging.info('load up the trade names now')
        tradeSummaries = []
        self.sc.ui.tradeList.clear()
        for key in self.ts:
            self.sc.ui.tradeList.addItem(key)
            tradeSummaries.append(self.ts[key])

        # Load dailyote
        dailyNoteModel = DailyNotesCrud(theDate)
        note = dailyNoteModel.getNote()
        self.dailyNoteModel = dailyNoteModel
        if not note:
            note = ""
        self.sc.ui.dailyNote.setText(note)

        inf = self.sc.ui.infileEdit.text()
        windowTitle = f"{self.sc.baseWindowTitle}: {inf}: User Data Loaded"
        self.sc.setWindowTitle(windowTitle)

        # In prep to do the mistake summary and excel export, return the list it uses now
        # It might be good to use the dict self.ts instead
        return tradeSummaries

    def runTtoSummaries(self, ldf):
        '''
        This script creates the tto object for each trade in the input file and appends it to a
        list It also creates a generic name for assoiated images. That name will be altered for
        speific images that may be created via the stock api or added by the user. Finally the
        sript creates the tradeList key and adds it to the tradeList widget. The key is used to
        retrieve the tto data from the tradeList widget currentText selection.
        :params ldf: A list of DataFrames. Each df is a complete trade from initial purchace or
                    hold to 0 shares or hold.
        '''

        newtradeSummaries, newts, newentries, initialImageNames = runSummaries(ldf)
        assert len(ldf) == len(initialImageNames)
        self.sc.ui.tradeList.clear()

        self.imageNames = initialImageNames
        self.ts = newts
        self.entries = newentries
        for tkey in newts:
            self.sc.ui.tradeList.addItem(tkey)
        self.tradeSummaries = newtradeSummaries

        return self.tradeSummaries

    def populateTradeSumForms(self, key):
        '''
        Use the widget dictionary (self.wd) and tto to populate the form. The images and related
        widgets are handled seperately in sc.setChartWidgets(). Then images loaded
        '''

        tto = self.ts[key]
        # Catch legacy object fix
        if 'P / L' in tto.keys():
            tto.rename(columns={'P / L': 'PnL'}, inplace=True)
            self.sc.setStatusTip('Legacy object. Please save and re-load')
        for wkey in self.wd:
            daVal = tto[wkey].unique()[0]
            if isinstance(daVal, (np.floating, float)):
                daVal = '{:.02f}'.format(daVal)
            elif isinstance(daVal, (np.integer, int)):
                daVal = '{}'.format(daVal)
            elif isinstance(daVal, (pd.Timestamp, dt.datetime, np.datetime64)):
                daVal = pd.Timestamp(daVal)
                daVal = daVal.strftime(self.timeFormat)
            elif wkey == "Strategy":
                continue
            elif not isinstance(daVal, str):
                logging.warning(f"{wkey} is {str(type(daVal))}: {daVal}. Changing to empty str")
                daVal = ''
                # raise TypeError(msg)
            self.wd[wkey].setText(daVal)

        strat = tto['Strategy'].unique()[0]
        self.sc.loadStrategies(strat)

        # Some trades lack the id key -- trades that have no user data saved -- The id will be added to tto when data has been saved
        iid = None
        if 'id' in tto:
            iid = int(tto['id'].unique()[0])
        self.sc.populateTags(tsum_id=iid)
        self.sc.setDailyPnL()

        self.sc.setChartWidgets()
        iname1 = self.sc.ui.chart1Name.text()
        iname2 = self.sc.ui.chart2Name.text()
        iname3 = self.sc.ui.chart3Name.text()
        outdir = self.sc.getOutdir()
        ipathfilename1 = os.path.join(outdir, iname1)
        ipathfilename2 = os.path.join(outdir, iname2)
        ipathfilename3 = os.path.join(outdir, iname3)
        self.sc.loadImageFromFile(self.sc.ui.chart1, ipathfilename1)
        self.sc.loadImageFromFile(self.sc.ui.chart2, ipathfilename2)
        self.sc.loadImageFromFile(self.sc.ui.chart3, ipathfilename3)
        self.sc.diffTarget(self.sc.ui.targ.text())
        self.sc.stopLoss(self.sc.ui.stop.text())

    def getEntries(self, key):
        '''
        The data structure is:
        [price, time, share, pl, diff, entryOrExit]. Share is positive for buy, negative for sell.
        :params key: Trade name from the tradeList widget
        '''
        entries = self.entries[key]
        return entries

    def updateTsDictionary(self):
        '''
        Up date older versions of the dictionary that lack some keys. Specifically update the
        chart widget elements
        '''
        for c, interval in zip(['chart1', 'chart2', 'chart3'], [1, 5, 15]):
            for key in self.ts:
                if c not in self.ts[key].keys():
                    self.ts[key][c] = ''
                    start = pd.Timestamp('2175-01-02')
                    end = pd.Timestamp('2175-01-01')
                    self.ts[key][c + 'Start'] = start
                    self.ts[key][c + 'End'] = end
                    self.ts[key][c + 'Interval'] = interval

    def getChartData(self, key, ckey):
        '''
        Get the chart data from the tradeObject
        :params key: Trade name from the tradeList widget
        :params ckey: The widget name of the clickLabel will be one of 'chart1', 'chart2', or
                    'chart3'
        '''
        from PyQt5.QtCore import QDate

        assert ckey in ('chart1', 'chart2', 'chart3')
        if key not in self.ts.keys():
            return None, None, None, None
        tto = self.ts[key]
        if 'chart1' not in tto.keys():
            self.updateTsDictionary()
        if ckey not in tto.columns:
            # Set some default vals for begin, end and interval if no chart entry exists
            begin = tto['Time1'].unique()[0]
            end = None
            for i in range(1, 9):
                x = tto['Time' + str(i)].unique()[0]
                if x:
                    end = x
                else:
                    break
            interval = 1 if ckey == 'chart1' else 5 if ckey == 'chart2' else 15

            return ['', begin, end, interval]

        name = tto[ckey].unique()[0]
        begin = tto[ckey + 'Start'].unique()[0]
        end = tto[ckey + 'End'].unique()[0]
        if not isinstance(begin, (pd.Timestamp, dt.datetime, np.datetime64, QDate)) or (
                not isinstance(end, (pd.Timestamp, dt.datetime, np.datetime64, QDate))):
            logging.warning(f'WARNING: date type is not standard: {type(begin)}')
            return None

        interval = int(tto[ckey + 'Interval'].unique()[0])

        return [name, begin, end, interval]

    def setChartTimes(self, key, ckey, data):
        '''
        Store the chart begin and end times with the trade info
        :key: Trade name from the tradeList
        :ckey: The widget name of the clickLabel. Will be one of ['chart1', 'chart2', 'chart3']
        :data: (start, end) timestring or timestamps
        '''
        data[0] = pd.Timestamp(data[0])
        data[1] = pd.Timestamp(data[1])
        self.ts[key][ckey + 'Start'] = data[0]
        self.ts[key][ckey + 'End'] = data[1]

    def setChartData(self, key, data, ckey):
        '''
        Store the chart data in the trade object
        :params key: Trade name from the tradeList
        :params data: a list or list of lists. Each has: [start, end, interval, name]
        :params ckey: The widget name of the clickLabel will be one of 'chart1', 'chart2', or
                    'chart3'
        '''
        if self.ts:

            assert len(self.ts[key] == 1)
            if isinstance(ckey, list):
                for k, d in zip(ckey, data):
                    assert k in ['chart1', 'chart2', 'chart3']
                    self.ts[key].at[0, k] = d
                    return
            assert ckey in ['chart1', 'chart2', 'chart3']
            self.ts[key][ckey] = data[0]
            self.ts[key][ckey + 'Start'] = data[1]
            self.ts[key][ckey + 'End'] = data[2]
            self.ts[key][ckey + 'Interval'] = data[3]

    def toggleTimeFormat(self, key):
        '''
        reload the time values for the trade time entries. This is done after toggling the date
        format to use (includes date info or not).
        '''
        tto = self.ts[key]
        twidgets = [self.sc.ui.time1, self.sc.ui.time2, self.sc.ui.time3, self.sc.ui.time4,
                    self.sc.ui.time5, self.sc.ui.time6, self.sc.ui.time7, self.sc.ui.time8]
        for i, widg in enumerate(twidgets):
            daVal = tto['Time' + str(i + 1)].unique()[0]
            if isinstance(daVal, (pd.Timestamp, dt.datetime, np.datetime64)):
                daVal = pd.Timestamp(daVal)
                daVal = daVal.strftime(self.timeFormat)
            widg.setText(daVal)

    def setTargVals(self, key, targ, diff, rr, realrr):
        '''Store the values affected by a change in the target value'''

        rc = self.rc
        tto = self.ts[key]
        tto[rc.targ] = targ
        tto[rc.targdiff] = diff
        tto[rc.realrr] = realrr
        if rr:
            tto[rc.rr] = rr

    def setStopVals(self, key, stop, diff, rr, maxloss):
        '''
        When the user enters a value in stoploss several things happen in the callback then
        here we store all the related values in tto. If the widgets have been marked clean,
        determine if a loss in PL exceeds maxloss. If so, save the data to tto
        '''

        rc = self.rc
        tto = self.ts[key]
        tto[rc.stoploss] = stop
        tto[rc.sldiff] = diff
        if rr:
            tto[rc.rr] = rr
        maxloss = 0.0 if not maxloss else maxloss
        tto[rc.maxloss] = maxloss

        lost = 0.0
        note = ''
        clean = tto['clean'].unique()[0]
        name = tto[rc.name].unique()[0]
        pl = tto[rc.pl].unique()[0]
        if isinstance(pl, bytes):
            pl = 0
        if maxloss:
            if 'long' in name.lower() and diff >= 0:
                return lost, note, clean
            if 'short' in name.lower() and diff <= maxloss:
                return lost, note, clean
            # assert maxloss < 0
            if maxloss > pl:
                lost = maxloss - pl
                tto[rc.mstkval] = lost
                note = 'Loss exceeds max loss!'
                tto[rc.mstknote] = note
                ibdb = StatementDB()
                if 'id' in tto:
                    ibdb.updateMstkValsSA(tto['id'].unique()[0], lost, note)
        return (lost, note, clean)

    def setClean(self, key, b):
        '''
        Set clean in self.ts to b. The clean value is used to determine if there is user input
        to maintain in the mistake note/mistake val.
        :params key: The current trade name is the key found in the tradeList Combo box
        :params b: bool
        '''
        self.ts[key]['clean'] = b

    def setMstkVals(self, key, val, note):
        '''
        Set mstkval and mstknote in self.ts
        :params key: The current trade name is the key found in the tradeList Combo box
        :params val: Float, The value for the 'lost' widget
        :params note: The value for the sumNotes widget
        '''
        self.ts[key][self.rc.mstkval] = val
        self.ts[key][self.rc.mstknote] = note

    def setExplain(self, key, val):
        '''
        Set explain in self.ts
        :params key: The current trade name is the key found in the tradeList Combo box
        :params val: The value for the explain widget
        '''
        self.ts[key][self.rc.explain] = val

    def setNotes(self, key, val):
        '''
        Set notes in self.ts
        :params key: The current trade name is the key found in the tradeList Combo box
        :params val: The value for the notes widget
        '''
        self.ts[key][self.rc.notes] = val

    def setStrategy(self, key, val):
        '''Sets strategy in self.ts to val'''
        self.ts[key][self.rc.strat] = val

    def getStrategy(self, key):
        '''Retrieves the current strategy from self.ts'''
        val = self.ts[key][self.rc.strat].unique()[0]
        return val

    def getImageName(self, key, wloc, uinfo=''):
        '''
        This is an image name for a pasted image. We don't know the interval or time limits beyond
        the trade times. Remove any interval info, add the widget name (e.g. 'chart1') to the
        generic name.
        :params key: The name of the trade from the tradeList
        :params wloc: The name of the clickLabel widget
        :params uinfo: Misc string to add to the name
        '''

        name = self.ts[key][wloc].unique()[0]
        data = self.getChartData(key, wloc)
        if name:
            n, ext = os.path.splitext(name)
            if n.endswith('min'):
                n = n[:-5]
            wwloc = wloc
            if n.find(wwloc) > 0:
                wwloc = ''
            if uinfo and n.find(uinfo) > 0:
                uinfo = ''
            n = n + wwloc + uinfo + ext
        elif data:
            # Just in case the name is missing
            b = data[1]
            e = data[2]

            begin = qtime2pd(b)
            end = qtime2pd(e)
            delt = end - begin
            bstring = begin.strftime('%H%M%S')
            estring = delt.__str__().replace(':', '.')
            n = 'Trade{}_{}_{}_{}_{}.png'.format(key, bstring, estring, wloc, uinfo)
            n = n.replace(' ', '_')
        if data[0] != n:
            data[0] = n
            self.setChartData(key, data, wloc)
        return n

    def getImageNameX(self, key, wloc):
        '''
        This is a chart name for which we know the candle interval because we gave that parameter
        to the stock api.
        '''
        name = key.replace(' ', '_')
        data = self.getChartData(key, wloc)

        # if not data:
        #     raise ValueError('Raise the error to call attention to programming deficit')

        b = pd.Timestamp(qtime2pd(data[1]))
        e = pd.Timestamp(qtime2pd(data[2]))

        delt = e - b
        bstring = b.strftime('%H%M%S')
        estring = delt.__str__().replace(':', '.')
        istring = str(data[3]) + 'min'
        n = 'Trade{}_{}_{}_{}.png'.format(
            name, bstring, estring, istring)
        n = n.replace(' ', '_')
        if data[0] != n:
            data[0] = n
            self.setChartData(key, data, wloc)
        return n
