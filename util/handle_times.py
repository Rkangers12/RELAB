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

    def format_a_day(self, day=None, weekday=False):
        """format a given day into a datetime object into a date format"""
        now = datetime.now()
        day = day or now.day

        # ensure the day has not been passed
        month_incre = 0
        if day < now.day:
            month_incre += 1

        # check that day provided does not exceed number of days in month
        day_limit = self.calculate_days(
            month=(now.month + month_incre), period="month"
        )[1]
        if day > day_limit:
            day = day_limit

        date_period = date(year=now.year, month=(now.month + month_incre), day=day)

        # if True, keep same day if weekday else find closest weekday occuring before day
        if weekday:
            sel_data_num = date_period.weekday()

            if sel_data_num > 4 and (day - (sel_data_num - 4)) > 0:
                day = day - (sel_data_num - 4)
            elif sel_data_num > 4:
                day = day + (6 - sel_data_num)
            date_period = date(year=now.year, month=(now.month + month_incre), day=day)

        return date_period
