import discord
import asyncio
import os

from datetime import time, datetime, timedelta
from discord.ext import tasks
from uuid import uuid4

from tools.handler import Handler
from util.handle_times import HandleTimes
from tools.income_commands import IncomeCommands


class PayslipReport:
    def __init__(self, datastore, intents=None, client=None):

        self._ht = HandleTimes()
        self._datastore = datastore

        self._ic = IncomeCommands(datastore=self._datastore)

        self._intents = intents or discord.Intents.all()
        self._client = client or discord.Client(intents=self._intents)

        self._task_time = time(hour=8, minute=00, second=00)

    def get_paydate_timestamp(self, paydate):
        """extract the coming paydate and convert to timestamp"""

        return self._ht.date_to_ts(paydate)

    async def payslip(self, channel, user):
        """create a payslip"""

        slip = self._ic.get_payslip(user)

        stub = [f"```Payslip by RELAB:"]
        stub.append(
            f"Date [{self._ht.format_a_day(datetime.now().day)}] | Payslip ID [#{str(uuid4().hex[:10])}]\n"
        )

        oset = " " * 8
        stub.append(f"{oset}- Gross: £{round(slip.get('gross', 0.01) / 12, 2)}")
        stub.append(f"{oset}- Tax paid: -£{slip.get('tax', 0)}")
        stub.append(f"{oset}- Employee NIC: -£{slip.get('nic', 0)}")

        if self._ic.sl_check("activeSL", user):
            stub.append(f"{oset}- Student loan paid: -£{slip.get('slt', 0)}")

        stub.append(f"\n{oset}- Income recievable: £{slip.get('takehome', 0)}```")

        await channel.send("\n".join(stub))

    async def background_reporter(self):
        """checks if a new payday is coming up and to send out alerts for reminders"""

        users = self._datastore.get_value("users")
        for payroll_user in users:

            pay_date = int(self._ic.get("payDay", payroll_user))
            if pay_date == 0:
                print("exiting", payroll_user)
                continue

            reporter_env = self._datastore.get_nested_value(
                ["users", payroll_user, "REPORTER"]
            )
            try:
                channel = self._client.get_channel(int(os.getenv(reporter_env)))
            except TypeError:
                continue

            payday = self._ht.format_a_day(pay_date, weekday=True)
            paydate_ts = self.get_paydate_timestamp(payday)

            now = self._ht.current_timestamp()

            if paydate_ts - 86400 * 7 < now < paydate_ts - 86400 * 6.7:
                await channel.send(
                    f"```REMINDER: You are due to be paid in 7 days, {payday}.```"
                )

            if paydate_ts - 86400 * 3 < now < paydate_ts - 86400 * 2.7:
                await channel.send(
                    f"```REMINDER: You are due to be paid in 3 days, {payday}.```"
                )

            if paydate_ts - 86400 * 1 < now < paydate_ts - 86400 * 0.7:
                await channel.send(
                    f"```REMINDER: You are due to be paid in 1 day, {payday}.```"
                )

            if paydate_ts < now < paydate_ts + 86400:
                await channel.send(
                    "```RELAB has determined today as your pay date. See below for payslip:```"
                )
                await self.payslip(channel, payroll_user)

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
            )  # 08:00:00 AM today
            seconds_until_activate = (activate_time - now).total_seconds()
            # Sleep until RELAB hits the activation time
            await asyncio.sleep(seconds_until_activate)

            await self.background_reporter()  # Call the helper function that sends the message

            # functionality to wait till midnight
            midnight = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds_until_midnight = (midnight - now).total_seconds()
            await asyncio.sleep(seconds_until_midnight)
