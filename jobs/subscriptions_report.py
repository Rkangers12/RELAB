import discord
import asyncio
from datetime import time, datetime, timedelta
from discord.ext import tasks

from store.handler import Handler
from util.handle_times import HandleTimes
from util.monitor_subscriptions import SubscriptionsMonitor


class SubscriptionsReport:

    _KEY = "subscriptionsData"

    def __init__(self, channel_id, intents=None, client=None):

        self._datastore = Handler()
        self._ht = HandleTimes()
        self._sm = SubscriptionsMonitor(
            "subscription", self._KEY, datastore=self._datastore
        )

        self._channel_id = channel_id
        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=7, minute=15, second=00)

    async def background_reporter(self):
        """checks if a new payday is coming up and to send out alerts for reminders"""

        channel = self._client.get_channel(self._channel_id)

        subscriptions = self._sm.get_data
        for sub in subscriptions:

            if not self._sm.subscription_active(sub):
                continue

            print(self._sm.subscription_active(sub), sub)
            sd = self._ht.format_a_day(
                self._datastore.get_nested_value([self._KEY, sub, "debit_day"])
            )
            se = self._datastore.get_nested_value([self._KEY, sub, "expense"])

            sub_day_ts = self._ht.date_to_ts(sd)
            now = self._ht.current_timestamp()

            if sub_day_ts - 86400 * 3 < now < sub_day_ts - 86400 * 2.7:
                await channel.send(
                    "REMINDER: Your **£{}** **{}** subscription is due in 3 days, **{}**.".format(
                        se, sub.title(), sd
                    )
                )

            if sub_day_ts - 86400 * 1 < now < sub_day_ts - 86400 * 0.7:
                await channel.send(
                    "REMINDER: Your **£{}** **{}** subscription is due in 1 day, **{}**.".format(
                        se, sub.title(), sd
                    )
                )

            if sub_day_ts < now < sub_day_ts + 86400:
                await channel.send(
                    "£**{}** for **{}** subscription payment made today. - RELAB".format(
                        se, sub.title()
                    )
                )

    @tasks.loop(seconds=600)  # TESTING ADJUSTABLE
    async def subscription_reporter(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Subscription Reporter is at work." % now.time())

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
