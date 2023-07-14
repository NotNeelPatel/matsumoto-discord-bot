import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
import subprocess
import os
import asyncio
import pandas as pd
from ai import prompt
import random

def convert_to_voice(text: str, voice, u_voice = 0):
    """
        Converts text to voice and plays based on user-defined voice
    """
    # Piper location
    PIPER = '/home/neel/github/piper/piper'
    # Installed Models, located at /home/neel/github/models/*
    MODELS = ['danny/en-us-danny-low.onnx', 
                'alan/en-gb-alan-low.onnx', 
                'amy/en-us-amy-low.onnx', 
                'gb_female/en-gb-southern_english_female-low.onnx',  
                'ryan/en-us-ryan-low.onnx'
                ]

    # Subprocess to run bash commands in python
    # although there are ways to interface piper in python directly
    
    model = '/home/neel/github/models/' + MODELS[u_voice]
    echo_proc = subprocess.Popen(["echo", text], stdout=subprocess.PIPE)
    piper_proc = subprocess.Popen([PIPER, "--model", model, "--output_file", 'out.wav'], stdin=echo_proc.stdout)
    piper_proc.wait()
    piper_proc.communicate()
    play_voice(voice)

def play_voice(voice):
    """
    plays voice sound effect, outputs to out.wav, a temporary file
    """
    source = FFmpegPCMAudio('out.wav')
    player = voice.play(source)

def play_sound(voice, sound_effect: str):
    """
    plays given sound effect
    """
    s = './sounds/' + sound_effect + '.mp3'
    print(s)
    source = FFmpegPCMAudio(s)
    player = voice.play(source)

def get_voice(user:str, df) -> int:
    """
    Returns an int, which corresponds to the voice model the user selected, see convert_to_voice
    Returns -1 if user does not have an entry
    """
    if user in df['user'].unique():
        return df.loc[df['user'] == user, 'voice'].item()
    else:
        return -1

def read_user_prefs():
    """
    Returns dataframe of users with their voice preferences and attributes
    """
    return pd.read_csv('voices.csv')

class Matsumoto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def say(self, ctx):
        """
        Bot says whatever user types in chat in their desired voice
        """
        # Only works if user is in a voice channel
        if (ctx.author.voice):
            u_voice = get_voice(str(ctx.message.author), read_user_prefs())

            if ctx.guild.voice_client not in bot.voice_clients:
                voice = await ctx.message.author.voice.channel.connect()
            else:
                voice = ctx.guild.voice_client

            convert_to_voice(ctx.message.content[5:], voice, u_voice)
        else: 
            await ctx.send('You are not in a voice chat!')

    @commands.command()
    async def s(self, ctx):
        """Another way to call say()"""
        ctx.message.content = ',say ' + ctx.message.content[3:]
        await self.say(ctx)

    @commands.command()
    async def stop(self, ctx):
        """Disconnects the bot from voice"""
        await ctx.voice_client.disconnect()
    
    @commands.command()
    async def voice(self, ctx):
        """Assigns voice model to user"""
        # Check what number the user selected, if invalid it assigns 0
        if int(ctx.message.content[7:]) in range(0,5):
            u_voice = int(ctx.message.content[7:])
        else:
            u_voice = 0

        # Find and replace user's current setting
        existing_usr_line = -1
        user = str(ctx.message.author)
        df = read_user_prefs()
        if get_voice(user, df) != -1:
            df.loc[df['user'] == user, 'voice'] = u_voice
        else:
            new_entry = {'user':user,'voice':u_voice}
            df = df._append(new_entry, ignore_index=True)

        print(df)     
        df.to_csv("voices.csv", index=False)
        await ctx.send(f"{'user':user,'voice':u_voice}")
    
    @commands.command()
    async def ps(self, ctx):
        """Plays sound effects in vc"""
        SOUNDS = ['clonk','grr', 'heheheha']
        # Only works in vc
        if (ctx.author.voice):
            if ctx.guild.voice_client not in bot.voice_clients:
                voice = await ctx.message.author.voice.channel.connect()
            else:
                voice = ctx.guild.voice_client
            # Only plays valid sound    
            if str(ctx.message.content[4:]) in SOUNDS:
                play_sound(voice, str(ctx.message.content[4:]))
            else:
                print('y')
                await ctx.send(f'{ctx.message.content[4:]} is not in the list of possible sounds: {SOUNDS}')
    
    @commands.command()
    async def gpt(self, ctx):
        """Prompt AI a question
        Tokens define the length of the response, the higher the token the longer the response
        newprompt is used for when a prompt is specified, otherwise a default prompt is used
        """
        async with ctx.message.channel.typing():
            await bot.change_presence(activity=discord.Streaming(name="handling a GPT prompt", url='https://notneelpatel.github.io'))

            # Tells user that his brain is slow
            think = ['let me think', 'allow me to ponder', 'give me a moment to think', 'give me a second', 'tough request. Let me see', 'allow me to think', 'lets see', '']
            r = random.randint(0, len(think) - 1)
            await ctx.send(f'Hmm {think[r]}...\nDO NOT REQUEST ANOTHER QUESTION WHILE I THINK!! MY BRAIN IS SLOW!!!!')

            # Get attributes of the author
            user = str(ctx.message.author)
            df = read_user_prefs()
            if get_voice(user, df) != -1:
                attribute = user + ". " + str(df.loc[df['user'] == user, 'attributes'].item())
            else:
                attribute = user

            # Get message    
            message_content = ctx.message.content[5:].split()

            # Look for users mentioned in the message
            # by searching for <@
            otherAttributes = []
            cutoff_range = len(message_content)
            tokens = 500
            newprompt = 0
            for i in range(len(message_content)):
                if '<@' in message_content[i]:
                    loop = True
                    j = 20
                    # Some user ids are of differing length, this corrects it
                    while loop:
                        if '>' not in message_content[i][2:j]:
                            loop = False
                        else:
                            j -= 1
                    
                    # When user is found, their id is swapped with their username
                    user_id = message_content[i][2:j]
                    user = str(ctx.guild.get_member(int(user_id)))
                    message_content[i] = user

                    # Look for attributes for the user if possible
                    if get_voice(user, df) != -1:
                        otherAttributes.append('User: ' + user + ', Attributes: ' + str(df.loc[df['user'] == user, 'attributes'].item()))
                    
                # In situations when the number of tokens or if a new prompt is defined
                if message_content[i] == "TOKEN":
                    tokens = int(message_content[i+2])
                    cutoff_range = i

                if  message_content[i] == "NEWPROMPT":
                    newprompt = int(message_content[i+2])

            new_message_content = message_content[0:cutoff_range]
            # Convert message and attributes of users from list to str
            final_message_content = ' '.join(new_message_content)
            final_other_attributes = '\n'.join(otherAttributes)

            # Send text
            text = prompt(final_message_content, attribute, final_other_attributes, tokens, newprompt)
        async with ctx.message.channel.typing():
            await ctx.send(text)
            await bot.change_presence(activity=None)

    @commands.command()
    async def customgpt(self, ctx):
        ctx.message.content = ',gpt ' + ctx.message.content[11:] + ' TOKEN = 1000000 NEWPROMPT = 2'
        await self.gpt(ctx)

    @commands.command()
    async def att(self, ctx, username):
        """Changes the attribute for a user"""
        # Get username of the user
        user = str(ctx.guild.get_member(int(username[2:-1])))

        # Only works if the user is in the server
        if user != None:
            df = read_user_prefs()
            attribute = str(ctx.message.content[len(username) + 6:])

            # Check if user is already in dataframe
            if get_voice(user, df) != -1:
                df.loc[df['user'] == user, 'attributes'] = attribute
            else:
                new_entry = {'user':user,'voice':0, 'attributes': attribute}
                df = df._append(new_entry, ignore_index=True)
            
            df.to_csv("voices.csv", index=False)
            await ctx.send(f'Changed {user}: Attribute: {attribute}')


intents = discord.Intents.all()
intents.message_content = True
intents.members = True

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(","),
    intents=intents
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
 
async def main():
    async with bot:
        await bot.add_cog(Matsumoto(bot))
        await bot.start(TOKEN)

asyncio.run(main())
