# Matsumoto
### A Super AI for my Discord Servers!

This is my discord bot that can answer questions and you can feed him information about you to make it more personalized! He can also play sounds and convert text to speech for those in a voice channel!

Matsumoto is ran completely locally on a machine of your choice, including the AI LLM!

I made this bot just for me, but my code may be helpful to someone.
## Command List
Matsumoto can be summoned using the prefix ','
 - ,say: says whatever you type in a voice chat
 - ,stop: disconnects Matsumoto from the voice chat
 - ,voice: change the voice to another model
 - ,ps: plays sound effect in voice chat
 - ,gpt: ask Matsumoto a question and he'll respond to you
 - ,customgpt: Allows you to have more granular control of Matsumoto if you want him to behave in a certain way
 - ,att: Set custom attributes to a user. Ex: ,att @ExampleUser They are a cool funny person who loves anime. Matsumoto will take that into consideration when @ExampleUser is mentioned or if they ask him a question.

## Requirements/Usage:

#### From pip:
 - discord.py
 - discord.py\[voice]
 - dotenv
 - pandas
 - ffmpeg
 - llama\_cpp_python

#### Packages:
 - python3
 - pip
 - ffmpeg
 - piper
 
#### Other:
 - piper voice models
 - an LLM compatible with llama\_cpp
 - sound effects (optional)

#### Hardware:
 - The better the computer, the faster the gpt prompts are processed

To start Matsumoto:

```python3 matsumoto.py```