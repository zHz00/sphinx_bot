import configparser
import shutil

poll_pause=15
poll_error_pause=60
auto_delete_time=3600
token=""
chats=dict()
new_chats_allowed=True

chats_folder="chats/"

def load():
    global new_chats_allowed
    global poll_pause
    global poll_error_pause
    global auto_delete_time
    global token
    c=configparser.ConfigParser()
    c.read("settings_global.ini",encoding="utf-8")
    new_chats_allowed=bool(c["COMMON"]["new_chats_allowed"])
    poll_pause=int(c["COMMON"]["poll_pause"])
    poll_error_pause=int(c["COMMON"]["poll_error_pause"])
    auto_delete_time=int(c["COMMON"]["auto_delete_time"])
    token=c["COMMON"]["token"]

def load_chat_settings(id):
    global chats
    if id in chats.keys():
        return
    chats[id]=dict()
    filename=chats_folder+str(id)+".ini"
    c=configparser.ConfigParser()
    c.read(filename,encoding="utf-8")
    if "COMMON" not in c:#файл отсутствует или битый. увы, функция не выбрасывает исключения...
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

    