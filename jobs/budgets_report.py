import discord
import asyncio
import os

from datetime import time, datetime, timedelta
from discord.ext import tasks

from tools.handler import Handler
from util.handle_times import HandleTimes
from util.budget_handler import BudgetHandler


class BudgetsReport:

    _KEY = "budgetData"

    def __init__(self, intents=None, client=None):

        self._datastore = Handler()
        self._ht = HandleTimes()
        self._budget = BudgetHandler(datastore=self._datastore)

        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=7, minute=15, second=00)

    async def background_reporter(self):
        """checks for expiration or exceeding of budgets"""

        users = self._datastore.get_value("users")
        for budget_user in users:

            reporter_env = self._datastore.get_nested_value(
                ["users", budget_user, "REPORTER"]
            )
            try:
                channel = self._client.get_channel(reporter_env)
            except TypeError:
                continue

            # Get all budgets and iterate through
            budgets = self._budget.get_all_budgets(budget_user)
            for budget in budgets:
                # Call check_expired method. Compares the dates, if expired then it is to be archived.
                if self._budget.check_expired(budget, budget_user) == 201:
                    await channel.send(
                        f"```{budget.title()} budget has expired, archived accordingly.```"
                    )
                    continue

                remaining = self._budget.get_remaining(budget, budget_user)

                if remaining <= 0:
                    await channel.send(
                        f"```You've met your {budget.title()} budget, no further spending for period ending {budgets.get(budget, {}).get('expiration')}. Automatically starting archive process.```"
                    )
                    self._budget.archive_budget(budget, budget_user)
                elif remaining < self._budget.get_threshold(budget_user):
                    # if the budget is nearing the threshold, then send out an alert.
                    await channel.send(
                        f"```You've spent £{budgets.get(budget, {}).get('spending')} on {budget.title()} which has fallen below your budget threshold for limit £{budgets.get(budget, {}).get('limit')}.```"
                    )

            # Monthly check to be performed on the last day of the month:
            if self._ht.check_end_month():
                # Post budget report -> Send out a message of all archived budgets for the month.
                archived = self._budget.get_all_archived(budget_user)

                message = ["```Monthly Budget Breakdown:"]
                message.append(
                    f"    Period Ending: [{self._ht.convert_timestamp(self._ht.current_timestamp(), 'clean')}]"
                )

                budget_messages = []
                success = 0
                for archive in archived:

                    name = archived.get(archive, {}).get("og_name")
                    remaining = self._budget.get_remaining(archive, budget_user)
                    statistic = "missed" if remaining < 0 else "within"
                    expiration = archived.get(archive, {}).get("expiration")

                    if statistic == "within":
                        success += 1

                    budget_messages.append(
                        f"        - [{expiration}] {name.title()} budget: {statistic} budget by £{abs(remaining)}."
                    )

                message.append(
                    f"    [{success}/{len(archived)}] budgets successfully met."
                )
                if len(archived) > 0:

                    message = message + budget_messages
                    message.append("\n(Summary brought to you by RELAB)```")
                    await channel.send("\n".join(message))
                # Reset the archived budgets dictionary for the following month.
                self._budget.reset_archive(budget_user)

    @tasks.loop(seconds=600)  # TESTING ADJUSTABLE
    async def budget_reporter(self):

        now = datetime.now()
        print("[%s] INTERNAL MESSAGE: Budget Reporter is at work." % now.time())

        if now.time() > self._task_time:
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            #  Seconds until tomorrow (midnight)
            seconds_until_midnight = (midnight - now).total_seconds()
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
            await asyncio.sleep(seconds_until_midnight)  # TESTING ADJUSTABLE
