from datetime import datetime
from datetime import timedelta

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
        self._studykey = 'study_records'

        if self._studykey not in self._datastore.get_keys():
            self._datastore.overwrite(db_key=self._studykey, db_value={})

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
        
        return str(self.get_timedelta(current_session['finish'], current_session['start']))

    def store_study(self, session):
        '''store the current study session by adding to existing or new'''

        timestamp = self._handletime.current_timestamp()
        datestamp = self._handletime.convert_timestamp(timestamp, 'date')

        records = self._datastore.get_value(self._studykey, {})
        today_record = records.get(datestamp, [])
        today_record.append(session)

        db = self._datastore.get()
        db[self._studykey][datestamp] = today_record
        
        self._datastore.write_all(db)
    
    def get_study_start(self):
        '''get the current study sessions starting time'''

        current_start = self._datastore.get_value('current_session', {}).get('start')
        return self._handletime.convert_timestamp(stamp=current_start)
    
    def get_timedelta(self, timestampA, timestampB):
        '''get the time delta in a presentable format of a timestamp'''

        return timedelta(seconds=self._handletime.time_difference(timestampA, timestampB))

    def tally_study(self, date=None):
        '''calculates the hours spent studying for the day'''

        datestamp = date or self._handletime.convert_timestamp(self._handletime.current_timestamp(), 'date')
        
        sessions = self._datastore.get_value(self._studykey, {}).get(datestamp, None)

        if sessions is None:
            return 0
        
        hour_tally = self.get_timedelta(0, 0)

        print(sessions)
        for session in sessions:
            tally = self.get_timedelta(session.get('finish', 0), session.get('start', 0))
           
            hour_tally = hour_tally + tally            

        return hour_tally

