import discord
import asyncio
import os

from datetime import time, datetime, timedelta
from discord.ext import tasks

from tools.handler import Handler
from util.handle_times import HandleTimes
from util.monitor_notes import NotesMonitor


class NotesReport:
    def __init__(self, intents=None, client=None):

        self._datastore = Handler()
        self._ht = HandleTimes()
        self._nm = NotesMonitor("note", datastore=self._datastore)

        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=9, minute=30, second=00)

    async def background_reporter(self):
        """Check if an alert for a note is due"""

        users = self._datastore.get_value("users")
        for note_user in users:

            reporter_env = self._datastore.get_nested_value(
                ["users", note_user, "REPORTER"]
            )
            try:
                channel = self._client.get_channel(reporter_env)
            except TypeError:
                continue

            notes = self._nm.get_all(note_user)
            for note in notes:

                meta = self._datastore.get_nested_value(
                    ["users", note_user, "note", note]
                )
                day = self._ht.format_a_day(meta["day"])
                desc = meta["desc"]

                note_ts = self._ht.date_to_ts(day)
                now = self._ht.current_timestamp()

                if note_ts < now < note_ts + 86400:
                    await channel.send(
                        f"```ALERT: Reminding you about your {'repeat' if meta['repeat'] else 'quick'} note '{note}'. [1/2]```"
                    )
                    await channel.send(f"```{desc.capitalize()}. [2/2]```")

                    if not meta["repeat"]:
                        self._nm.delete(name=note, user=note_user)

    @tasks.loop(seconds=600)  # TESTING ADJUSTABLE
    async def note_reporter(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Note Reporter is at work." % now.time())

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
