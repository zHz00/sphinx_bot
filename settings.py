import configparser
import shutil
import os

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
language="en"

chats_folder="chats/"
settings_folder="settings/"
default_file_prefix="default_"
ignore_file_prefix="ignore_"
log_folder="logs/"
log_readable=log_folder+"message_log_readable.txt"
log_raw=log_folder+"message_log.txt"
settings_file="settings_global.ini"
settings_file_default_prefix="settings_global_default_"
ini_suffix=".ini"

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
    global language

    if os.path.isfile(settings_folder+settings_file)==False:
        #new installation
        langs=[]
        files=os.listdir(".")
        for file in files:
            if file.startswith(settings_file_default_prefix):
                langs.append(file.removeprefix(settings_file_default_prefix).removesuffix(ini_suffix))
        print("Select default language for bot. Available languages: ",end="")
        print(", ".join(langs))
        lang="/"
        while lang not in langs:
            lang=input("Enter language code:")
        shutil.copy(settings_folder+settings_file_default_prefix+lang+ini_suffix,settings_folder+settings_file)


    c=configparser.ConfigParser()
    try:
        c.read(settings_folder+settings_file,encoding="utf-8")
    except:
        c.read(settings_folder+settings_file,encoding="utf-8-sig")
    new_chats_allowed=bool(c["COMMON"]["new_chats_allowed"])
    poll_pause=int(c["COMMON"]["poll_pause"])
    poll_wait_timeout=int(c["COMMON"]["poll_wait_timeout"])
    poll_error_pause=int(c["COMMON"]["poll_error_pause"])
    auto_delete_time=int(c["COMMON"]["auto_delete_time"])
    answer_retry_time=int(c["COMMON"]["answer_retry_time"])
    command=c["COMMON"]["command"]
    command_path=c["COMMON"]["command_path"]
    language=c["COMMON"]["language"]
    try:
        owner_id=int(c["COMMON"]["owner_id"])
    except:
        owner_id=int(input("It seems that you have new installation. Please enter bot owner id or zero to skip:"))
        c["COMMON"]["owner_id"]=str(owner_id)
        f=open(settings_folder+settings_file,"w",encoding="utf-8")
        c.write(f)
        f.close()
        print("Written to file.")

    token=c["COMMON"]["token"]
    if token=="XXXX" or len(token)==0:#new installation
        token=input("It seems that you have new installation. Please enter telegram bot token. WARNING! This will be saved as unencryped text:")
        c["COMMON"]["token"]=token
        proxy_set=input("Set proxy settings?(y/n):")
        proxy_set=proxy_set.lower()
        if proxy_set=="y":
            print("Now you will be asked about proxy settings, which takes 4 steps. If you don't know an answer, press Enter.")
            print("Only SOCKS 5 proxies are supported. You can change settings later by editing the file "+settings_folder+settings_file)
            proxy_ip=input("(1/4) Enter proxy IP address or domain name:")
            proxy_port=input("(2/4) Enter port:")
            proxy_user=input("(3/4) Enter username (Enter if none):")
            proxy_pass=input("(4/4) Enter proxy password. WARNING! This will be saved as unencrypted text! (Enter if none):")
            c["PROXY"]["ip"]=proxy_ip
            c["PROXY"]["port"]=proxy_port
            c["PROXY"]["user"]=proxy_user
            c["PROXY"]["pass"]=proxy_pass
        f=open(settings_folder+settings_file,"w",encoding="utf-8")
        c.write(f)
        f.close()
        print("Written to file.")
    messages=dict()
    for m in c["MESSAGES"]:
        messages[m]=c["MESSAGES"][m]

    proxy_ip=c["PROXY"]["ip"]
    proxy_port=c["PROXY"]["port"]
    proxy_user=c["PROXY"]["user"]
    proxy_pass=c["PROXY"]["pass"]

    file_list=os.listdir(chats_folder)
    id=0
    for file in file_list:
        if file.startswith(default_file_prefix) or file.startswith(ignore_file_prefix):
            continue
        try:
            id=int(file[:-4])
            load_chat_settings(id)
            print(f"chat loaded: {id}")
        except:#something is wrong with name
            print("error with file name while loading chat:"+file)
            continue
    


def load_chat_settings(id,stop_recursion=False):
    global chats
    if id in chats.keys() and len(chats[id].keys())>0:
        return None
    chats[id]=dict()
    filename=chats_folder+str(id)+ini_suffix
    c=configparser.ConfigParser()
    try:
        c.read(filename,encoding="utf-8")
    except:
        c.read(filename,encoding="utf-8-sig")
    if "COMMON" not in c:#file is absent or incorrect. please note that c.read don't make exceptions when file is absent
        if stop_recursion:
            print("ERROR, incorrect chat file. Please check: "+filename)
            return None
        print("creating new chat ini-file")
        if new_chats_allowed:
            shutil.copyfile(chats_folder+default_file_prefix+language+ini_suffix,filename)
            return load_chat_settings(id,stop_recursion=True)
        else:
            shutil.copyfile(chats_folder+ignore_file_prefix+language+ini_suffix,filename)
            return load_chat_settings(id,stop_recursion=True)
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
            chats[id][q_type][q_id]=c["QUESTIONS"][m]#questions and answers are loaded into two separate sections with same index
        if q_type=="A":
            answers=c["QUESTIONS"][m].replace("ё","е").replace("Ё","Е").lower()
            answers=answers.split("|")
            chats[id][q_type][q_id]=answers
            
            q_id+=1#auto-numbering during load: you can number questions as you like, just watch out! 
            #numbers must be equal for question and answer, and now same numbers for different questions are allowed
    chats[id]["ignore"]=bool(int(c["COMMON"]["ignore"]))
    chats[id]["mute_timer"]=int(c["COMMON"]["mute_timer"])
    chats[id]["reactions_max"]=int(c["COMMON"]["reactions_max"])
    chats[id]["reactions_warning"]=int(c["COMMON"]["reactions_warning"])
    chats[id]["reactions_final_warning"]=int(c["COMMON"]["reactions_final_warning"])
    return None

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