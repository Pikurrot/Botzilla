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

@bot.command()
async def movie(ctx, *, title):
    msg = await ctx.send(f"Searching for movie {title}...")
    
    # search for the movie
    search_results = ia.search_movie(title)
    if not search_results:
        await msg.edit(content=f"No results found for {title}.")
        return
    
    # get the first result
    movie_id = search_results[0].movieID
    movie_info = ia.get_movie(movie_id)
    
    # get movie information
    movie_title = movie_info.get("title", "N/A")
    movie_plot = movie_info.get("plot outline", "N/A")
    movie_rating = movie_info.get("rating", "N/A")
    movie_genres = ", ".join(movie_info.get("genres", []))
    
    # format the message
    if movie_plot:
        movie_message = f"Title: {movie_title}\nRating: {movie_rating}\nGenres: {movie_genres}\nPlot: {movie_plot}"
    else:
        movie_message = f"Title: {movie_title}\nRating: {movie_rating}\nGenres: {movie_genres}\nNo plot available."
    
    await msg.edit(content=movie_message)

@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages sent by the bot itself
        return

    if message.content.lower() == "hello":
        await message.channel.send("Hello!")

    await bot.process_commands(message)

keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
