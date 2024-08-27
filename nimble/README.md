# Nimble

## Warning
***Know and understand the [rate limits](https://platform.openai.com/docs/guides/rate-limits/usage-tiers) your OpenAI dev account has before execution. When you execute this software you take full responsibility for any OpenAI account violations.***

***Pricing for using the API is available [here](https://openai.com/api/pricing/)***

## Goal
Nimble is a simple CLI that's able to take an entire PDF or TXT, extract the main body
text from it, and convert that to separate audio files using [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech/overview).

## Requirements

### Supported OSes
```
Debian/Ubuntu
Mac OS
Windows
```
- OpenAI's TTS API speech recognition model to perform the narration
    - An [$OPENAI_API_KEY](https://platform.openai.com/api-keys) environment variable.

- This program also requires these dependencies to be installed:
```
pip install openai pypdf tqdm
```

## Usage

Below is an example of how it should be used:
```
python3 nimble.py --doc ~/path/to/pdf/or/sample.txt -a ~/path/to/save/your/audiofiles.mp3 --range 35 45 --voice echo --model tts-1-hd
```

The output audio is split amongst several parts saved to the specified folder using the following format as an example:

```
┬─[alex@alex-tablet:~/D/c/p/nimble]─[07:43:02 PM]─[G:main]
╰─>$ python3 nimble.py --doc "tale-of-genji.txt" -a "genji.mp3"

            Model: tts-1,
            Audio: genji.mp3,
            TXT:   tale-of-genji.txt
                
working on task: part-3-genji.mp3
working on task: part-5-genji.mp3
working on task: part-2-genji.mp3
working on task: part-7-genji.mp3
working on task: part-1-genji.mp3
working on task: part-6-genji.mp3
working on task: part-4-genji.mp3
working on task: part-8-genji.mp3

```

## Features
- 5 different audio output formats (per OpenAI's docs)
- All the languages supported by OpenAI's TTS API
- Ability to download AI generated narration directly to your own device
- Use OpenAI to narrate an entire PDF or TXT

## Issues
Please submit a bug report on Github!
