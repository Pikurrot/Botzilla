from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keep_alive

load_dotenv()

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="$",
    description="Your favourite slave bot.",
    intents=intents,
)


@bot.command()
async def m(ctx, *, prompt):
  msg = await ctx.send(f"“{prompt}”\n> Generating...")

  await msg.edit(content=f"You said {prompt}, I say xd")


    await msg.edit(content=f"You said {prompt}, I say xd")

keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
