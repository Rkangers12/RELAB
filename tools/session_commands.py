class SessionCommands:
    def __init__(self, datastore, studytrack, gymtrack):

        self._datastore = datastore
        self._studytrack = studytrack
        self._gymtrack = gymtrack

    async def study(self, message, user):
        """activate/deactivate study mode"""

        await message.delete()

        if not self._datastore.get_nested_value(["sessions", user, "studying"]):
            self._studytrack.activate(user)
            await message.channel.send("```Study Mode Activated...```")

        else:
            studied = self._studytrack.deactivate(user)
            await message.channel.send(
                f"```Study Mode Deactivated... \n  - Time Studied: {studied}```"
            )

    async def get_study(self, message, user):
        """retrieve study session information"""

        await message.delete()

        if self._datastore.get_nested_value(["sessions", user, "studying"]):
            await message.channel.send(
                f"```You began studying: {self._studytrack.get_session_start(user)}```"
            )

        else:
            await message.channel.send("```No currently active study session...```")

    async def gym(self, message, user):
        """activate/deactivate gym session"""

        await message.delete()

        if not self._datastore.get_nested_value(["sessions", user, "gymming"]):
            self._gymtrack.activate(user)
            await message.channel.send("```Gym Session Activated...```")

        else:
            exercised = self._gymtrack.deactivate(user)
            await message.channel.send(
                f"```Gym Session Deactivated... \n  - Exercise duration: {exercised}```"
            )

    async def get_gym(self, message, user):
        """get gym session information"""

        await message.delete()

        if self._datastore.get_nested_value(["sessions", user, "gymming"]):
            await message.channel.send(
                f"```You began gymming: {self._gymtrack.get_session_start(user)}```"
            )

        else:
            await message.channel.send("```No active gym session...```")
