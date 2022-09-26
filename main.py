import discord
import os
from dotenv import load_dotenv
from tools.income_commands import IncomeCommands

from store.handler import Handler
from tools.session_commands import SessionCommands
from util.session_tracker import SessionTrack
from util.summary_report import SummaryReport


load_dotenv()
intents = discord.Intents.all()
client = discord.Client(intents=intents)

datastore = Handler()
studytrack = SessionTrack('study_records', 'studying', datastore=datastore)
gymtrack = SessionTrack('gym_records', 'gymming', datastore=datastore)

sesscomms = SessionCommands(datastore=datastore, studytrack=studytrack, gymtrack=gymtrack)
incomcomms = IncomeCommands(datastore=datastore)


@client.event
async def on_ready():
    print('\nWe have logged in as {0.user}'.format(client))

    summaryTask = SummaryReport(
        channel_id=1012023361922150450, 
        intents=intents, 
        client=client,
        sessions=[
            {'classVar': studytrack, 'sessionType': 'Study'},
            {'classVar': gymtrack, 'sessionType': 'Gym'}
        ])

    if not summaryTask.statistic_report.is_running():
        summaryTask.statistic_report.start()  # if the task is not already running, start it.
        print("Booted Background Process: Statistic Reporter - {0.user}\n".format(client))


async def snapshot(message):
    """take a snapshot of the database"""

    await message.delete()
    datastore.snapshot()
    await message.channel.send("**Your database has been backed up in a secure location.**")


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

    support = '```{}\n\n{}\n\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n```'.format(greeting, message2, cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7)
    
    await message.channel.send(support)

@client.event
async def on_message(message):

    if message.author == client.user:
        return
    
    msg = message.content

    # example of how we can restrict functionality to specific channels within the guild
    if message.channel.id == 1012023361922150450:  # channel id of the greetings channel
        if msg.startswith('.hello'):
            await message.delete()
            await message.channel.send("Hi {}, in the {} channel!".format(message.author, message.channel))
                
    if msg.startswith('.snapshot'):
        await snapshot(message)

    if msg.startswith('.study'):
        await sesscomms.study(message)

    if msg.startswith('.getstudy'):
        await sesscomms.get_study(message)

    if msg.startswith('.gym'):
        await sesscomms.gym(message)

    if msg.startswith('.getgym'):
        await sesscomms.get_gym(message)

    if msg.startswith('.help'):
        await help(message)

    if msg.startswith('.setsalary'):
        await incomcomms.set_payroll_data(msg, 'grossSalary')
    
    if msg.startswith('.getsalary'):
        await incomcomms.get_individual_payroll_data(message, 'grossSalary')

client.run(os.getenv('TOKEN'))