from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keep_alive
import imdb

ia = imdb.IMDb()

# bot
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

@bot.command()
async def top_movies(ctx):
  msg = await ctx.send("Accessing IMDb API...")

  top250 = ia.get_top250_movies()
  lst = "\n".join([movie['title'] for movie in top250[:10]])
  
  await msg.edit(content=lst)

@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages sent by the bot itself
        return

    if message.content.lower() == "hello":
        await message.channel.send("Hello!")

    await bot.process_commands(message)

keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
