import discord
import asyncio
import os

from datetime import time, datetime, timedelta
from discord.ext import tasks
from uuid import uuid4

from tools.handler import Handler
from util.handle_times import HandleTimes
from util.monitor_travel import TravelMonitor


class TravelReport:
    def __init__(self, datastore, intents=None, client=None):

        self._datastore = Handler()
        self._ht = HandleTimes()

        self._datastore = datastore
        self._tm = TravelMonitor(datastore=self._datastore)

        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=6, minute=00, second=00)
        self._channel = self._client.get_channel(int(os.getenv("TFL_CHANNEL")))

    async def background_reporter(self):
        """report the current outlook of the tfl status"""

        self._tm.constructor
        tfl_data = self._datastore.get_value("services")

        comm = [f"```TFL Services Status Update:"]
        comm.append(
            f"Date [{self._ht.format_a_day(datetime.now().day)}] | TFL Update ID [#{str(uuid4().hex[:10])}]\n"
        )
        for service in tfl_data:
            meta = tfl_data[service]
            comm.append(f"Service: {meta['name']} [ {meta['status']}]")

        await self._channel.send(".purge")
        await asyncio.sleep(15)

        await self._channel.send(("\n").join(comm) + "```")

    @tasks.loop(seconds=600)
    async def travel_reporter(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Travel Reporter is at work." % now.time())

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
            )  # 06:00:00 AM today
            seconds_until_activate = (activate_time - now).total_seconds()
            # Sleep until RELAB hits the activation time
            await asyncio.sleep(seconds_until_activate)

            await self.background_reporter()  # Call the helper function that sends the message

            # functionality to wait till midnight
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds_until_midnight = (midnight - now).total_seconds()
            await asyncio.sleep(seconds_until_midnight)
