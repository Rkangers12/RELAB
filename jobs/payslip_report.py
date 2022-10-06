import discord
import asyncio

from datetime import datetime, time, timedelta
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

        self._task_time = time(hour=00, minute=1, second=00)

    def get_paydate_timestamp(self):
        """extract the coming paydate and convert to timestamp"""

        payday = self._ht.format_a_day(int(self._ic.get("payDay")), weekday=True)
        return payday

    async def background_reporter(self):
        """checks if a new payday is coming up and to send out alerts for reminders"""

        channel = self._client.get_channel(self._chanel_id)

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
