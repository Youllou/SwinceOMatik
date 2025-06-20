from discord import app_commands
from discord.ext import commands
import discord

from SwinceOMatik.swincer import controller as swincer_controller





class MemberListTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> list[discord.Member]:
        members = []
        for mention in value.split(" "):
            mention = mention.strip()
            if mention.startswith("<@") and mention.endswith(">"):
                user_id = int(mention[2:-1])
                member = interaction.guild.get_member(user_id)
                if member is not None:
                    members.append(member)
                else:
                    await interaction.response.send_message(f"User with ID {user_id} not found in the guild.", ephemeral=True)
                    return []
            else:
                await interaction.response.send_message(f"Invalid mention format: {mention}", ephemeral=True)
                return []
        return members


class Swince(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="swince", description="Register a chug nomination video")
    @app_commands.describe(
        video="We need video proof of the chug",
        originators="Upload the originators in the format @user1 @user2 ... (one user can be entered multiple times)",
        targets="Upload the targets in the format @user1 @user2 ... (one user can be entered multiple times)",
        message="Optional message to include"
    )
    async def swince(
            self,
            interaction: discord.Interaction,
            video: discord.Attachment,
            originators: app_commands.Transform[list[discord.Member], MemberListTransformer],
            targets: app_commands.Transform[list[discord.Member], MemberListTransformer],
            message: str = None,
    ):
        await interaction.response.defer(thinking=True)
        # TODO : Handle if video is not a video (add a check for direct verification by discord)
        originators_name = ", ".join(m.mention for m in originators)
        targets_name = ", ".join(m.mention for m in targets)

        user_controller = swincer_controller.UserController(interaction.guild.id)
        swince_controller = swincer_controller.SwinceController(interaction.guild.id)


        for originator in originators:
            user_controller.add_user(originator.id, originator.name)
        for recipient in targets:
            user_controller.add_user(recipient.id, recipient.name)
        swince_controller.add_swince(
            from_user=[originator.id for originator in originators],
            to_user=[recipient.id for recipient in targets],
            date=interaction.created_at,
            origin=interaction.user.id,
        )

        file = await video.to_file()
        to_send = f"{originators_name} just nominated {targets_name}"
        to_send+= f"\n>>> {message}" if message is not None else ''
        await interaction.followup.send(
            to_send,
            ephemeral=False, file=file
        )

    @app_commands.command(name="score", description="Let's see how many chugs you need to do")
    async def score(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        user_controller = swincer_controller.UserController(interaction.guild.id)
        user = user_controller.get_user(interaction.user.id)
        if user is None:
            await interaction.followup.send("You are not registered in the database")
            return
        stats_controller = swincer_controller.StatController(interaction.guild.id)
        gotten,given = stats_controller.get_score(user.id)
        score = gotten - given
        myCommands = self.get_app_commands()  # `get_app_commands()` not `get_commands()`

        command_id = None
        for command in myCommands:
            if command.name == "swince":
                try:
                    command_id = command.id
                except AttributeError:
                    command_id = None
        await interaction.followup.send(f"You have {score} chugs to do ! ({gotten} gotten, {given} given)\nChop chop lets not waste a second ! Use {'<' if command_id is not None else ''}/swince{(':'+str(command_id)+'>') if command_id is not None else ''} to register a chug nomination video")

    @app_commands.command(name="scoreboard", description="Check who is the best chugger")
    async def scoreboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        stats_controller = swincer_controller.StatController(interaction.guild.id)
        user_controller = swincer_controller.UserController(interaction.guild.id)

        users = user_controller.get_all_users()
        for user in users:
            discord_user = interaction.guild.get_member(user.id)
            if discord_user:
                nickname = discord_user.nick if discord_user.nick else discord_user.display_name
                user_controller.update_user_name(user.id, nickname)

        scores = stats_controller.get_all_score()
        scores.sort(key=lambda x: -(x[1] - x[2]))
        # score is a list of tuples (user_name, gotten, given)
        nameList = []
        scoreList = []
        detailsList = []
        longestName = 0



        for (name, gotten, given) in scores:
            nameList.append(name)
            print(f"len of current : {len(name)}")
            if len(name) > longestName:
                longestName = len(name)
                print(f"new longest : {longestName}")
            scoreList.append(gotten - given)
            detailsList.append(f"{gotten} 📥, {given} 📨")
        print(nameList)
        print("Name")
        print("Name".center(longestName))
        message = "# Scoreboard\n"
        message += "```\n"
        message += f"|{'Name'.center(longestName+1)} | {'Score'.center(5)} | {'Details'}\n"
        message += f"|{'-' * (longestName+1)}-|-{'-' * 6}|{'---' * 3} \n"
        for i in range(len(nameList)):
            name = nameList[i]
            score = scoreList[i]
            details = detailsList[i]
            message += f"| {name:<{longestName}} | {str(score).center(5)} | {details}\n"
        message += "```"

        await interaction.followup.send(message)





