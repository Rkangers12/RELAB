from datetime import datetime
from os import times
from time import time

from store.handler import Handler


class HandleTimes:

    def current_timestamp(self):
        '''return the current timestamp'''

        now = datetime.now()
        return int(datetime.timestamp(now))
    
    def convert_timestamp(self, stamp, date_format=None):
        '''convert the current timestamp into date or hhmm'''

        dt_object = datetime.fromtimestamp(stamp)

        if date_format == 'date':
            dt_object = dt_object.strftime("%d%m%y")
        elif date_format == 'time':
            dt_object = dt_object.strftime("%H%M")

        return dt_object

    def time_difference(self, timestampA, timestampB):
        '''calculate seconds difference between two timestamps'''

        return timestampA - timestampB


class StudyTrack:
    
    def __init__(self, datastore=None):

        self._datastore = datastore or Handler()
        self._handletime = HandleTimes()

        if 'study_records' not in self._datastore.get_keys():
            self._datastore.overwrite(db_key='study_records', db_value={})

    def activate(self):
        '''activate study mode and record start of session'''
        
        timestamp = self._handletime.current_timestamp()
        
        current_session = {'start': timestamp}

        self._datastore.overwrite(db_key='studying', db_value=True)
        self._datastore.overwrite(db_key='current_session', db_value=current_session)

    def deactivate(self):
        '''deactivate study mode and record end of session'''

        timestamp = self._handletime.current_timestamp()
        
        current_session = self._datastore.get_value('current_session')
        current_session['finish'] = timestamp

        self._datastore.overwrite(db_key='studying', db_value=False)
        self.store_study(current_session)

        # re-initialise current_session
        self._datastore.overwrite(db_key='current_session', db_value={})

    def store_study(self, session):
        '''store the current study session by adding to existing or new'''

        timestamp = self._handletime.current_timestamp()
        datestamp = self._handletime.convert_timestamp(timestamp, 'date')

        records = self._datastore.get_value('study_records', {})
        today_record = records.get(datestamp, [])
        today_record.append(session)

        db = self._datastore.get()
        db['study_records'][datestamp] = today_record
        
        self._datastore.write_all(db)
        