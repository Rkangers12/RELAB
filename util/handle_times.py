import calendar
from datetime import date, datetime
from datetime import timedelta


class HandleTimes:
    def current_timestamp(self):
        """return the current timestamp"""

        now = datetime.now()
        return int(datetime.timestamp(now))

    def convert_timestamp(self, stamp, date_format=None):
        """convert the current timestamp into date or hhmm"""

        dt_object = datetime.fromtimestamp(stamp)

        if date_format == "date":
            dt_object = dt_object.strftime("%d%m%y")
        elif date_format == "time":
            dt_object = dt_object.strftime("%H%M")
        elif date_format == "clean":
            dt_object = dt_object.strftime("%c")

        return dt_object

    def time_difference(self, timestampA, timestampB):
        """calculate seconds difference between two timestamps"""

        return timestampA - timestampB

    def get_timedelta(self, timestampA, timestampB):
        """get the time delta in a presentable format of a timestamp"""

        return timedelta(seconds=self.time_difference(timestampA, timestampB))

    def check_end_week(self):
        """check if it's the end of the week"""

        # week check - check if it is a sunday
        if date.today().weekday() == 6:
            return True

        return False

    def check_end_month(self):
        """check if it's the end of the month"""

        days_in_month = self.calculate_days(period="month")

        if days_in_month:
            # month check - check if it's the last day of the month
            if datetime.now().day == days_in_month[1]:
                return True

        return False

    def check_end_year(self):
        """check if it's the end of the year"""

        now = datetime.now()
        # year check - check if it's 31st December
        if now.month == 12 and now.day == 31:
            return True

        return False

    def calculate_days(self, year=None, month=None, period=None):
        """check number of days for a given period"""

        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        if period == "month":
            return calendar.monthrange(year, month)

        if period == "year":
            return 366 if calendar.isleap(year) else 365

        if period == "week":
            return 7

    def format_a_day(self, day=None, weekday=False, income=True):
        """format a given day into a datetime object into a date format"""
        now = datetime.now()
        day = day or now.day

        # ensure the day has not been passed
        month = now.month
        if day < now.day:
            month = month + 1 if month != 12 else 1

        # check that day provided does not exceed number of days in month
        day_limit = self.calculate_days(month=(month), period="month")[1]
        if day > day_limit:
            day = day_limit

        date_period = date(year=now.year, month=(month), day=day)

        # if True, keep same day if weekday else find closest weekday occuring before day
        if weekday:
            sel_data_num = date_period.weekday()

            if sel_data_num > 4 and (day - (sel_data_num - 4)) > 0:
                day = day - (sel_data_num - 4) if income else day + (7 - sel_data_num)
            elif sel_data_num > 4:
                day = day - (7 - sel_data_num) if income else day + (7 - sel_data_num)

            if day < 0:
                month = now.month
                lim = self.calculate_days(month=(month), period="month")[1]
                day = lim - abs(day)

            date_period = date(year=now.year, month=(month), day=day)

        return date_period

    def date_to_ts(self, date_obj):
        """convert a datetime.date object into a timestamp"""

        dt_obj = datetime.strptime(str(date_obj) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        return dt_obj.timestamp()

    def day_suffix(self, myday):
        """return the suffix of the day (int)"""

        dayix = ["th", "st", "nd", "rd"]

        if myday % 10 in [1, 2, 3] and myday not in [11, 12, 13]:
            return dayix[myday % 10]
        else:
            return dayix[0]
