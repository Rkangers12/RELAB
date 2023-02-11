from tools.handler import Handler
from util.handle_times import HandleTimes


class SessionTrack:
    def __init__(self, session_key, action, datastore=None):

        self._datastore = datastore or Handler()
        self._handletime = HandleTimes()
        self._record = session_key  # e.g. 'studyRecords'
        self._action = action  # e.g. 'studying'

    def activate(self, user):
        """activate session mode and record start of session"""

        session = {"start": self._handletime.current_timestamp()}

        self._datastore.overwrite_nested(
            ["users", user, "sessions"], self._action, db_value=True
        )
        self._datastore.overwrite_nested(
            ["users", user, "sessions"], "currentSession", session
        )

    def deactivate(self, user):
        """deactivate session mode and record end of session"""

        session = self._datastore.get_nested_value(
            ["users", user, "sessions", "currentSession"]
        )
        session["finish"] = self._handletime.current_timestamp()

        self._datastore.overwrite_nested(
            ["users", user, "sessions"], self._action, db_value=False
        )
        self.store_session(session, user)

        # re-initialise current_session
        self._datastore.overwrite_nested(
            ["users", user, "sessions"], "currentSession", {}
        )

        return str(self._handletime.get_timedelta(session["finish"], session["start"]))

    def store_session(self, session, user):
        """store the current session by adding to existing or new"""

        timestamp = self._handletime.current_timestamp()
        datestamp = self._handletime.convert_timestamp(timestamp, "date")

        records = self._datastore.get_nested_value(
            ["users", user, "sessions", self._record],
            default={},
        )
        today_record = records.get(datestamp, [])
        today_record.append(session)

        self._datastore.overwrite_nested(
            ["users", user, "sessions", self._record], datestamp, db_value=today_record
        )

    def get_session_start(self, user):
        """get the current session's starting time"""

        current_start = self._datastore.get_nested_value(
            ["users", user, "sessions", "currentSession", "start"]
        )
        return self._handletime.convert_timestamp(stamp=current_start)

    def tally_activity(self, user, date=None):
        """calculates the hours spent partaking in activity for the day"""

        datestamp = date or self._handletime.convert_timestamp(
            self._handletime.current_timestamp(), "date"
        )

        sessions = self._datastore.get_nested_value(
            ["users", user, "sessions", self._record, datestamp]
        )

        hour_tally = self._handletime.get_timedelta(0, 0)

        if sessions is None:
            return hour_tally

        for session in sessions:
            tally = self._handletime.get_timedelta(
                session.get("finish", 0), session.get("start", 0)
            )

            hour_tally = hour_tally + tally

        return hour_tally

    def period_dates(self, period, user):
        """called when period at end and provide an dates for a given period"""

        if period == "week":
            # check if week ended, exit False if not.
            period_end = self._handletime.calculate_days(period="week")

        if period == "month":
            # check if month ended, exit False if not
            period_end = self._handletime.calculate_days(period="month")[1]

        if period == "year":
            # check if year ended, exit False if not
            period_end = self._handletime.calculate_days(period="year")

        dates = []
        current = self._handletime.current_timestamp()

        while period_end > 0:

            period_end -= 1
            minus_days = period_end * 86400
            dates.append(
                self._handletime.convert_timestamp(current - minus_days, "date")
            )

        hour_tally = self._handletime.get_timedelta(0, 0)
        for date_stamp in dates:
            hour_tally = hour_tally + self.tally_activity(user, date_stamp)

        return hour_tally
