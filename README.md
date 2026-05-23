=== About ===
This is yet another telegram bot. The main purpose is anti-spam.

It uses strictly defined algorithm that prevents ~99% of spam.

It can only be used in open chats (with usernames), but not in chats connected to channels.

=== Requirements ===
Tested on Python 3.8.

Packages (see requirements.txt):

For use:

* requests
* requests[socks]

For tests:

* pytest
* requests_mock

=== Installation ===
Just run sphinx_bot_start.py . If it detects that this is first run, it asks you about telegram bot token (get it from @BotFather) and some other questions.

When bot is running, you can add it to any group chat as an admin. After that, it will begin operating with default settings. You can change settings if you want, and then restart bot.

Main required permission is to restrict users. Optional permissions are to ban users and to delete messages.

You can make system unit in linux if you run this bot on your server. Making system units is not described here.

=== Algorithm ===

Algorithm is pretty simple:
1. If user enters chat, he is muted immediately for one week. After that mute will be lifted automatically.
2. User can write PM to bot, and he will be asked a question. If he answers correctly, mute will be lifted. In case of wrong answer user can try again indefinitely.
3. If muted user sets reactions to messages, he will be banned after several reactions (can be tweaked in settings).

=== Settings ===
Settings are stored in settings files and can be edited only server-side. You must restart bot after every change.

==== settings/settings_global.ini ====
There are two files, settings_global_default_en.ini and settings_global_default_ru.ini. You can add other for other languages. When you install this bot for the first time, it copies one of these files as settings_global.ini. Main trouble with this file is that you can specify language for public messages in every chat you have, but you can't specify many languages for bot PM. This file defines language for bot PM messages. If you have several chats with different languages, then public messages can be specified for every chat, but if any user writes PM to bot, he will see messages from this file regardless from chat's language. This problem now have no solution.


Now let me explain options of these files.

[COMMON]
new_chats_allowed = 1 #use 0 if you don't want to be added to new chats
poll_pause = 5 #[sec] pause between requests to telegram servers
poll_wait_timeout = 30 #[sec] wait time if no new updates from telegram server are available
poll_error_pause = 9 #[sec] pause if previous request ended with error
answer_retry_time = 60 #[sec] if user answers incorrectly, he must wait some time before next question
auto_delete_time = 3599 #[sec] timer for deleting greeting message. Please note that list of greeting messages is stored only in RAM, so if you restart your bot, then no messages will be deleted
token = XXXX #get it from @BotFather
owner_id = XXXX #optional. Bot answers to some additional commands to owner. You can get owner id with @Getmyid_bot
command = uname -a #you can define ONE command that owner can run using "test_command" feature. Write it here
command_path = . #folder for test_command
language = ru #default language for new chants
[MESSAGES]
#This section is self-explanatory. User will get these messages when he write PM to bot. Wildcards are supported only in certain messages. Please see original file for exapmles.
[PROXY]
#You can specify proxy access via socks5. Other types are not supported.

==== chats/\<id\>.ini ====
Every group chat have own settings file. If new_chats_allowed is equal to 1, then default_en.ini or default_ru.ini is selected and copied as <id>.ini. Otherwise, ignore_??.ini is used.

Only useful option of igrnore_??.ini is ignore=1. Every time your bot is added to unauthorized chat, new settings file with ignore option will be created. Please note that if you change new_chats_allowed settings in global file, ignored files will not be replaced. But you can replace them manually with correct version even if new_chats_allowed is set to 0.

Now let me explain options of chat files.

[COMMON]
ignore = 0 #if it is 1, then bot will not operate in this chat even if it has admin rights
mute_timer = 604800 #[sec] timer for mute for new members. Set to 0 for permanent mute.
reactions_max = 10 #How many reactions must set restricted user to get ban.
reactions_warning = 5 #First warning
reactions_final_warning = 8 #Second and final warning
[MESSAGES]
profile= profile #text for #I in next messages
#Please note that #N and #I wildcards are supported only in messages that use it in default file.
[QUESTIONS]
Q1 = Please write: i'm a human
A1 = i'm a human
#You can make questions out of order and some numbers can be omitted. But question and answer must have equal numbers. You can specify several answers with \| character.

=== Licence and author information ===
MIT Licence. See LICENCE.txt file for details.
(C) 2025-2026 zHz
You can contact me via Telegram @zHz01
Also, please visit project's github page:
https://github.com/zHz00/sphinx_bot
