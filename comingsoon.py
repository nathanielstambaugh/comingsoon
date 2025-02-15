from datetime import datetime
import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import tasks, commands
import logging

# Set up logging
logging.basicConfig(filename='stock_check.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = 'MTMzOTk5NjMxNzMxMjc0OTYxMA.GpHg2v.KHEPSYfqKxaLjLXDZEk9FjE_F8-c5G04tZxnzU'  # Replace with your Discord bot token
CHANNEL_ID = 1339996037372317737  # Replace with your Discord channel ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    logging.info('Logged in as %s', bot.user)
    check_stock.start()

@tasks.loop(minutes=30)
async def check_stock():
    url = "https://www.bestbuy.com/site/nvidia-geforce-rtx-5080-16gb-gddr7-graphics-card-gun-metal/6614153.p?skuId=6614153"
    headers = {"User-Agent":"Mozilla/5.0","cache-control":"max-age=0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Check for "Sold Out", "Coming Soon", and "Add to Cart"
    status_elements = soup.find_all(string=["Sold Out", "Coming Soon", "Add to Cart"])
    stock_status = "Not Found"

    for element in status_elements:
        parent_div = element.find_parent("div")
        if parent_div and "Sold Out" in element:
            stock_status = "Sold Out"
            logging.info("The RTX 5080 is currently sold out.")
        elif parent_div and "Coming Soon" in element:
            stock_status = "Coming Soon"
        elif parent_div and "Add to Cart" in element:
            stock_status = "Add to Cart"

    channel = bot.get_channel(CHANNEL_ID)

    if stock_status in ["Add to Cart", "Coming Soon", "Not Found"]:
        if stock_status == "Add to Cart":
            message = "The RTX 5080 is available for purchase!"
        elif stock_status == "Coming Soon":
            message = "The RTX 5080 is coming soon."
        else:
            message = "Stock status not found."

        logging.info(message)
        await channel.send(message)

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    print(formatted_now + " ----->", stock_status)

@check_stock.before_loop
async def before_check_stock():
    await bot.wait_until_ready()

bot.run(TOKEN)
