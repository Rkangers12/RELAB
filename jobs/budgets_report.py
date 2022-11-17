import discord
import asyncio
from datetime import time, datetime, timedelta
from discord.ext import tasks

from store.handler import Handler
from util.handle_times import HandleTimes
from util.budget_handler import BudgetHandler


class BudgetsReport:

    _KEY = "budgetData"

    def __init__(self, channel_id, intents=None, client=None):

        self._datastore = Handler()
        self._ht = HandleTimes()
        self._budget = BudgetHandler(datastore=self._datastore)

        self._channel_id = channel_id
        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=7, minute=15, second=00)

    async def budget_reporter(self):
        """checks for expiration or exceeding of budgets"""

        channel = self._client.get_channel(self._channel_id)

        # Get all budgets and iterate through
        budgets = self._budget.get_all_budgets
        for budget in budgets:
            # Call check_expired method. Compares the dates, if expired then it is to be archived.
            if self._budget.check_expired(budget):
                await channel.send("{budget} budget has expired, archived accordingly.")

            remaining = self._budget.get_remaining(budget)
            if remaining < 0:
                # If the budget has exceeded the threshold, then send out an alert to the user.
                channel.send(
                    f"You've exceeded your {budget} budget of limit: £{budgets.get(budget, {}).get('limit')} by £{abs(remaining)}."
                )
            elif remaining < self._budget.get_threshold:
                # if the budget is nearing the threshold, then send out an alert.
                channel.send(
                    f"You are nearing your {budget} budget of limit: £{budgets.get(budget, {}).get('limit')}."
                )

        # Monthly check to be performed on the last day of the month:
        if self._ht.check_end_month():
            channel.send("Providing budget summary for end of month:")

            # Post budget report -> Send out a message of all archived budgets for the month.
            archived = self._budget.get_all_archived

            for archive in archived:

                remaining = self._budget.get_remaining(archive)
                statistic = "over" if remaining > 0 else "under"
                creation = archived.get(archive, {}).get("creation")
                expiration = archived.get(archive, {}).get("expiration")

                channel.send(
                    f"{archive} budget [{creation}] [{expiration}]: {statistic}budget by {remaining}."
                )

            # Reset the archived budgets dictionary for the following month.
            self._budget.reset_archive

    @tasks.loop(seconds=600)  # TESTING ADJUSTABLE
    async def budget_reporter(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Budget Reporter is at work." % now.time())

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
