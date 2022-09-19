from store.handler import Handler
from util.handle_times import HandleTimes

class SessionTrack:
    
    def __init__(self, session_key, active_key, datastore=None):
        
        self._datastore = datastore or Handler()
        self._handletime = HandleTimes()
        self._session_key = session_key  # e.g. 'study_records'
        self._active_key = active_key  # e.g. 'studying'

        if self._session_key not in self._datastore.get_keys():
            self._datastore.overwrite(db_key=self._session_key, db_value={})

    def activate(self):
        '''activate session mode and record start of session'''
        
        timestamp = self._handletime.current_timestamp()
        
        current_session = {'start': timestamp}

        self._datastore.overwrite(db_key=self._active_key, db_value=True)
        self._datastore.overwrite(db_key='current_session', db_value=current_session)

    def deactivate(self):
        '''deactivate session mode and record end of session'''

        timestamp = self._handletime.current_timestamp()
        
        current_session = self._datastore.get_value('current_session')
        current_session['finish'] = timestamp

        self._datastore.overwrite(db_key=self._active_key, db_value=False)
        self.store_session(current_session)

        # re-initialise current_session
        self._datastore.overwrite(db_key='current_session', db_value={})
        
        return str(self._handletime.get_timedelta(current_session['finish'], current_session['start']))

    def store_session(self, session):
        '''store the current session by adding to existing or new'''

        timestamp = self._handletime.current_timestamp()
        datestamp = self._handletime.convert_timestamp(timestamp, 'date')

        records = self._datastore.get_value(self._session_key, {})
        today_record = records.get(datestamp, [])
        today_record.append(session)

        db = self._datastore.get()
        db[self._session_key][datestamp] = today_record
        
        self._datastore.write_all(db)
    
    def get_session_start(self):
        '''get the current sessions' starting time'''

        current_start = self._datastore.get_value('current_session', {}).get('start')
        return self._handletime.convert_timestamp(stamp=current_start)
    
    def tally_activity(self, date=None):
        '''calculates the hours spent partaking in activity for the day'''

        datestamp = date or self._handletime.convert_timestamp(self._handletime.current_timestamp(), 'date')
        
        sessions = self._datastore.get_value(self._session_key, {}).get(datestamp, None)
        
        hour_tally = self._handletime.get_timedelta(0, 0)

        if sessions is None:
            return hour_tally

        for session in sessions:
            tally = self._handletime.get_timedelta(session.get('finish', 0), session.get('start', 0))
           
            hour_tally = hour_tally + tally            

        return hour_tally

    def period_dates(self, period):
        '''called when period at end and provide an dates for a given period'''
        
        if period == 'week':
            # check if week ended, exit False if not.
            period_end = self._handletime.calculate_days(period='week')

        if period == 'month':
            # check if month ended, exit False if not
            period_end = self._handletime.calculate_days(period='month')[1]

        if period == 'year':
            # check if year ended, exit False if not
            period_end = self._handletime.calculate_days(period='year')
            
        dates = []
        current = self._handletime.current_timestamp()

        while period_end > 0:
            
            period_end -= 1
            minus_days = period_end * 86400
            dates.append(self._handletime.convert_timestamp(current - minus_days, 'date'))

        hour_tally = self._handletime.get_timedelta(0, 0)
        for date_stamp in dates:
            hour_tally = hour_tally + self.tally_activity(date_stamp)
        
        return hour_tally
