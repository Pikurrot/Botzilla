import discord
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keep_alive
import imdb
import requests
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

ia = imdb.IMDb()

# bot
load_dotenv()

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(
	command_prefix="$",
	description="Tu esclavo bot favorito",
	intents=intents,
)

@bot.command()
async def commands(ctx):
	commands = ["$m mensaje", "$top_movies n-m", "$movie título", "$movie_info título", "$movie_reviews título"]
	string = "Commandos disponibles:\n" + "\n".join(commands)
	await ctx.send(string)

@bot.command()
async def m(ctx, *, prompt):
	msg = await ctx.send(f"“{prompt}”\n> Generando...")

	await msg.edit(content=f"Este comando aun no esta disponible :(")

@bot.command()
async def top_movies(ctx, *, arg = "1-10"):
	arg = arg.replace(" ", "")
	try:
		n, m = arg.split("-")
		n = min(max(1, int(n)), 250) - 1
		m = min(max(1, int(m)), 250) - 1
		if n > m:
			n, m = m, n
		msg = await ctx.send(f"Obteniendo las {n+1} - {m+1} mejores pelis...")
	except:
		msg = await ctx.send(f"Error: El argumento no esta en un buen formato. Prueba: $top_movies 10 - 25")
		return

	try:
		top250 = ia.get_top250_movies()
		lst = "\n".join([f"{n+i+1}: {movie['title']}" for i, movie in enumerate(top250[n:m+1])])

		await msg.edit(content=lst)
	except:
		await msg.edit("Error: Lo siento, ha ocurrido un error")

@bot.command()
async def movie(ctx, *, title):
	msg = await ctx.send(f"Buscando película \"{title}\"...")
	
	try:
		# search for the movie
		search_results = ia.search_movie(title)
		if not search_results:
			await msg.edit(content=f"No se encontraron resultados para \"{title}\".")
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
			movie_message = f"- Título: {movie_title}\n- Puntuación: {movie_rating}\n- Géneros: {movie_genres}\n- Plot: {movie_plot}"
		else:
			movie_message = f"- Título: {movie_title}\n- Puntuación: {movie_rating}\n- Géneros: {movie_genres}\n- Plot no disponible."
		
		await msg.edit(content=movie_message)
	except:
	   await msg.edit("Error: Lo siento, ha ocurrido un error")

@bot.command()
async def movie_info(ctx, *, title):
	msg = await ctx.send(f"Buscando información para {title}...")

	try: 
		# Search for the movie
		results = ia.search_movie(title)
		if not results:
			await msg.edit(content=f"No results found for \"{title}\".")
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
		message = f"- Título: {movie_title}\n"
		message += f"- Título original: {original_title}\n"
		message += f"- Año: {year}\n"
		message += f"- Puntuación: {rating}\n"
		message += f"- Género: {genres}\n"
		message += f"- Director: {director}\n"
		message += f"- Escritor: {writer}\n"
		message += f"- Productor: {producer}\n"
		message += f"- Empresas productoras: {production_companies}\n"
		message += f"- Reparto: {cast}"

		await msg.edit(content=message)
	except:
	   await msg.edit("Error: Lo siento, ha ocurrido un error")

@bot.command()
async def movie_reviews(ctx, *, title):
	msg = await ctx.send(f"Buscando reseñas para \"{title}\"...")
	
	try:
		# Search for the movie
		results = ia.search_movie(title)
		if not results:
			await msg.edit(content=f"No se encontraror resultados para \"{title}\".")
			return
		
		# Get the first search result (most likely the correct movie)
		movie = ia.get_movie(results[0].getID())
		
		# Get the user reviews
		ia.update(movie, 'reviews')
		user_reviews = movie.get('reviews', [])[:3]
		
		# Show the reviews in different messages
		content = user_reviews[0]['content'] if len(user_reviews[0]['content']) < 1000 else user_reviews[0]['content'][:1000] + "..."
		reviews_str = f"- {user_reviews[0]['title']}  :  {user_reviews[0]['rating']}/10  ({user_reviews[0]['date']})\n{content}\n\n"
		await msg.edit(content=f"Reseñas para {movie.get('title')}: \n\n{reviews_str}")

		if len(user_reviews) < 2: return
		for review in user_reviews[1:]:
			content = review['content'] if len(review['content']) < 1000 else review['content'][:1000] + "..."
			await ctx.send(f"- {review['title']}  :  {review['rating']}/10  ({review['date']})\n{content}\n\n")
	except:
	   await msg.edit("Error: Lo siento, ha ocurrido un error")

@bot.command()
async def cat_fact(ctx):
	try:
		response = requests.get("https://catfact.ninja/fact")
		fact = response.json()["fact"]
		await ctx.send(fact)
	except:
		await ctx.send("Error: Lo siento, ha ocurrido un error")

@bot.event
async def on_message(message):
	if message.author == bot.user:  # ignore messages sent by the bot itself
		return

	if message.content.lower() == "hola":
		await message.channel.send("Hola!")

	await bot.process_commands(message)

@bot.command()
async def joke(ctx):
	try:
		# Send a request to JokeAPI to get a random joke
		response = requests.get("https://v2.jokeapi.dev/joke/Any")
		data = response.json()

		# Check if the response was successful
		if response.status_code == 200 and data["type"] == "single":
			# If the joke is a single line, just send it as a message
			await ctx.send(data["joke"])
		elif response.status_code == 200 and data["type"] == "twopart":
			# If the joke has two parts, send both parts separately
			await ctx.send(data["setup"])
			await ctx.send(data["delivery"])
		else:
			# If the API returns an unexpected response, show an error message
			await ctx.send("Error: No se pudo encontrar un chiste")
	except:
		# If there was an error with the request, show an error message
		await ctx.send("Error: Lo siento, ha ocurrido un error")

def get_location_info(location):
	api_key = "bc4832167e424a2baadaf7ebd4822291"
	url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"

	response = requests.get(url)
	data = response.json()

	if not data["results"]:
		return -1

	result = data["results"][0]
	
	return result

@bot.command()
async def location(ctx, location):
	msg = await ctx.send(f"Buscando ubicación: \"{location}\"...")
	
	try:
		url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"

		response = requests.get(url)

		data = response.json()[0]

		if not data:
			await msg.edit("No results found for the given location.")
			return

		lat, lon = float(data["lat"]), float(data["lon"])

		location_info = get_location_info(location)

		bounds = location_info["bounds"]
		bbox = f"{bounds['southwest']['lng']},{bounds['southwest']['lat']},{bounds['northeast']['lng']},{bounds['northeast']['lat']}"

		map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lon}"

		options = Options()
		options.headless = True
		driver = webdriver.Chrome(options=options)

		driver.get(map_url)

		time.sleep(0.4)

		screenshot = driver.get_screenshot_as_png()

		driver.quit()

		file = discord.File(io.BytesIO(screenshot), filename="map.png")
		
		currency_name = location_info['annotations']['currency']['name']
		currency_symbol = location_info['annotations']['currency']['symbol']

		await msg.edit(file=file)
		await ctx.send(f"{location_info['formatted']}\nCurrency: {currency_name} ({currency_symbol})")
	except:
		await msg.edit("Error: Lo siento, ha ocurrido un error")


keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
