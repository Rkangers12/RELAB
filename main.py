import discord
import os

from json import loads
from dotenv import load_dotenv

from store.handler import Handler
from util.study_tracker import StudyTrack

load_dotenv()
client = discord.Client()
datastore = Handler()
studytrack = StudyTrack(datastore=datastore)

if 'studying' not in datastore.get_keys():
    datastore.overwrite(db_key='studying', db_value=False)


@client.event
async def on_ready():

    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):

    if message.author == client.user:
        return
    
    msg = message.content

    if msg.startswith('.hello'):
        await message.delete()
        await message.channel.send("Hello There!")
    
    if msg.startswith('.snapshot'):
        await message.delete()
        datastore.snapshot()
        await message.channel.send("Your database has been backed up in a secure location.")

    if msg.startswith('.study'):
        await message.delete()

        if not datastore.get_value('studying'):
            studytrack.activate()
            await message.channel.send("Study Mode Activated...")

        else:
            studied = studytrack.deactivate()
            await message.channel.send("Study Mode Deactivated... \nTime Studied: {}".format(studied))

    if msg.startswith('.getstudy'):
        await message.delete()

        if datastore.get_value('studying'):
            await message.channel.send("You began studying: {}".format(studytrack.get_study_start()))

        else:
            await message.channel.send("I have not been informed of your study session")


client.run(os.getenv('TOKEN'))