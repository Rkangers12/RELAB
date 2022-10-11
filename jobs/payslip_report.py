import py_compile
import discord
import asyncio

from datetime import time, datetime, timedelta
from discord.ext import tasks

from store.handler import Handler
from util.handle_times import HandleTimes
from tools.income_commands import IncomeCommands


class PayslipReport:
    def __init__(self, channel_id, intents=None, client=None):

        self._datastore = Handler()
        self._ht = HandleTimes()
        self._ic = IncomeCommands(datastore=self._datastore)

        self._chanel_id = channel_id
        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=8, minute=00, second=00)

    def get_paydate_timestamp(self, paydate):
        """extract the coming paydate and convert to timestamp"""

        return self._ht.date_to_ts(paydate)

    async def background_reporter(self):
        """checks if a new payday is coming up and to send out alerts for reminders"""

        channel = self._client.get_channel(self._chanel_id)

        payday = self._ht.format_a_day(int(self._ic.get("payDay")), weekday=True)
        paydate_ts = self.get_paydate_timestamp(payday)

        print(
            self._ht.convert_timestamp(paydate_ts),
            self._ht.convert_timestamp(paydate_ts - 86400 * 7),
        )

        now = self._ht.current_timestamp()

        if paydate_ts - 86400 * 8 < now < paydate_ts - 86400 * 6:
            print("REMINDER: You are due to be paid in 7 days, **{}**.".format(payday))
            await channel.send(
                "REMINDER: You are due to be paid in 7 days, **{}**.".format(payday)
            )

        if paydate_ts - 86400 * 4 < now < paydate_ts - 86400 * 2:
            print("REMINDER: You are due to be paid in 3 days, **{}**.".format(payday))
            await channel.send(
                "REMINDER: You are due to be paid in 3 days, **{}**.".format(payday)
            )

        if paydate_ts - 86400 * 2 < now < paydate_ts:
            print("REMINDER: You are due to be paid in 1 day, **{}**.".format(payday))
            await channel.send(
                "REMINDER: You are due to be paid in 1 day, **{}**.".format(payday)
            )

        if True:
            await channel.send(
                "RELAB has determined today as your pay date. See below for payslip:."
            )
            await channel.send(".payslip")

    @tasks.loop(seconds=600)
    async def payslip_reporter(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Payslip Reporter is at work." % now.time())

        if now.time() > self._task_time:
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            #  Seconds until tomorrow (midnight)
            seconds_until_midnight = (midnight - now).total_seconds()
            # Sleep until midnight and then loop shall begin
            await asyncio.sleep(seconds_until_midnight)

        # Loop begins
        while True:
            now = datetime.now()

            # functionality to wait till activation time
            activate_time = datetime.combine(
                now.date(), self._task_time
            )  # 00:01:00 AM today
            seconds_until_activate = (activate_time - now).total_seconds()
            # Sleep until RELAB hits the activation time
            await asyncio.sleep(seconds_until_activate)

            await self.background_reporter()  # Call the helper function that sends the message

            # functionality to wait till midnight
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds_until_midnight = (midnight - now).total_seconds()
            await asyncio.sleep(seconds_until_midnight)
