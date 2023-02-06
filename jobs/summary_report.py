import discord
import asyncio

from datetime import datetime, time, timedelta
from discord.ext import tasks

from util.handle_times import HandleTimes


class SummaryReport:
    def __init__(self, channel_id, intents=None, client=None, sessions=None):

        self._ht = HandleTimes()

        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)
        self._sessions = sessions or []
        self._channel_id = channel_id

        # Create the time on which the task should always run
        self._task_time = time(hour=23, minute=55, second=00)

    def breakdown_generate(self, period):

        period_resp = self._ht.calculate_days(period=period)
        days = period_resp[1] if period == "month" else period_resp

        start = self._ht.convert_timestamp(
            self._ht.current_timestamp() - (86400 * days),
            "clean",
        )

        end = self._ht.convert_timestamp(self._ht.current_timestamp(), "clean")

        session_breakdown = []
        for session in self._sessions:
            func = session.get("classVar")
            period_end = func.period_dates(period)

            session_breakdown.append(
                "{}: {} (hours)".format(session.get("sessionType"), period_end)
            )

        message = [f"```Summary ({period.capitalize()})"]
        message.append(f"    Period: [{start} - {end}]\n")
        message.append("    Total hours spent per sessions:")

        for breakdown in session_breakdown:
            message.append(f"        - {breakdown}")

        message.append("")
        message.append("(Summary brought to you by RELAB)```")

        return message

    async def background_reporter(self):
        """checks if a period has come to an end to provide a summary on each session"""

        channel = self._client.get_channel(self._channel_id)

        if self._ht.check_end_week():
            await channel.send("\n".join(self.breakdown_generate("week")))

        if self._ht.check_end_month():
            await channel.send("\n".join(self.breakdown_generate("month")))

        if self._ht.check_end_year():
            await channel.send("\n".join(self.breakdown_generate("year")))

    @tasks.loop(seconds=600)  # Create the task
    async def statistic_report(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Statistic Reporter is at work." % now.time())

        if now.time() > self._task_time:
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))

            # Seconds until tomorrow (midnight)
            seconds_until_midnight = (midnight - now).total_seconds()
            await asyncio.sleep(seconds_until_midnight)  # sleep till 00:00 & start loop

        # Loop begins
        while True:
            now = datetime.now()

            # functionality to wait till activation time - 23:55:00 PM today
            activate_time = datetime.combine(now.date(), self._task_time)
            seconds_until_activate = (activate_time - now).total_seconds()
            await asyncio.sleep(seconds_until_activate)  # Sleep until activation time

            await self.background_reporter()  # Call the helper function that sends the message

            # functionality to wait till midnight
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds_until_midnight = (midnight - now).total_seconds()
            await asyncio.sleep(seconds_until_midnight)
