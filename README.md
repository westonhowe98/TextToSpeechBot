# Discord Text to Speech Bot
> Allow people unable to use voice chat to speak.


Configure a text channel source and a voice channel for output. The bot will convert any messages in the text channel into audio played in the voice channel. 

Run on an ubuntu host.

![](header.png)

## Installation


Install supervisor to auto-start the bot.
```sh
apt-get update
apt-get install -y ffmpeg python3-pip
```

Create directory and clone repo.
```sh
cd /opt
git clone https://github.com/westonhowe98/TextToSpeechBot
cd /opt/TextToSpeechBot
```

Copy the secrets file and populate the token with your [Discord bot token](https://www.writebots.com/discord-bot-token/).
Create a new json file to store [Google Cloud API Service](https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries) credentials.
```sh
cp secrets.example.py secrets.py
nano secrets.py
nano GoogleAppCreds.json
```

Install the required python libraries.
```sh
pip3 install --upgrade discord.py google-cloud-texttospeech
```

Make the script executable and configure the bot as a service. Enable and start the bot.
```sh
chmod +x main.py
cp TextToSpeechBot.service /lib/systemd/system/TextToSpeechBot.service
systemctl daemon-reload
systemctl enable TextToSpeechBot.service
systemctl start TextToSpeechBot.service
```

## Usage

After the bot has started, have it join your Discord server.
Use the prefixed commands in any channel to configure the text and voice channels.
```
>set text #yourTextChannelNameHere
>set voice VoiceChannelNameHere
>save
```

Once the settings have been configured for the first time restart the bot.
```sh
systemctl restart TextToSpeechBot.service
```

## License: GPLv2

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
