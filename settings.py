import configparser
import shutil
from os import listdir

poll_pause=15
poll_wait_timeout=15
poll_error_pause=60
auto_delete_time=3600
token=""
chats=dict()
messages=dict()
new_chats_allowed=True
owner_id=0
command="uname -a"
command_path="."
answer_retry_time=30

chats_folder="chats/"
default_file="default.ini"
ignore_file="ignore.ini"

proxy_ip=""
proxy_port=""
proxy_user=""
proxy_pass=""


def load():
    global new_chats_allowed
    global poll_pause
    global poll_wait_timeout
    global poll_error_pause
    global auto_delete_time
    global token
    global messages
    global owner_id
    global command
    global command_path
    global proxy_ip,proxy_port,proxy_user,proxy_pass
    global answer_retry_time

    c=configparser.ConfigParser()
    try:
        c.read("settings_global.ini",encoding="utf-8")
    except:
        c.read("settings_global.ini",encoding="utf-8-sig")
    new_chats_allowed=bool(c["COMMON"]["new_chats_allowed"])
    poll_pause=int(c["COMMON"]["poll_pause"])
    poll_wait_timeout=int(c["COMMON"]["poll_wait_timeout"])
    poll_error_pause=int(c["COMMON"]["poll_error_pause"])
    auto_delete_time=int(c["COMMON"]["auto_delete_time"])
    answer_retry_time=int(c["COMMON"]["answer_retry_time"])
    command=c["COMMON"]["command"]
    command_path=c["COMMON"]["command_path"]
    token=c["COMMON"]["token"]
    owner_id=int(c["COMMON"]["owner_id"])
    messages=dict()
    for m in c["MESSAGES"]:
        messages[m]=c["MESSAGES"][m]

    proxy_ip=c["PROXY"]["ip"]
    proxy_port=c["PROXY"]["port"]
    proxy_user=c["PROXY"]["user"]
    proxy_pass=c["PROXY"]["pass"]

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
    try:
        c.read(filename,encoding="utf-8")
    except:
        c.read(filename,encoding="utf-8-sig")
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
    q_id=1
    for m in c["QUESTIONS"]:
        #q_id=int(m[1:])
        q_type=m[0].capitalize()
        if q_type not in ["Q","A"]:
            raise ValueError("Only Q## and A## values allowed in QUESTIONS section")
        if q_type=="Q":
            chats[id][q_type][q_id]=c["QUESTIONS"][m]#вопросы и ответы идут в разные секции но под одинаковым индексом
        if q_type=="A":
            answers=c["QUESTIONS"][m].replace("ё","е").replace("Ё","Е").lower()
            answers=answers.split("|")
            chats[id][q_type][q_id]=answers
            
            q_id+=1#это сделано чтобы можно было нумеровать вопросы не подряд и не следить за нумерацией. главное чтобы номера не повторялись
    chats[id]["ignore"]=bool(int(c["COMMON"]["ignore"]))
    chats[id]["mute_timer"]=int(c["COMMON"]["mute_timer"])
    chats[id]["reactions_max"]=int(c["COMMON"]["reactions_max"])
    chats[id]["reactions_warning"]=int(c["COMMON"]["reactions_warning"])
    chats[id]["reactions_final_warning"]=int(c["COMMON"]["reactions_final_warning"])

def get_proxies():
    url="socks5://"
    if len(proxy_user)>0:
        url+=proxy_user
    if len(proxy_pass)>0:
        url+=":"+proxy_pass+"@"
    else:
        if len(proxy_user)>0:
            url+="@"
    url+=proxy_ip+":"+proxy_port
    if len(proxy_ip)>0:
        return dict(http=url,https=url)
    else:
        return dict()