#!/usr/bin/env python3

import json
import asyncio
import discord
from discord.ext import commands
from google.cloud import texttospeech

from secrets import *

SettingsFile = "settings.json"
SoundFile = "speech.mp3"

GoogleApiFile = "GoogleAppCreds.json"

Settings = {
    "text": "",
    "voice": "General",
    "ServerID": "",
}
References = {}

VoiceClient = None


# Bot invite URL
# https://discord.com/api/oauth2/authorize?client_id=783437282811707442&scope=bot&permissions=8

def main():
    bot.run(Token)


bot = commands.Bot(command_prefix='>')


def getSettingsStr():
    msg = "TTS Bot Settings:\n\n"
    for key, value in Settings.items():
        msg += "\t%s : %s\n" % (key, value)

    return msg


def processSettings():
    global References
    channelId = int(Settings["text"][2:-1])

    References["Server"] = bot.get_guild(Settings["ServerID"])
    References["TextChannel"] = bot.get_channel(channelId)
    References["VoiceChannel"] = discord.utils.get(References["Server"].voice_channels, name=Settings["voice"])


def isReady():
    try:
        if References["Server"] is None:
            return False

        if References["TextChannel"] is None:
            return False

        if References["VoiceChannel"] is None:
            return False
    except KeyError:
        return False

    return True


def getAudio(inputStr):
    # Instantiates a client
    tts = texttospeech.TextToSpeechAsyncClient.from_service_account_json(GoogleApiFile)

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=inputStr)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        {"language_code": "en-US", "ssml_gender": texttospeech.SsmlVoiceGender.MALE, "name": "en-US-Wavenet-I"})

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig({"audio_encoding": texttospeech.AudioEncoding.MP3})

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = tts.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # The response's audio_content is binary.
    with open(SoundFile, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)


@bot.event
async def on_ready():
    try:
        await load()
    except FileNotFoundError:
        print("No settings file found.")


@bot.command()
async def set(ctx, key, value):
    global Settings
    global References

    Settings["ServerID"] = ctx.guild.id

    if key in Settings.keys():
        Settings[key] = value
        await ctx.send("Set %s to %s." % (key, value))
        processSettings()
    else:
        await ctx.send("Invalid setting passed.")


@bot.command()
async def info(ctx):
    await ctx.send(getSettingsStr())


@bot.command()
async def save(ctx):
    with open(SettingsFile, 'w') as file:
        file.write(json.dumps(Settings))

    await ctx.send("Settings saved!")


@bot.command()
async def load(ctx=None):
    global Settings
    global References
    global VoiceClient

    if ctx != None:
        Settings["ServerID"] = ctx.guild.id

    if VoiceClient is not None:
        References["VoiceChannel"].disconnect()
        VoiceClient = None

    with open(SettingsFile, 'r') as file:
        Settings = json.loads(file.read())

    processSettings()
    print("Settings loaded:\n\n" + getSettingsStr())

    VoiceClient = await References["VoiceChannel"].connect()

    if ctx != None:
        await ctx.send("Settings loaded:\n\n" + getSettingsStr())


Messages = []


@bot.event
async def on_message(message):
    if isReady():
        if message.author != bot.user:
            if message.content[0] != ">":
                if message.channel == References["TextChannel"]:
                    Messages.append(message.content)
                    print(message.content)

    if len(Messages) > 0 and not VoiceClient.is_playing():
        msg = Messages.pop()
        getAudio(msg)

        VoiceClient.play(discord.FFmpegPCMAudio(SoundFile), after=None)

        while VoiceClient.is_playing():
            await asyncio.sleep(0.5)

    await bot.process_commands(message)


main()
