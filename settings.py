import configparser
import shutil
from os import listdir

poll_pause=15
poll_error_pause=60
auto_delete_time=3600
token=""
chats=dict()
messages=dict()
new_chats_allowed=True

chats_folder="chats/"
default_file="default.ini"
ignore_file="ignore.ini"

def load():
    global new_chats_allowed
    global poll_pause
    global poll_error_pause
    global auto_delete_time
    global token
    global messages
    c=configparser.ConfigParser()
    c.read("settings_global.ini",encoding="utf-8")
    new_chats_allowed=bool(c["COMMON"]["new_chats_allowed"])
    poll_pause=int(c["COMMON"]["poll_pause"])
    poll_error_pause=int(c["COMMON"]["poll_error_pause"])
    auto_delete_time=int(c["COMMON"]["auto_delete_time"])
    token=c["COMMON"]["token"]
    messages=dict()
    for m in c["MESSAGES"]:
        messages[m]=c["MESSAGES"][m]

    file_list=listdir(chats_folder)
    id=0
    for file in file_list:
        if file==default_file or file==ignore_file:
            continue
        try:
            id=int(file[:-4])
            load_chat_settings(id)
            print(f"chat loaded: {id}")
        except:#что-то не так с именем файла
            print("error with file name while loading chat:"+file)
            continue


def load_chat_settings(id):
    global chats
    if id in chats.keys():
        return
    chats[id]=dict()
    filename=chats_folder+str(id)+".ini"
    c=configparser.ConfigParser()
    c.read(filename,encoding="utf-8")
    if "COMMON" not in c:#файл отсутствует или битый. увы, функция не выбрасывает исключения...
        print("creating new chat ini-file")
        if new_chats_allowed:
            shutil.copyfile(chats_folder+"default.ini",filename)
            c.read(filename,encoding="utf-8")
        else:
            shutil.copyfile(chats_folder+"ignore.ini",filename)
            c.read(filename,encoding="utf-8")
    chats[id]["MSG"]=dict()
    for m in c["MESSAGES"]:
        chats[id]["MSG"][m]=c["MESSAGES"][m]
    chats[id]["Q"]=dict()
    chats[id]["A"]=dict()
    for m in c["QUESTIONS"]:
        q_id=int(m[1:])
        q_type=m[0].capitalize()
        if q_type not in ["Q","A"]:
            raise ValueError("Only Q## and A## values allowed in QUESTIONS section")
        chats[id][q_type][q_id]=c["QUESTIONS"][m]#вопросы и ответы идут в разные секции но под одинаковым индексом
    chats[id]["ignore"]=bool(int(c["COMMON"]["ignore"]))
    chats[id]["mute_timer"]=int(c["COMMON"]["mute_timer"])

    