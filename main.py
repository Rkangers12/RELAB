import discord
import os
from json import loads
from dotenv import load_dotenv

from store.handler import Handler
from util.session_tracker import SessionTrack
from util.summary_report import SummaryReport


load_dotenv()
intents = discord.Intents.all()
client = discord.Client(intents=intents)


datastore = Handler()
studytrack = SessionTrack('study_records', 'studying', datastore=datastore)
gymtrack = SessionTrack('gym_records', 'gymming', datastore=datastore)

sessions = ['studying', 'gymming']

for session in sessions:
    if session not in datastore.get_keys():
        datastore.overwrite(db_key=session, db_value=False)


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

async def study(message):
    """activate/deactivate study mode"""

    await message.delete()

    if not datastore.get_value('studying'):
        studytrack.activate()
        await message.channel.send("**Study Mode Activated...**")

    else:
        studied = studytrack.deactivate()
        await message.channel.send("**Study Mode Deactivated...** \n  - Time Studied: {}".format(studied))

async def get_study(message):
    """retrieve study session information"""

    await message.delete()

    if datastore.get_value('studying'):
        await message.channel.send("You began studying: **{}**".format(studytrack.get_session_start()))

    else:
        await message.channel.send("No currently **active** study session...")

async def gym(message):
    """activate/deactivate gym session"""

    await message.delete()

    if not datastore.get_value('gymming'):
        gymtrack.activate()
        await message.channel.send("**Gym Session Activated...**")

    else:
        exercised = gymtrack.deactivate()
        await message.channel.send("**Gym Session Deactivated...** \n  - Exercise duration: {}".format(exercised))

async def get_gym(message):
    """get gym session information"""

    await message.delete()

    if datastore.get_value('gymming'):
        await message.channel.send("You began gymming: **{}**".format(gymtrack.get_session_start()))

    else:
        await message.channel.send("No **active** gym session...")

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
        await study(message)

    if msg.startswith('.getstudy'):
        await get_study(message)

    if msg.startswith('.gym'):
        await gym(message)

    if msg.startswith('.getgym'):
        await get_gym(message)

    if msg.startswith('.help'):
        await help(message)


client.run(os.getenv('TOKEN'))