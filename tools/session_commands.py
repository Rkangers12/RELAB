class SessionCommands:
    def __init__(self, datastore, studytrack, gymtrack):

        self._datastore = datastore
        self._studytrack = studytrack
        self._gymtrack = gymtrack

        sessions = ["studying", "gymming"]
        for session in sessions:
            if session not in self._datastore.get_keys():
                self._datastore.overwrite(db_key=session, db_value=False)

    async def study(self, message):
        """activate/deactivate study mode"""

        await message.delete()

        if not self._datastore.get_value("studying"):
            self._studytrack.activate()
            await message.channel.send("```Study Mode Activated...```")

        else:
            studied = self._studytrack.deactivate()
            await message.channel.send(
                f"```Study Mode Deactivated... \n  - Time Studied: {studied}```"
            )

    async def get_study(self, message):
        """retrieve study session information"""

        await message.delete()

        if self._datastore.get_value("studying"):
            await message.channel.send(
                f"```You began studying: {self._studytrack.get_session_start()}```"
            )

        else:
            await message.channel.send("```No currently active study session...```")

    async def gym(self, message):
        """activate/deactivate gym session"""

        await message.delete()

        if not self._datastore.get_value("gymming"):
            self._gymtrack.activate()
            await message.channel.send("```Gym Session Activated...```")

        else:
            exercised = self._gymtrack.deactivate()
            await message.channel.send(
                f"```Gym Session Deactivated... \n  - Exercise duration: {exercised}```"
            )

    async def get_gym(self, message):
        """get gym session information"""

        await message.delete()

        if self._datastore.get_value("gymming"):
            await message.channel.send(
                f"```You began gymming: {self._gymtrack.get_session_start()}```"
            )

        else:
            await message.channel.send("```No active gym session...```")
