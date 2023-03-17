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
async def top_movies(ctx, *, arg = "1-10"):
  arg = arg.replace(" ", "")
  try:
    n, m = arg.split("-")
    n = min(max(1, int(n)), 250) - 1
    m = min(max(1, int(m)), 250) - 1
    if n > m:
       n, m = m, n
    msg = await ctx.send(f"Getting the {n+1} - {m+1} top movies...")
  except:
    msg = await ctx.send(f"Error: argument is not in a good format. Try: $top_movies 10 - 25")
    return

  try:
    top250 = ia.get_top250_movies()
    lst = "\n".join([f"{n+i+1}: {movie['title']}" for i, movie in enumerate(top250[n:m+1])])
    
    await msg.edit(content=lst)
  except:
     await msg.edit("Error: An error ocurred")

@bot.command()
async def movie(ctx, *, title):
    msg = await ctx.send(f"Searching for movie {title}...")
    
    try:
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
            movie_message = f"- Title: {movie_title}\n- Rating: {movie_rating}\n- Genres: {movie_genres}\n- Plot: {movie_plot}"
        else:
            movie_message = f"- Title: {movie_title}\n- Rating: {movie_rating}\n- Genres: {movie_genres}\n- No plot available."
        
        await msg.edit(content=movie_message)
    except:
       await msg.edit("Error: An error ocurred")

@bot.command()
async def movie_info(ctx, *, title):
    msg = await ctx.send(f"Searching for information about {title}...")

    try: 
        # Search for the movie
        results = ia.search_movie(title)
        if not results:
            await msg.edit(content=f"No results found for {title}.")
            return

        # Get the first search result (most likely the correct movie)
        movie = ia.get_movie(results[0].getID())

        # Get the information
        movie_title = movie.get('title')
        original_title = movie.get('original title', 'Unknown')
        year = movie.get('year', 'Unknown')
        rating = movie.get('rating', 'Unknown')
        genres = ", ".join(movie.get('genres', []))
        director = movie.get('director', {})[0].get('name', 'Unknown')
        writer = movie.get('writer', [{}])[0].get('name', 'Unknown')
        producer = movie.get('producer', [{}])[0].get('name', 'Unknown')
        production_companies = ", ".join([company.get('name', 'Unknown') for company in movie.get('production companies', [])])
        cast = ", ".join([actor.get('name', 'Unknown') for actor in movie.get('cast', [])[:10]])

        # Build the message
        message = f"- Title: {movie_title}\n"
        message += f"- Original title: {original_title}\n"
        message += f"- Year: {year}\n"
        message += f"- Rating: {rating}\n"
        message += f"- Genres: {genres}\n"
        message += f"- Director: {director}\n"
        message += f"- Writer: {writer}\n"
        message += f"- Producer: {producer}\n"
        message += f"- Production Companies: {production_companies}\n"
        message += f"- Cast: {cast}"

        await msg.edit(content=message)
    except:
       await msg.edit("Error: An error ocurred")

@bot.command()
async def movie_reviews(ctx, *, title):
    msg = await ctx.send(f"Searching for reviews of {title}...")
    
    try:
        # Search for the movie
        results = ia.search_movie(title)
        if not results:
            await msg.edit(content=f"No results found for {title}.")
            return
        
        # Get the first search result (most likely the correct movie)
        movie = ia.get_movie(results[0].getID())
        
        # Get the user reviews
        ia.update(movie, 'reviews')
        user_reviews = movie.get('reviews', [])[:3]
        
        # Show the reviews in different messages
        content = user_reviews[0]['content'] if len(user_reviews[0]['content']) < 1000 else user_reviews[0]['content'][:1000] + "..."
        reviews_str = f"- {user_reviews[0]['title']}  :  {user_reviews[0]['rating']}/10  ({user_reviews[0]['date']})\n{content}\n\n"
        await msg.edit(content=f"Reviews for {movie.get('title')}: \n\n{reviews_str}")

        if len(user_reviews) < 2: return
        for review in user_reviews[1:]:
            content = review['content'] if len(review['content']) < 1000 else review['content'][:1000] + "..."
            await ctx.send(f"- {review['title']}  :  {review['rating']}/10  ({review['date']})\n{content}\n\n")
    except:
       await msg.edit("Error: An error ocurred")

@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages sent by the bot itself
        return

    if message.content.lower() == "hello":
        await message.channel.send("Hello!")

    await bot.process_commands(message)

keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
