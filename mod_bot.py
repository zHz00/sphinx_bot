import requests
import json
import time
import datetime

__token=""
__chat_id=""
req_prefix="https://api.telegram.org/bot"

request_idx=0

def init(token,chat_id):
    global __token,__chat_id
    print("Posting to "+chat_id+", token len: "+str(len(token)))
    __token=token
    __chat_id=chat_id

def send_text(text,preview=True,tries=3):
    if preview==True:
        disable_preview_text="False"#потому что дизейбл
    else:
        disable_preview_text="True"
    data = {"chat_id": __chat_id, "text": text,"parse_mode":"Markdown","disable_web_page_preview":disable_preview_text}
    url=req_prefix+__token+"/sendMessage"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data)
    except:
        print("error with request (send_text). pause")
        time.sleep(10)
        if tries>0:
            return send_text(text,preview,tries-1)
        else:
            return []
    return res

def fix_JSON(json_message=None):
    result = None
    try:        
        result = json.loads(json_message,strict=False)
    except Exception as e:      
        # Find the offending character index:
        idx_to_replace = int(str(e).split(' ')[-1].replace(')', ''))        
        print(str(e))
        print("\n=====\n")
        print(json_message)
        # Remove the offending character:
        json_message = list(json_message)
        json_message[idx_to_replace] = ' '
        new_message = ''.join(json_message)     
        return fix_JSON(json_message=new_message)
    return result

def get_updates(id=0):
    global request_idx
    request_idx+=1
    data={"limit":1,"allowed_updates":'["message","message_reaction","chat_member"]'}
    if id!=0:
        data["offset"]=id
    url=req_prefix+__token+"/getUpdates"
    try:
        res=requests.post(url,data=data)
    except:
        print(f"Request error! Wait 60 (idx:{request_idx})")
        time.sleep(60)
        tg_result=dict()
        update_id=-1
        return tg_result,update_id
    s=res.content.replace(b'\\"',b"*").decode("unicode-escape")
    j=fix_JSON(s)
    if "result" in j:
        if len(j["result"])>0:
            tg_result=j["result"][0]
            update_id=tg_result["update_id"]
            update_id=int(update_id)
        else:
            tg_result=dict()
            update_id=-1
    else:
        print(f"Request error! (no result) Wait 60 (idx:{request_idx})")
        if "error_code" in j:
            print(f"There is error_code:{j['error_code']}")
        else:
            print("No error_code present. See:"+str(j))
        time.sleep(60)
        tg_result=dict()
        update_id=-1
        return tg_result,update_id
    return tg_result,update_id

def get_chat(tries=3):
    data = {"chat_id": __chat_id}
    url=req_prefix+__token+"/getChat"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data)
    except:
        print("error with request (get_chat). pause")
        time.sleep(10)
        if tries>0:
            return get_chat(tries-1)
        else:
            return []
    return res

def restrict(uid,date,tries=3):
    data = {"chat_id": __chat_id,"user_id":uid,"permissions":'{"can_send_messages":false}',"until_date":date}
    url=req_prefix+__token+"/restrictChatMember"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data)
    except:
        print("error with request (restrict). pause")
        time.sleep(10)
        if tries>0:
            return restrict(uid,date,tries-1)
        else:
            return []
    return res


test_res={"update_id": 744449279,
 "chat_member":
     {
        "chat":
             {
                "id": -1001489654859, 
                "title": "Астрономический чат «Ultima Thule»", 
                "username": "astro_chat_ut", 
                "type": "supergroup"
            },
         "from":
             {
                "id": 1738303190, 
                "is_bot": False, 
                "first_name": "Надя", 
                "last_name": "Савельева", 
                "is_premium": True
            },
         "date": 1744958312, 
         "old_chat_member": 
            {
                "user": 
                    {
                        "id": 1738303190, 
                        "is_bot": False, 
                        "first_name": "Надя", 
                        "last_name": "Савельева", 
                        "is_premium": True
                        },
                 "status": "left"
            },
         "new_chat_member": 
            {
                "user": 
                    {
                        "id": 1738303190, 
                        "is_bot": False,
                         "first_name": "Надя", 
                         "last_name": "Савельева", 
                         "is_premium": True}, 
                "status": "member"
            },
         "via_chat_folder_invite_link": True
    }
}

if __name__=="__main__":
    settings=open("settings.txt")
    token=settings.readline().strip()
    chat_id=settings.readline().strip()
    init(token,chat_id)
    #res=send_text("test")
    res=get_chat()
    print(str(res)+"\n")
    print(res.content.decode("unicode-escape"))
    #res=restrict(310299961,1745314457+604800)#7 дней
    #print(res.content.decode("unicode-escape"))
    id=-1
    sent_counter=3
    while(1):
        (res,id_new)=get_updates(id+1)
        if id_new!=-1:
            id=id_new
        #if res.contents!=""
        if len(res)>0:
            date=1
            if "message" in res:
                date=res["message"]["date"]
            if "message_reaction" in res:
                date=res["message_reaction"]["date"]
            if "chat_member" in res:
                date=res["chat_member"]["date"]
            date_s=datetime.datetime.fromtimestamp(date).strftime("%B %d %Y, %H:%M:%S")#ftime.strftime("%B %d %Y", str(date))
            print(f"update_id={id}, {date_s}")
            t=open("messages_log.txt","a",encoding="utf-8",errors="replace")
            txt=json.dumps(res,ensure_ascii=False)
            json.dump(res,t,ensure_ascii=False)
            #t.write(txt)
            t.write("\n")
            t.close()
            #res=test_res
            if "chat_member" in res:
                cm=res["chat_member"]
                user=cm["new_chat_member"]["user"]
                status=cm["new_chat_member"]["status"]
                if status=="member":
                    print("new member!")
                    uid=user["id"]
                    uid_from=cm["from"]["id"]
                    name=user["first_name"]
                    if "last_name" in user:
                        name+=" "+user["last_name"]
                    if "username" in user:
                        name+=" \\("+user["username"]+"\\)"
                    if uid==uid_from:#настоящий вход
                        message=name+", здравствуйте!\n\nИз-за атаки ботов всем новым пользователям отключена отправка сообщений на одну неделю.\n\nДля досрочного снятия блокировки пишите администраторам чата."
                        print(message)
                        res=send_text(message)
                        print(res.content.decode("unicode-escape"))
                        res=restrict(int(uid),int(date)+604800)#7 дней
                        print(res.content.decode("unicode-escape"))
                    else:#разбан
                        message="Пользователь "+name+" разбанен вручную."
                        print(message)
                        send_text(message)

        time.sleep(15)