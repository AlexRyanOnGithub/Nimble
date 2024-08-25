# Nimble

## Warning
***Use at your own risk. By executing this software you (the reader) are responsible for any form of damage it may cause to you or others.***

***On a side note, know and understand the [rate limits](https://platform.openai.com/docs/guides/rate-limits/usage-tiers) your OpenAI dev account has before execution.***

## Goal
Nimble is a simple CLI that's able to take a PDF or TXT, extract the main body
text from it, and convert that to an audio file using [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech/overview).

## Requirements

- OpenAI's TTS API speech recognition model to perform the narration
    - An [$OPENAI_API_KEY](https://platform.openai.com/api-keys) environment variable.

- This program relies on the following dependencies:
```
pip install pypdf tqdm
```

## Features
- 5 different audio output formats (per OpenAI's docs)
- All the languages supported by OpenAI's TTS API
- Ability to download AI generated narration directly to your own device

## Usage

Below is an example of how it should be used:
```
python3 nimble.py --doc ~/path/to/pdf/or/sample.txt -a ~/path/to/save/your/audiofile/ --range 35 45 --voice echo --model tts-1-hd
```

The output audio is split amongst several parts saved to the specified folder using the following format as an example:

```
part-36-the-odyssey.mp3
part-37-the-odyssey.mp3
part-38-the-odyssey.mp3
etc...

```

## Issues
Please submit a bug report on Github!
