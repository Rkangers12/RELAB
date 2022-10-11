import discord
import os
from uuid import uuid4
from dotenv import load_dotenv

from store.handler import Handler
from tools.income_commands import IncomeCommands
from tools.session_commands import SessionCommands
from util.handle_times import HandleTimes
from util.session_tracker import SessionTrack
from jobs.payslip_report import PayslipReport
from jobs.summary_report import SummaryReport


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


@client.event
async def on_ready():
    print("\nWe have logged in as {0.user}".format(client))

    summaryTask = SummaryReport(
        channel_id=1012023361922150450,
        intents=intents,
        client=client,
        sessions=[
            {"classVar": studytrack, "sessionType": "Study"},
            {"classVar": gymtrack, "sessionType": "Gym"},
        ],
    )

    if not summaryTask.statistic_report.is_running():
        summaryTask.statistic_report.start()  # if the task is not already running, start it.
        print("Booted Background Process: Statistic Reporter - {0.user}".format(client))

    payslipTask = PayslipReport(
        channel_id=1012023361922150450, intents=intents, client=client
    )

    if not payslipTask.payslip_reporter.is_running():
        payslipTask.payslip_reporter.start()  # if the task is not already running, start it.
        print("Booted Background Process: Payslip Reporter - {0.user}\n".format(client))


async def snapshot(message):
    """take a snapshot of the database"""

    await message.delete()
    datastore.snapshot()
    await message.channel.send(
        "**Your database has been backed up in a secure location.**"
    )


async def help(message):
    """display helper information regarding RELAB"""

    await message.delete()
    greeting = "Hi, Welcome to 'Ranveer's Easy Life Autonomy Bot' or 'RELAB' for short."
    message2 = "I see that you have requested some help, here is a breakdown of my current services:"
    cmd1 = "    - .hello    -> I provide a greeting."
    cmd2 = "    - .snapshot -> I perform a backup of your existing data to keep it extra safe. xD"
    cmd3 = "    - .study    -> I `activate/deactivate` study mode and make a log of the session."
    cmd4 = "    - .getstudy -> I tell you how long your study session has been active."
    cmd5 = "    - .gym    -> I `activate/deactivate` gym mode and make a log of the session."
    cmd6 = "    - .getgym -> I tell you how long your gym session has been active."
    cmd7 = "    - .help     -> I provide some help to yourself, as is occurring now!"

    support = "```{}\n\n{}\n\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n```".format(
        greeting, message2, cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7
    )

    await message.channel.send(support)


@client.event
async def on_message(message):

    msg = message.content

    if message.author == client.user:
        if msg.startswith(".payslip"):
            pass
        else:
            return

    # example of how we can restrict functionality to specific channels within the guild
    if message.channel.id == 1012023361922150450:  # channel id of the greetings channel
        if msg.startswith(".hello"):
            await message.delete()
            await message.channel.send(
                "Hi {}, in the {} channel!".format(message.author, message.channel)
            )

    if msg.startswith(".snapshot"):
        await snapshot(message)

    if msg.startswith(".study"):
        await sesscomms.study(message)

    if msg.startswith(".getstudy"):
        await sesscomms.get_study(message)

    if msg.startswith(".gym"):
        await sesscomms.gym(message)

    if msg.startswith(".getgym"):
        await sesscomms.get_gym(message)

    if msg.startswith(".help"):
        await help(message)

    if msg.startswith(".setsalary"):
        await message.delete()
        resp = inc_coms.set_payroll(msg, "grossSalary")

        if resp == 200:
            await message.channel.send("**Gross Salary** details updated. - RELAB")
        elif resp == 404:
            await message.channel.send("Please provide appropriate payroll data.")

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
            await message.channel.send("Please provide appropriate payroll data.")

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
            await message.channel.send("Please provide appropriate payroll data.")

    if msg.startswith(".getpaydate"):
        await message.delete()
        comms = "Payroll details by RELAB: \n    - Next Pay Day: **{}**"
        await message.channel.send(
            comms.format(
                hand_time.format_a_day(int(inc_coms.get("payDay")), weekday=True)
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
            comms.format("active" if inc_coms.sl_check("activeSL") else "inactive")
        )

    if msg.startswith(".takehome"):
        await message.delete()
        await message.channel.send(
            "Your income after tax is **£{}** (**{}**). - RELAB".format(
                inc_coms.get_takehome(),
                hand_time.format_a_day(int(inc_coms.get("payDay")), weekday=True),
            )
        )

    if msg.startswith(".payrollsettings"):
        await message.delete()
        comms = (
            "Payroll details by RELAB:\n    "
            "- Gross Salary: **£{}**\n    "
            "- Notionals: **£{}**\n    "
            "- Next Pay Day: **{}**\n    "
            "- Student Loan: **{}**"
        )

        await message.channel.send(
            comms.format(
                inc_coms.get("grossSalary"),
                inc_coms.get("notionals"),
                hand_time.format_a_day(int(inc_coms.get("payDay")), weekday=True),
                "active" if inc_coms.sl_check("activeSL") else "inactive",
            )
        )

    if msg.startswith(".payslip"):
        await message.delete()

        slip = inc_coms.get_payslip()

        comm1 = "**Payslip #{} RELAB**:\n".format(str(uuid4().hex[:10]))
        comm2 = "```    - Gross income: £{}\n    ".format(
            round(slip.get("gross", 0) / 12, 2)
        )
        comm3 = "- Tax paid: - £{}\n    ".format(slip.get("tax", 0))
        comm4 = "- Employee NIC: - £{}\n    ".format(slip.get("nic", 0))
        if inc_coms.sl_check("activeSL"):
            comm5 = "- Student loan paid: - £{}\n    ".format(slip.get("slt", 0))
        else:
            comm5 = ""
        comm6 = "\n    - Income recievable: £{}```".format(slip.get("takehome", 0))

        await message.channel.send(comm1 + comm2 + comm3 + comm4 + comm5 + comm6)


client.run(os.getenv("TOKEN"))
