import discord
import asyncio
from datetime import time, datetime, timedelta
from discord.ext import tasks

from store.handler import Handler
from util.handle_times import HandleTimes
from util.monitor import Monitor


class BillsReport:
    def __init__(self, channel_id, intents=None, client=None):

        self._datastore = Handler()
        self._ht = HandleTimes()
        self._bm = Monitor("bill", "billsData", datastore=self._datastore)

        self._channel_id = channel_id
        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=7, minute=00, second=00)

    async def background_reporter(self):
        """checks if a new payday is coming up and to send out alerts for reminders"""

        channel = self._client.get_channel(self._channel_id)

        bills = self._bm.get_data
        for bill in bills:

            bd = self._ht.format_a_day(
                self._datastore.get_nested_value(["billsData", bill, "debit_day"])
            )
            be = self._datastore.get_nested_value(["billsData", bill, "expense"])

            bill_day_ts = self._ht.date_to_ts(bd)
            now = self._ht.current_timestamp()

            if bill_day_ts - 86400 * 3 < now < bill_day_ts - 86400 * 2.7:
                await channel.send(
                    "REMINDER: Your **£{}** **{}** bill is due in 3 days, **{}**.".format(
                        be, bill.title(), bd
                    )
                )

            if bill_day_ts - 86400 * 1 < now < bill_day_ts - 86400 * 0.7:
                await channel.send(
                    "REMINDER: Your **£{}** **{}** bill is due in 1 day, **{}**.".format(
                        be, bill.title(), bd
                    )
                )

            if bill_day_ts < now < bill_day_ts + 86400:
                await channel.send(
                    "£**{}** for **{}** bill payment made today. - RELAB".format(
                        be, bill.title()
                    )
                )

    @tasks.loop(seconds=600)  # TESTING ADJUSTABLE
    async def bill_reporter(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Bill Reporter is at work." % now.time())

        if now.time() > self._task_time:
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            #  Seconds until tomorrow (midnight)
            seconds_until_midnight = (midnight - now).total_seconds()
            # Sleep until midnight and then loop shall begin
            await asyncio.sleep(seconds_until_midnight)  # TESTING ADJUSTABLE

        # Loop begins
        while True:
            now = datetime.now()

            # functionality to wait till activation time
            activate_time = datetime.combine(
                now.date(), self._task_time
            )  # 07:00:00 AM today
            seconds_until_activate = (activate_time - now).total_seconds()
            # Sleep until RELAB hits the activation time
            await asyncio.sleep(seconds_until_activate)  # TESTING ADJUSTABLE

            await self.background_reporter()  # Call the helper function that sends the message

            # functionality to wait till midnight
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds_until_midnight = (midnight - now).total_seconds()
            await asyncio.sleep(seconds_until_midnight)
