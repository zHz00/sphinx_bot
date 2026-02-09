import requests
import json
import time
import settings as s


__token=""
req_prefix="https://api.telegram.org/bot"

request_idx=0

def init(token):
    global __token
    print("Token len: "+str(len(token)))
    __token=token

def send_file(chat_id,caption,file,tries=3):
    data = {"chat_id": chat_id, "caption": caption}
    try:
        with open(file, "rb") as data_file:
            res=requests.post(req_prefix+__token+"/sendDocument",data=data,files={"document":data_file},proxies=s.get_proxies())
    except:
        print("error with request (send_file). pause")
        time.sleep(10)
        if tries>0:
            return send_file(chat_id,caption,file,tries-1)
        else:
            return []

    return res

def send_text(chat_id,text,reply="",preview=True,tries=3):
    forbidden=[ '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for ch in forbidden:
        text=text.replace(ch,"\\"+ch)
    if preview==True:
        disable_preview_text="False"#потому что дизейбл
    else:
        disable_preview_text="True"
    data = {"chat_id": chat_id, "text": text,"parse_mode":"MarkdownV2","disable_web_page_preview":disable_preview_text}
    if len(reply)>0:
        data["reply_markup"]=reply
    url=req_prefix+__token+"/sendMessage"
    #print("url:"+url)
    #print("text:"+text)
    t=open("message_log_readable.txt","a",encoding="utf-8",errors="replace")
    t.write(f"Sending text:{chat_id},{text}\n")
    t.close()
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (send_text). pause")
        time.sleep(10)
        if tries>0:
            return send_text(chat_id,text,reply,preview,tries-1)
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
        try:
            print(json_message)
        except:
            print("(message with surrogates)")
        # Remove the offending character:
        json_message = list(json_message)
        json_message[idx_to_replace] = ' '
        new_message = ''.join(json_message)     
        return fix_JSON(json_message=new_message)
    return result

def get_updates(id=0):
    global request_idx
    request_idx+=1
    data={"limit":100,"allowed_updates":'["message","message_reaction","chat_member","callback_query"]'}
    if id!=0:
        data["offset"]=id
    url=req_prefix+__token+"/getUpdates"
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print(f"Request error! Wait 60 (idx:{request_idx})")
        time.sleep(60)
        tg_result=[dict()]
        update_id=-1
        return tg_result,update_id
    #s_res=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
    s_res=res.content
    j=fix_JSON(s_res)
    if "result" in j:
        if len(j["result"])>0:
            print(f'LEN={len(j["result"])}')
            tg_result=j["result"]
            update_id=tg_result[-1]["update_id"]
            update_id=int(update_id)
        else:
            tg_result=[dict()]
            update_id=-1
    else:
        error_pause=s.poll_error_pause
        if "parameters" in j:
            if "retry_after" in j["parameters"]:
                error_pause=j["parameters"]["retry_after"]
                print(f"returned sleep:{error_pause}")
        print(f"Request error! (no result) Wait {error_pause} (idx:{request_idx})")
        if "error_code" in j:
            print(f"There is error_code:{j['error_code']}")
        else:
            print("No error_code present. See:"+str(j))
        time.sleep(error_pause)
        tg_result=[dict()]
        update_id=-1
        return tg_result,update_id
    return tg_result,update_id

def get_chat(chat_id,tries=3):
    data = {"chat_id": chat_id}
    url=req_prefix+__token+"/getChat"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (get_chat). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return get_chat(chat_id,tries-1)
        else:
            return []
    return res

def get_chat_member(chat_id,uid,tries=3):
    data = {"chat_id": chat_id,"user_id":uid}
    url=req_prefix+__token+"/getChatMember"
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (get_chat_member). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return get_chat(chat_id,tries-1)
        else:
            return []
    return res

def ban(chat_id,uid,date,tries=3):
    data = {"chat_id": chat_id,"user_id":uid,"until_date":date}
    url=req_prefix+__token+"/banChatMember"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (restrict). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return ban(chat_id,uid,date,tries-1)
        else:
            return []
    return res


def restrict(chat_id,uid,date,tries=3):
    data = {"chat_id": chat_id,"user_id":uid,"permissions":'{"can_send_messages":false}',"until_date":date}
    url=req_prefix+__token+"/restrictChatMember"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (restrict). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return restrict(chat_id,uid,date,tries-1)
        else:
            return []
    return res

def unrestrict(chat_id,uid,tries=3):
    data = {"chat_id": chat_id,"user_id":uid,"permissions":'{"can_send_messages":true,"can_send_audios":true,"can_send_documents":true,"can_send_photos":true,"can_send_videos":true,"can_send_video_notes":true,"can_send_voice_notes":true,"can_send_polls":true,"can_send_other_messages":true,"can_add_web_page_previews":true,"can_change_info":true,"can_invite_users":true,"can_pin_messages":true,"can_manage_topics":true}',"until_date":0}
    url=req_prefix+__token+"/restrictChatMember"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (restrict). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return unrestrict(chat_id,uid,tries-1)
        else:
            return []
    return res

def delete_message(chat_id,message_id,tries=3):
    data = {"chat_id": chat_id,"message_id":message_id}
    url=req_prefix+__token+"/deleteMessage"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (deleteMessage). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return restrict(chat_id,message_id,tries-1)
        else:
            return []
    return res

def answer_callback(chat_id,callback_query_id,tries=3):
    data = {"chat_id": chat_id,"callback_query_id":callback_query_id,"text":"OK!"}
    url=req_prefix+__token+"/answerCallbackQuery"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data,proxies=s.get_proxies())
    except:
        print("error with request (answerCallbackQuery). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return answer_callback(chat_id,callback_query_id,tries-1)
        else:
            return []
    return res

