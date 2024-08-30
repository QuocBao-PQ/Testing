from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
import asyncio
import os

# Load the bot token from an environment variable for security
# TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TOKEN = os.environ.get('token')

# Create bot instance with required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Request the message content intent
bot = commands.Bot(command_prefix='!', intents=intents)


# Command to run your script asynchronously
@bot.command(name='run_script')
async def run_script(ctx):
    try:
        # Prompt user for input
        await ctx.send('Enter the city in Viet Nam that you want to find a job:')
        city = await bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author)
        city = city.content.lower().strip()

        await ctx.send('Enter job title or skill:')
        details_of_job = await bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author)
        details_of_job = details_of_job.content.lower().strip()

        await ctx.send('Enter your email to receive the job listing:')
        recipient_email = await bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author)
        recipient_email = recipient_email.content.strip()
        

        # Run the script asynchronously
        await ctx.send('Running the script...')
        process = await asyncio.create_subprocess_exec(
            'python', 'My_Bot.py',
            city,
            details_of_job,
            recipient_email,
            # 'city', city,
            # 'details_of_job', details_of_job,
            # 'recipient_email', recipient_email,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if stdout:
            await ctx.send(f'```{stdout.decode()}```')
        if stderr:
            await ctx.send(f'Error: ```{stderr.decode()}```')

    except Exception as e:
        await ctx.send(f'Error: {e}')


bot.run(TOKEN)