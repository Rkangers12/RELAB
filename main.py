import os
import discord

from datetime import datetime
from dotenv import load_dotenv
from uuid import uuid4

from store.handler import Handler

from tools.income_commands import IncomeCommands
from tools.session_commands import SessionCommands

from jobs.bills_report import BillsReport
from jobs.budgets_report import BudgetsReport
from jobs.payslip_report import PayslipReport
from jobs.subscriptions_report import SubscriptionsReport
from jobs.summary_report import SummaryReport

from util.budget_handler import BudgetHandler
from util.handle_times import HandleTimes
from util.monitor import Monitor
from util.monitor_subscriptions import SubscriptionsMonitor
from util.session_tracker import SessionTrack
from util.temp_monitor import Tempy

load_dotenv()
intents = discord.Intents.all()
client = discord.Client(intents=intents)

datastore = Handler()
hand_time = HandleTimes()

studytrack = SessionTrack("study_records", "studying", datastore=datastore)
gymtrack = SessionTrack("gym_records", "gymming", datastore=datastore)

sesscomms = SessionCommands(
    datastore=datastore, studytrack=studytrack, gymtrack=gymtrack
)
inc_coms = IncomeCommands(datastore=datastore)

budget_handler = BudgetHandler(datastore=datastore)
temp_monitor = Tempy("bill", datastore=datastore)
bills_monitor = Monitor("bill", "billsData", datastore=datastore)
subs_monitor = SubscriptionsMonitor(
    "subscription", "subscriptionsData", datastore=datastore
)


@client.event
async def on_ready():
    print("\nWe have logged in as {0.user}".format(client))

    summaryTask = SummaryReport(
        channel_id=int(os.getenv("SESSIONS_CHANNEL")),
        intents=intents,
        client=client,
        sessions=[
            {"classVar": studytrack, "sessionType": "Study"},
            {"classVar": gymtrack, "sessionType": "Gym"},
        ],
    )

    if not summaryTask.statistic_report.is_running():
        summaryTask.statistic_report.start()  # if the task is not already running, start it.
        print(
            "Booted Background Process #1: Statistic Reporter - {0.user}".format(client)
        )

    payslipTask = PayslipReport(
        channel_id=int(os.getenv("PAYSLIP_CHANNEL")), intents=intents, client=client
    )

    if not payslipTask.payslip_reporter.is_running():
        payslipTask.payslip_reporter.start()  # if the task is not already running, start it.
        print(
            "Booted Background Process #2: Payslip Reporter - {0.user}".format(client)
        )

    billTask = BillsReport(
        channel_id=int(os.getenv("BILLS_CHANNEL")), intents=intents, client=client
    )

    if not billTask.bill_reporter.is_running():
        billTask.bill_reporter.start()  # if the task is not already running, start it.
        print("Booted Background Process #3: Bill Reporter - {0.user}".format(client))

    subscriptionTask = SubscriptionsReport(
        channel_id=int(os.getenv("SUBS_CHANNEL")), intents=intents, client=client
    )

    if not subscriptionTask.subscription_reporter.is_running():
        subscriptionTask.subscription_reporter.start()  # if the task is not already running, start it.
        print(
            "Booted Background Process #4: Subscription Reporter - {0.user}".format(
                client
            )
        )

    budgetTask = BudgetsReport(
        channel_id=int(os.getenv("BUDGETS_CHANNEL")), intents=intents, client=client
    )

    if not budgetTask.budget_reporter.is_running():
        budgetTask.budget_reporter.start()  # if the task is not already runnning, start.
        print(
            "Booted Background Process #5: Budget Reporter - {0.user}\n".format(client)
        )


async def snapshot(message):
    """take a snapshot of the database"""

    await message.delete()
    datastore.snapshot()
    await message.channel.send(
        "**[{}] - Database backed up to secure location.**".format(
            hand_time.format_a_day()
        )
    )


async def power(message):
    """command center for those relating to the bot settings"""
    await message.delete()

    setting = "settings"
    if datastore.get_value(setting, {}) == {}:
        datastore.overwrite(db_key=setting, db_value={})

    power = datastore.get_nested_value([setting, "power"], default=False)

    if power:
        datastore.overwrite_nested([setting], "power", False)
        await message.channel.send("**RELAB has been switched off.**")
    else:
        datastore.overwrite_nested([setting], "power", True)
        await message.channel.send("**RELAB has been switched on.**")


@client.event
async def on_message(message):

    msg = message.content
    bypass = False

    if message.author == client.user:
        if msg.startswith(".payslip"):
            bypass = True
        else:
            return

    if msg.startswith(".purge") and message.author.id == int(os.getenv("KING_ID")):
        try:
            print("Purging")
            await message.channel.purge(limit=100)
        except discord.errors.NotFound:
            print("No messages to purge found")

    if message.channel.id == int(os.getenv("BOT_SETTINGS")):
        if msg.startswith(".power"):
            await power(message)

    bot_powered = datastore.get_nested_value(["settings", "power"])
    if bot_powered:
        if message.channel.id == int(os.getenv("SNAPSHOTS_CHANNEL")):
            if msg.startswith(".snapshot"):
                await snapshot(message)

        if message.channel.id == int(os.getenv("HELP_CHANNEL")):

            if msg.startswith(".helppayroll"):
                await message.delete()

                prompt = ["```Payroll Command Prompt Help:"]

                prompt.append("    .setsalary <gross annual e.g. 45000>")
                prompt.append("    .getsalary")
                prompt.append("    .setnotionals <notional amount e.g. 100>")
                prompt.append("    .getnotionals")
                prompt.append("    .setpaydate <date of pay e.g. 15>")
                prompt.append("    .getpaydate")
                prompt.append("    .togglestudentloan")
                prompt.append("    .checkstudentloan")
                prompt.append("    .takehome")
                prompt.append("    .payrollsettings")
                prompt.append("    .payslip")
                prompt.append("    .helppayroll```")

                await message.channel.send("\n".join(prompt))

            if msg.startswith(".helpbills"):
                await message.delete()

                prompt = ["```Bill Command Prompt Help:"]
                prompt.append(
                    "    .createbill <name e.g. rent> ‹exp e.g. 14> <limit e.g. 50>"
                )
                prompt.append("    .billlimit <name e.g. rent> <limit e.g. 50>")
                prompt.append("    .billexpiration <name e.g. rent> <exp e.g. 1>")
                prompt.append("    .retrievebill <name e.g. rent>")
                prompt.append("    .bills")
                prompt.append("    .deletebill <name e.g. rent>")
                prompt.append("    .deleteallbills")
                prompt.append("    .helpbills```")

                await message.channel.send("\n".join(prompt))

            if msg.startswith(".helpbudget"):
                await message.delete()

                prompt = ["```Budget Command Prompt Help:"]
                prompt.append(
                    "    .createbudget <name e.g. coffee> <expiration e.g. 13> <limit e.g 50>"
                )
                prompt.append("    .budgetlimit <name e.g. coffee> <limit e.g 50>")
                prompt.append(
                    "    .budgetexpiration <name e.g. coffee> <expiration e.g. 13>"
                )
                prompt.append("    .getbudget <name e.g. coffee>")
                prompt.append("    .budgets")
                prompt.append("    .setthreshold <threshold e.g. 7.50>")
                prompt.append(
                    "    .spentbudget <name e.g. coffee> <spending e.g. 12.40>"
                )
                prompt.append("    .deletebudget <name e.g. coffee>")
                prompt.append("    .archivebudget <name e.g. coffee>")
                prompt.append("    .spendingbudget")
                prompt.append("    .resetbudgetarchive")
                prompt.append("    .helpbudget```")

                await message.channel.send("\n".join(prompt))

        if message.channel.id == int(os.getenv("BOT_HELPER")):
            if msg.startswith(".channels"):
                await message.channel.send("Success")

                for channel in client.get_all_channels():
                    print(channel.id, channel.name)

        if message.channel.id == int(os.getenv("RELAB_CHANNEL")) or bypass:
            if msg.startswith(".study"):
                await sesscomms.study(message)

            if msg.startswith(".getstudy"):
                await sesscomms.get_study(message)

            if msg.startswith(".gym"):
                await sesscomms.gym(message)

            if msg.startswith(".getgym"):
                await sesscomms.get_gym(message)

            if msg.startswith(".setsalary"):
                await message.delete()
                resp = inc_coms.set_payroll(msg, "grossSalary")

                if resp == 200:
                    await message.channel.send(
                        "**Gross Salary** details updated. - RELAB"
                    )
                elif resp == 404:
                    await message.channel.send(
                        "Please provide appropriate payroll data."
                    )

            if msg.startswith(".getsalary"):
                await message.delete()
                comms = "Payroll details by RELAB: \n    - Gross Salary: **£{}**"
                await message.channel.send(comms.format(inc_coms.get("grossSalary")))

            if msg.startswith(".setnotionals"):
                await message.delete()
                resp = inc_coms.set_payroll(msg, "notionals")

                if resp == 200:
                    await message.channel.send("**Notionals** details updated. - RELAB")
                elif resp == 404:
                    await message.channel.send(
                        "Please provide appropriate payroll data."
                    )

            if msg.startswith(".getnotionals"):
                await message.delete()
                comms = "Payroll details by RELAB: \n    - Notionals: **£{}**"
                await message.channel.send(comms.format(inc_coms.get("notionals")))

            if msg.startswith(".setpaydate"):
                await message.delete()
                resp = inc_coms.set_payroll(msg, "payDay")

                if resp == 200:
                    await message.channel.send("**Pay Date** details updated. - RELAB")
                elif resp == 404:
                    await message.channel.send(
                        "Please provide appropriate payroll data."
                    )

            if msg.startswith(".getpaydate"):
                await message.delete()
                comms = "Payroll details by RELAB: \n    - Next Pay Day: **{}**"
                await message.channel.send(
                    comms.format(
                        hand_time.format_a_day(
                            int(inc_coms.get("payDay")), weekday=True
                        )
                    )
                )

            if msg.startswith(".togglestudentloan"):
                await message.delete()
                comms = "Student Loan now **{}**. - RELAB"
                await message.channel.send(comms.format(inc_coms.sl_toggle("activeSL")))

            if msg.startswith(".checkstudentloan"):
                await message.delete()
                comms = "Payroll details by RELAB: \n    - Student Loan: **{}**"
                await message.channel.send(
                    comms.format(
                        "active" if inc_coms.sl_check("activeSL") else "inactive"
                    )
                )

            if msg.startswith(".takehome"):
                await message.delete()
                await message.channel.send(
                    "Your income after tax is **£{}** (**{}**). - RELAB".format(
                        inc_coms.get_takehome(),
                        hand_time.format_a_day(
                            int(inc_coms.get("payDay")), weekday=True
                        ),
                    )
                )

            if msg.startswith(".payrollsettings"):
                await message.delete()

                comms = [f"```Payroll details by RELAB:\n"]
                comms.append(f"    - Gross Salary: £{inc_coms.get('grossSalary')}")
                comms.append(f"    - Notionals: £{inc_coms.get('notionals')}")
                comms.append(
                    f"    - Next Pay Day: {hand_time.format_a_day(int(inc_coms.get('payDay')), weekday=True)}"
                )
                comms.append(
                    f"    - Student Loan: {'active' if inc_coms.sl_check('activeSL') else 'inactive'}"
                )

                await message.channel.send("\n".join(comms))

            if msg.startswith(".payslip"):
                await message.delete()

                slip = inc_coms.get_payslip()

                stub = [f"```Payslip by RELAB:"]
                stub.append(
                    f"Date [{hand_time.format_a_day(datetime.now().day)}] | Payslip ID [#{str(uuid4().hex[:10])}]\n"
                )

                oset = " " * 8
                stub.append(f"{oset}- Gross: £{round(slip.get('gross', 0.01) / 12, 2)}")
                stub.append(f"{oset}- Tax paid: -£{slip.get('tax', 0)}")
                stub.append(f"{oset}- Employee NIC: -£{slip.get('nic', 0)}")

                if inc_coms.sl_check("activeSL"):
                    stub.append(f"{oset}- Student loan paid: -£{slip.get('slt', 0)}")

                stub.append(
                    f"\n{oset}- Income recievable: £{slip.get('takehome', 0)}```"
                )

                await message.channel.send("\n".join(stub))

            def message_sorter(information):
                """break down information into components"""

                try:
                    return information.split(" ")[1:]
                except ValueError:
                    return 400

            def due_date(day, weekday=True):
                """convert a day integer in to a date"""

                return hand_time.format_a_day(int(day), weekday=weekday)

            if msg.startswith(".createbill"):
                await message.delete()

                components = message_sorter(msg)
                if components != 400 and len(components) == 3:
                    name, expiration, limit = components
                    res = temp_monitor.create(name, expiration, limit)
                else:
                    res = 400

                if res == 200:
                    await message.channel.send(
                        f"```Created {name.title()} bill of £{limit} due on {due_date(expiration)}```"
                    )
                elif res == 201:
                    await message.channel.send(
                        f"```Bill {name.title()} already exists, please delete or modify it.```"
                    )
                else:
                    await message.channel.send(
                        f"```Error creating bill. Please use command '.createbill <name e.g. electric> ‹expiration e.g. 14> <limit e.g. 50>'```"
                    )

            if msg.startswith(".billlimit"):
                await message.delete()

                components = message_sorter(msg)
                if components != 400 and len(components) == 2:
                    name, limit = components
                    res = temp_monitor.modify_limit(name, limit)
                else:
                    res = 400

                if res == 200:
                    await message.channel.send(
                        f"```Modified {name.title()} bill to £{limit}```"
                    )
                elif res == 204:
                    await message.channel.send(
                        f"```Bill {name.title()} does not exists, please create using '.createbill' first.```"
                    )
                else:
                    await message.channel.send(
                        f"```Error modifying limit. Please use command '.billlimit <name e.g. electric> <limit e.g. 50>'```"
                    )

            if msg.startswith(".billexpiration"):
                await message.delete()

                components = message_sorter(msg)
                if components != 400 and len(components) == 2:
                    name, limit = components
                    res = temp_monitor.modify_expiration(name, limit)
                else:
                    res = 400

                if res == 200:
                    await message.channel.send(
                        f"```Modified {name.title()} expiration, now indefinitely due on {due_date(expiration)}```"
                    )
                elif res == 204:
                    await message.channel.send(
                        f"```Bill {name.title()} does not exists, please create using '.createbill' first.```"
                    )
                else:
                    await message.channel.send(
                        f"```Error modifying expiration. Please use command '.billexpiration <name e.g. electric> <expiration e.g. 17>'```"
                    )

            if msg.startswith(".retrievebill"):
                await message.delete()

                components = message_sorter(msg)
                if components != 400 and len(components) == 1:
                    name = components[0]
                    bill = temp_monitor.get(name)
                else:
                    bill = None

                if bill is not None:
                    await message.channel.send(
                        f"```{name.title()} is payable on the {due_date(bill['expiration'])} for the amount £{bill['limit']}.```"
                    )
                else:
                    await message.channel.send(
                        f"```{name.title()} was not retrievable, does it exist? Please use command '.retrievebill <name e.g. rent>'.```"
                    )

            if msg.startswith(".deletebill"):
                await message.delete()

                components = message_sorter(msg)
                if components != 400 and len(components) == 1:
                    name = components[0]
                    res = temp_monitor.delete(name)

                    if res == 200:
                        await message.channel.send(
                            f"```Bill {name.title()} was deleted.```"
                        )
                        return None

                await message.channel.send(
                    f"```Error deleting bill {name.title()}. Please use command '.deletebill <name e.g. rent>'.```"
                )

            if msg.startswith(".deleteallbills"):
                await message.delete()

                outcome = temp_monitor.delete_all

                comms = ["```Bills Information:"]
                comms.append(
                    f"Date [{hand_time.format_a_day(datetime.now().day)}] | Request ID [#{str(uuid4().hex[:10])}]\n"
                )

                comms.append(
                    f"        - Successful bills deletion: {', '.join(outcome['deleted'])}"
                )
                comms.append(
                    f"        - Failed bills deletion: {', '.join(outcome['failed'])}"
                )

                await message.channel.send("\n".join(comms) + "```")

            if msg.startswith(".bills"):
                await message.delete()

                bills = temp_monitor.get_all

                comms = ["```Bills Information:"]
                comms.append(
                    f"Date [{hand_time.format_a_day(datetime.now().day)}] | Request ID [#{str(uuid4().hex[:10])}]\n"
                )

                if len(bills) == 0:
                    comms.append("        - No bills")

                for bill in bills:
                    meta = bills[bill]
                    comms.append(
                        f"        - {bill.title()} is payable on the {due_date(meta['expiration'])} for the amount £{meta['limit']}."
                    )

                await message.channel.send("\n".join(comms) + "```")

            if msg.startswith(".registersubscription"):
                await message.delete()
                resp = subs_monitor.register(msg)

                if resp == 200:
                    await message.channel.send(
                        "New subscription data has been registered. - RELAB"
                    )
                elif resp == 404:
                    await message.channel.send(
                        "Error registering subscription. - RELAB"
                    )

            if msg.startswith(".updatesubscription"):
                await message.delete()
                resp = subs_monitor.extend_update(msg)

                if resp == 200:
                    await message.channel.send("Subscription has been updated. - RELAB")
                elif resp == 404:
                    await message.channel.send("Error updating subscription. - RELAB")

            if msg.startswith(".getsubscription"):
                await message.delete()

                resp = subs_monitor.get(msg)

                if resp == 404:
                    await message.channel.send(
                        "Subscription information provided was invalid. - RELAB"
                    )
                    return

                await message.channel.send(subs_monitor.format_message(resp))

            if msg.startswith(".getmetasubscription"):
                await message.delete()

                resp = subs_monitor.extend_get_meta(msg)

                if resp == 404:
                    await message.channel.send(
                        "Subscription information provided was invalid. - RELAB"
                    )
                    return

                await message.channel.send(subs_monitor.format_message(resp))

            if msg.startswith(".subscriptions"):
                await message.delete()

                resp = subs_monitor.get_all()
                for msg_res in resp:
                    await message.channel.send(subs_monitor.format_message(msg_res))

            if msg.startswith(".deletesubscription"):
                await message.delete()
                resp = subs_monitor.delete(msg)

                if resp == 200:
                    await message.channel.send("Subscription has been deleted. - RELAB")
                elif resp == 404:
                    await message.channel.send("Error deleting subscripton. - RELAB")

            if msg.startswith(".delmetasub"):
                await message.delete()
                resp = subs_monitor.extend_delete_meta(msg)

                if resp == 200:
                    await message.channel.send(
                        "Subscription metadata has been deleted. - RELAB"
                    )
                elif resp == 404:
                    await message.channel.send(
                        "Error deleting subscripton metadata. - RELAB"
                    )

            if msg.startswith(".togglesubscription"):
                await message.delete()
                resp = subs_monitor.pause(msg)

                if resp.get("statusCode") == 404:
                    await message.channel.send(
                        "Error toggling subscription status - RELAB"
                    )

                if resp.get("statusCode") == 200:
                    if resp.get("active"):
                        await message.channel.send(
                            "**{} has been switched on.**".format(
                                resp.get("subscription")
                            )
                        )
                    else:
                        await message.channel.send(
                            "**{} has been switched off.**".format(
                                resp.get("subscription")
                            )
                        )

            if msg.startswith(".createbudget"):
                await message.delete()

                try:
                    name, expiration, limit = msg.split(" ")[1:]
                except ValueError:
                    res = 400
                else:
                    res = budget_handler.create_budget(name, expiration, limit)

                if res == 200:
                    await message.channel.send(
                        f"Created a **{name}** budget expiring **{hand_time.format_a_day(int(expiration))}** of **£{limit}**"
                    )
                elif res == 201:
                    await message.channel.send(
                        f"Budget **{name}** already exists, please **delete** or **archive** it first."
                    )
                else:
                    await message.channel.send(
                        f"Error creating budget. Please use command: '**.createbudget <name e.g. coffee> <expiration e.g. 14> <limit e.g. 50>**'"
                    )

            if msg.startswith(".budgetlimit"):
                await message.delete()

                try:
                    name, limit = msg.split(" ")[1:]
                except ValueError:
                    res = 400
                else:
                    res = budget_handler.modify_budget_limit(name, limit)

                if res == 200:
                    await message.channel.send(
                        f"Modified **{name}** budget to £**{limit}**."
                    )
                elif res == 204:
                    await message.channel.send(
                        f"Budget **{name}** does not exist. Please create using **'.createbudget'** first."
                    )
                else:
                    await message.channel.send(
                        f"Error modifying limit. Please use command: '**.budgetlimit <name e.g. coffee> <limit e.g. 50>**'"
                    )

            if msg.startswith(".budgetexpiration"):
                await message.delete()

                try:
                    name, expiration = msg.split(" ")[1:]
                except ValueError:
                    res = 400
                else:
                    res = budget_handler.modify_budget_expiration(name, expiration)

                if res == 200:
                    await message.channel.send(
                        f"Modified **{name}** budget to **{hand_time.format_a_day(int(expiration))}**."
                    )
                elif res == 204:
                    await message.channel.send(
                        f"Budget **{name}** does not exist. Please create using **'.createbudget'** first."
                    )
                else:
                    await message.channel.send(
                        f"Error modifying expiration. Please use command: '**.budgetexpiration <name e.g. coffee> <expiration e.g. 12>**'"
                    )

            if msg.startswith(".getbudget"):
                await message.delete()

                try:
                    name = msg.split(" ")[1]
                except (ValueError, IndexError):
                    budget = None
                else:
                    budget = budget_handler.get_budget(name)
                    if budget is not None:
                        await message.channel.send(
                            f"You've spent **£{budget.get('spending')}** of your **£{budget.get('limit')}** {name} budget lasting till **{budget.get('expiration')}**."
                        )

                if budget is None:
                    await message.channel.send(
                        "Error retrieving budget, please use '**.getbudget <name e.g. coffee>**'"
                    )

            if msg.startswith(".budgets"):
                await message.delete()

                budgets = budget_handler.get_all_budgets
                for budget in budgets:
                    meta = budgets[budget]
                    await message.channel.send(
                        f"You've spent £**{meta.get('spending')}** of your £**{meta.get('limit')}**, **{budget}** budget lasting till **{meta.get('expiration')}**."
                    )

            if msg.startswith(".setthreshold"):
                await message.delete()

                try:
                    val = float(msg.split(" ")[1])
                except (IndexError, ValueError):
                    await message.channel.send(
                        "Error modifying threshold, please use '**.setthreshold <value e.g. 10>**'."
                    )
                else:
                    budget_handler.set_threshold(val)

                    await message.channel.send(
                        f"Updated budget **threshold level alert** to £**{val}** - RELAB"
                    )

            if msg.startswith(".getthreshold"):
                await message.delete()

                thres = budget_handler.get_threshold
                await message.channel.send(
                    f"Current budget **threshold level alert** is £**{thres}** - RELAB"
                )

            if msg.startswith(".spentbudget"):
                await message.delete()

                try:
                    name, spending = msg.split(" ")[1:]
                    spending = float(spending)
                except (ValueError, TypeError):
                    res = 201
                else:
                    res = budget_handler.record_spending(name, spending)
                    budget = budget_handler.get_budget(name)

                if res != 201:
                    await message.channel.send(
                        f"Recorded spending of **£{spending}** toward your '**{name}**' budget. "
                        f"You've spent £**{budget.get('spending')}** of your £**{budget.get('limit')}** "
                        f"**{name}** budget lasting till **{budget.get('expiration')}**."
                    )
                    if res == 203:
                        await message.channel.send(
                            f"**Balance expired**. You've reached your **{name}** budget."
                        )
                        budget_handler.archive_budget(name)
                    elif res == 204:
                        await message.channel.send(
                            f"**Balance warning**. You've spent £**{budget.get('spending')}** of your £**{budget.get('limit')}** remaining **{name}** budget."
                        )
                else:
                    await message.channel.send(
                        "Error recording spending, please use '**.spentbudget <name e.g. coffee> <spending e.g. 12.50>**'"
                    )

            if msg.startswith(".budgetbalance"):
                await message.delete()

                try:
                    name = msg.split(" ")[1]
                except IndexError:
                    await message.channel.send(
                        "Error getting budget balance, please use '**.budgetbalance <name e.g. coffee>**'"
                    )
                else:
                    try:
                        balance = max(0, budget_handler.get_remaining(name))
                    except TypeError:
                        await message.channel.send(
                            "Error getting budget balance, please use '**.budgetbalance <name e.g. coffee>**'"
                        )
                    else:
                        await message.channel.send(
                            f"Budget **{name}** has a remaining balance of £**{balance}** - RELAB."
                        )

            if msg.startswith(".deletebudget"):
                await message.delete()

                try:
                    name = msg.split(" ")[1]
                except IndexError:
                    await message.channel.send(
                        "Error deleting budget, please use '**.deletebudget <name e.g. coffee>**'"
                    )
                else:
                    res = budget_handler.delete_budget(name)
                    if res == 200:
                        await message.channel.send(
                            f"Budget **{name}** has been **deleted**. - RELAB."
                        )
                    else:
                        await message.channel.send(
                            f"Budget **{name}** doesn't exist, please provide an existing budget."
                        )

            if msg.startswith(".archivebudget"):
                await message.delete()

                try:
                    name = msg.split(" ")[1]
                except IndexError:
                    await message.channel.send(
                        "Error archiving budget, please use '**.archivebudget <name e.g. coffee>**'"
                    )
                else:
                    res = budget_handler.archive_budget(name)
                    if res != 201:
                        await message.channel.send(
                            f"Budget **{name}** has been **archived**. - RELAB"
                        )
                    else:
                        await message.channel.send(
                            f"Budget **{name}** doesn't exist, please provide an existing budget."
                        )

            if msg.startswith(".spendingbudget"):
                await message.delete()

                await message.channel.send(
                    f"**Your spending across all active budgets is {budget_handler.budget_spending}. - RELAB**"
                )

            if msg.startswith(".checkbudgetexp"):
                await message.delete()

                try:
                    name = msg.split(" ")[1]
                except IndexError:
                    await message.channel.send(
                        "Error archiving budget, please use '**.archivebudget <name e.g. coffee>**'"
                    )
                else:
                    if budget_handler.check_expired(name):
                        await message.channel.send(
                            f"```Your {name} budget has expired.```"
                        )
                    else:
                        await message.channel.send(
                            f"```Your {name} budget has not expired.```"
                        )

            if msg.startswith(".resetbudgetarchive"):
                await message.delete()
                budget_handler.reset_archive
                await message.channel.send("Reset budget archive. - RELAB")


client.run(os.getenv("TOKEN"))
