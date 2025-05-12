from discord import app_commands
from discord.ext import commands
import discord

from swincer import model as swincer_model
from swincer import controller as swincer_controller





class MemberListTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> list[discord.Member]:
        print(value)
        members = []
        value.replace(">", ">,")
        # remove last comma
        if value[-1] == ",":
            value = value[:-1]
        for mention in value.split(","):
            originator, recipients = mention.split(">")
            originator = interaction.guild.get_member(int(originator.strip()[3:-1]))
            if originator is None:
                raise app_commands.TransformerError(f"Originator {originator} not found")
            members.append(originator)
            for recipient in recipients.split("@"):
                recipient = interaction.guild.get_member(int(recipient.strip()[3:-1]))
                if recipient is None:
                    raise app_commands.TransformerError(f"Recipient {recipient} not found")
                members.append(recipient)
        return members


class Swince(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="swince", description="Register a chug nomination video")
    @app_commands.describe(
        video="We need video proof of the chug",
        originators="Upload the originator in the format @user1@user2, ... (one user can be entered multiple times)",
        recipients="Upload the recipients in the format @user1@user2, ... (one user can be entered multiple times)",
        message="Optional message to include"
    )
    async def swince(
            self,
            interaction: discord.Interaction,
            video: discord.Attachment,
            originators: app_commands.Transform[list[discord.Member], MemberListTransformer],
            recipients: app_commands.Transform[list[discord.Member], MemberListTransformer],
            message: str = None,
    ):
        await interaction.response.defer(thinking=True)
        # TODO : Handle if video is not a video (add a check for direct verification by discord)
        originators_name = ", ".join(m.mention for m in originators)
        recipients_name = ", ".join(m.mention for m in recipients)

        user_controller = swincer_controller.UserController(interaction.guild.id)
        swince_controller = swincer_controller.SwinceController(interaction.guild.id)

        for originator in originators:
            user_controller.add_user(originator.id, originator.name)
        for recipient in recipients:
            user_controller.add_user(recipient.id, recipient.name)
        swince_controller.add_swince(
            from_user=[originator.id for originator in originators],
            to_user=[recipient.id for recipient in recipients],
            date=interaction.created_at,
            origin=interaction.user.id,
        )

        file = await video.to_file()

        await interaction.followup.send(
            f"{originators_name} just nominated {recipients_name}{f"\n>>> {message}" if message is not None else ""}",
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
                command_id = command.id
        await interaction.followup.send(f"You have {score} chugs to do ! ({gotten} gotten, {given} given)\nChop chop lets not waste a second ! Use {"<" if command_id is not None else ""}/swince{str(command_id)+">" if command_id is not None else ""} to register a chug nomination video")

    @app_commands.command(name="scoreboard", description="Check who is the best chugger")
    async def scoreboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        stats_controller = swincer_controller.StatController(interaction.guild.id)
        scores = stats_controller.get_all_score()
        # score is a list of tuples (user_name, gotten, given)
        embed = discord.Embed(title="Scoreboard", color=discord.Color.blue())
        nameList = ""
        scoreList = ""
        detailsList = ""
        for i, (name, gotten, given) in enumerate(scores):
            nameList += f"{i + 1}. {name}\n"
            scoreList += f"{gotten - given}\n"
            detailsList += f"({gotten} gotten, {given} given)\n"
        embed.add_field(name="Name", value=nameList, inline=True)
        embed.add_field(name="Score", value=scoreList, inline=True)
        embed.add_field(name="Details", value=detailsList, inline=True)
        await interaction.followup.send(embed=embed)





