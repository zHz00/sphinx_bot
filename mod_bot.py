import requests
import json
import time
import datetime
import random

import settings as s

__token=""
req_prefix="https://api.telegram.org/bot"

request_idx=0

def init(token):
    global __token
    print("Token len: "+str(len(token)))
    __token=token

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
    try:
        res=requests.post(url,data=data)
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
    data={"limit":1,"allowed_updates":'["message","message_reaction","chat_member","callback_query"]'}
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
    s_res=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
    j=fix_JSON(s_res)
    if "result" in j:
        if len(j["result"])>0:
            tg_result=j["result"][0]
            update_id=tg_result["update_id"]
            update_id=int(update_id)
        else:
            tg_result=dict()
            update_id=-1
    else:
        error_pause=s.poll_error_pause
        if "parameters" in j:
            if "retry_after" in j["paramters"]:
                error_pause=j["parameters"]["retry_after"]
                print(f"returned sleep:{error_pause}")
        print(f"Request error! (no result) Wait {error_pause} (idx:{request_idx})")
        if "error_code" in j:
            print(f"There is error_code:{j['error_code']}")
        else:
            print("No error_code present. See:"+str(j))
        time.sleep(error_pause)
        tg_result=dict()
        update_id=-1
        return tg_result,update_id
    return tg_result,update_id

def get_chat(chat_id,tries=3):
    data = {"chat_id": chat_id}
    url=req_prefix+__token+"/getChat"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data)
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
        res=requests.post(url,data=data)
    except:
        print("error with request (get_chat_member). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return get_chat(chat_id,tries-1)
        else:
            return []
    return res

def restrict(chat_id,uid,date,tries=3):
    data = {"chat_id": chat_id,"user_id":uid,"permissions":'{"can_send_messages":false}',"until_date":date}
    url=req_prefix+__token+"/restrictChatMember"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data)
    except:
        print("error with request (restrict). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return restrict(chat_id,uid,date,tries-1)
        else:
            return []
    return res

def unrestrict(chat_id,uid,tries=3):
    data = {"chat_id": chat_id,"user_id":uid,"permissions":'{"can_send_messages":true,"can_send_audios":true,"can_send_documents":true,"can_send_photos":true,"can_send_videos":true,"can_send_video_notes":true,"can_send_voice_notes":true,"can_send_polls":true,"can_send_other_messages":true,"can_add_web_page_previews":true,"can_change_info":true,"can_invite_users":true,"can_pin_messages":true,"can_manage_topics":true}',"until_date":date}
    url=req_prefix+__token+"/restrictChatMember"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data)
    except:
        print("error with request (restrict). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return restrict(chat_id,uid,date,tries-1)
        else:
            return []
    return res

def delete_message(chat_id,message_id,tries=3):
    data = {"chat_id": chat_id,"message_id":message_id}
    url=req_prefix+__token+"/deleteMessage"
    #print("url:"+url)
    #print("text:"+text)
    try:
        res=requests.post(url,data=data)
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
        res=requests.post(url,data=data)
    except:
        print("error with request (answerCallbackQuery). pause")
        time.sleep(s.poll_error_pause)
        if tries>0:
            return answer_callback(chat_id,callback_query_id,tries-1)
        else:
            return []
    return res


if __name__=="__main__":
    to_delete_chat_id=[]
    to_delete_id=[]
    to_delete_date=[]
    active_q=dict()
    active_q_group=dict()
    q_id=0
    s.load()
    init(s.token)
    id=-1
    sent_counter=3
    while(1):
        for i in range(len(to_delete_id)):
            m_chat_id=to_delete_chat_id[i]
            m_id=to_delete_id[i]
            m_date=to_delete_date[i]
            dif=int(datetime.datetime.now().timestamp())-m_date
            if dif>s.auto_delete_time:#1 час
                res=delete_message(m_chat_id,m_id)
                print(res.content.decode("unicode-escape",errors='replace'))
                s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                j=fix_JSON(s_tmp)
                if "ok" in j:
                    if j["ok"]==True:
                        print(f"message deleted. id={m_id},date={m_date}")
                        to_delete_chat_id.pop(i)
                        to_delete_id.pop(i)
                        to_delete_date.pop(i)
                        #мы не хотим проблем с изменённым в цикле списке, поэтому после изменения сразу прекращаем. следующее сообщение, если оно есть, удалим в следующий раз
                        break
                    else:
                        print(f"message NOT deleted, [ok]==false. id={m_id},date={m_date}")
                else:
                    print(f"message NOT deleted, [ok] section absent. id={m_id},date={m_date}")
        (res,id_new)=get_updates(id+1)
        if id_new!=-1:
            id=id_new
        #if res.contents!=""
        if len(res)>0:
            date=1
            chat_id=0
            if "message" in res:
                date=res["message"]["date"]
                chat_id=res["message"]["chat"]["id"]
                if "text" in res["message"] and res["message"]["text"]=="test1147":
                    send_text(chat_id,"response784")
                    #send_text(chat_id,"\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u041c\u0438\u0449\u0435\u043d\u043a\u043e")
            if "message_reaction" in res:
                date=res["message_reaction"]["date"]
                chat_id=res["message_reaction"]["chat"]["id"]
            if "chat_member" in res:
                date=res["chat_member"]["date"]
                chat_id=res["chat_member"]["chat"]["id"]
            if "callback_query" in res:
                date=0
                chat_id=res["callback_query"]["from"]["id"]

            date_s=datetime.datetime.fromtimestamp(date).strftime("%B %d %Y, %H:%M:%S")#ftime.strftime("%B %d %Y", str(date))
            print(f"update_id={id}, {date_s}")
            t=open("messages_log.txt","a",encoding="utf-8",errors="replace")
            txt=json.dumps(res,ensure_ascii=False)
            json.dump(res,t,ensure_ascii=False)
            #t.write(txt)
            t.write("\n")
            t.close()
            #res=test_res

            if "message" in res and res["message"]["chat"]["type"]=="private":
                if "text" not in res["message"]:
                    continue
                if chat_id in active_q:#мы задали вопрос
                    group_chat_id=active_q_group[chat_id]
                    q_id=active_q[chat_id]
                    active_q.pop(chat_id)
                    active_q_group.pop(chat_id)
                    answer=res["message"]["text"].replace("ё","е").replace("Ё","Е").lower()
                    if answer in s.chats[group_chat_id]["A"][q_id]:
                        send_text(chat_id,s.messages["unmute_success"])
                        unrestrict(group_chat_id,chat_id)
                    else:
                        keyboard='{"inline_keyboard":[[{"text":"'+s.messages["again"]+'","callback_data":"'+str(group_chat_id)+'|another"}]]}'
                        send_text(chat_id,s.messages["unmute_fail"],keyboard)
                    continue
                #тут будет вся обработка лички (кроме коллбека)
                if res["message"]["text"]=="/start":
                    button1=s.messages["check_button"]
                    button2=s.messages["unmute_button"]
                    reply='{"keyboard":[[{"text":"'+button1+'"},{"text":"'+button2+'"}]],"resize_keyboard":true}'
                    send_text(chat_id,s.messages["greeting"].replace("\\n","\n"),reply=reply)
                    continue
                if res["message"]["text"]==s.messages["check_button"]:
                    text=s.messages["check"]+"\n"
                    n=1
                    for group_chat_id in s.chats.keys():
                        res2=get_chat(group_chat_id)
                        s_tmp=res2.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                        j=fix_JSON(s_tmp)
                        print(s_tmp.encode("utf-8",errors="replace").decode())
                        if "result" in j and "title" in j["result"]:
                            title=j["result"]["title"]+f" ({group_chat_id})"
                        else:
                            title=f"<NO TITLE> ({group_chat_id})"
                        res=get_chat_member(group_chat_id,chat_id)
                        print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
                        s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                        j=fix_JSON(s_tmp)
                        if "result" in j and "status" in j["result"]:
                            text+=f"{n}. "+title+"\n"
                            text+=j["result"]["status"]+"\n"
                            if j["result"]["status"]=="restricted":
                                if s.chats[group_chat_id]["mute_timer"]==0:
                                    text+=s.messages["mode_restricted_forever"]
                                else:
                                    text+=s.messages["mode_restricted"].replace("#D",str(s.chats[group_chat_id]["mute_timer"]/86400.0))
                            else:
                                text+=s.messages["mode_allowed"]
                        text+="\n\n"
                    send_text(chat_id,text)
                    continue
                if res["message"]["text"]==s.messages["unmute_button"]:
                    text=s.messages["unmute"]+"\n"
                    buttons='{"inline_keyboard":[['
                    n=1
                    for group_chat_id in s.chats.keys():
                        res=get_chat(group_chat_id)
                        print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
                        s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                        j=fix_JSON(s_tmp)
                        if "result" in j and "title" in j["result"]:
                            title=j["result"]["title"]+f" ({group_chat_id})"
                        else:
                            title=f"<NO TITLE> ({group_chat_id})"
                        res=get_chat_member(group_chat_id,chat_id)
                        print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
                        s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                        j=fix_JSON(s_tmp)
                        if "result" in j and "status" in j["result"]:
                            buttons+='{"text":"'+title+'","callback_data":"'+str(group_chat_id)+'"},'
                    if buttons[-1]==",":
                        buttons=buttons[:-1]
                    buttons+="]]}"
                    send_text(chat_id,text,reply=buttons)
                    continue
                if True:#все остальные сообщения
                    button1=s.messages["check_button"]
                    button2=s.messages["unmute_button"]
                    reply='{"keyboard":[[{"text":"'+button1+'"},{"text":"'+button2+'"}]],"resize_keyboard":true}'
                    send_text(chat_id,s.messages["unknown"].replace("\\n","\n"),reply=reply)
                    continue

                
                continue#дальнейшая обработка не имеет смысла

            if "callback_query" in res:
                answer_callback(chat_id,res["callback_query"]["id"])
                ans_data=res["callback_query"]["data"].split("|")
                group_chat_id=int(ans_data[0])
                if group_chat_id not in s.chats:
                    send_text(chat_id,"Chat NOT found")
                    continue
                q_id=random.randint(0,len(s.chats[group_chat_id]["Q"])-1)+1
                if q_id not in s.chats[group_chat_id]["Q"]:
                    print(f"key error! {q_id} question not found! check ini file!")
                    continue
                text=s.messages["unmute_question"]+"\n\n"
                if len(ans_data)>1 and ans_data[1]=="another":
                    text=s.messages["unmute_question_short"]+"\n\n"
                text+=s.chats[group_chat_id]["Q"][q_id]
                active_q[chat_id]=q_id
                active_q_group[chat_id]=group_chat_id
                send_text(chat_id,text)
                continue

            #остались группы и супергруппы (а может и ещё что, т.к. по документации это непонятно)
            c_s=dict()
            s.load_chat_settings(chat_id)
            c_s=s.chats[chat_id]
            if c_s["ignore"]==True:
                print(f"ignoring message from chat {chat_id}")
                time.sleep(s.poll_pause)
                continue#чат не входит в число обслуживаемых. личка не считается

            if "chat_member" in res:
                cm=res["chat_member"]
                user=cm["new_chat_member"]["user"]
                status=cm["new_chat_member"]["status"]
                is_member=False
                if status=="restricted":
                    is_member=cm["new_chat_member"]["is_member"]
                    print(f"is_member:{is_member}")
                if status=="member" or (status=="restricted" and is_member):#второе -- зашёл уже замьюченный пользователь. продлеваем мьют
                    print("new member!")
                    uid=user["id"]
                    uid_from=cm["from"]["id"]
                    name=user["first_name"]
                    if "last_name" in user:
                        name+=" "+user["last_name"]
                    if "username" in user:
                        name+=" ("+user["username"]+")"
                    #name=name.encode("unicode-escape").decode()
                    if uid==uid_from:#настоящий вход
                        message=c_s["MSG"]["hello"]
                        message=message.replace("#N",name).replace("\\n","\n")
                        print(message)
                        res=send_text(chat_id,message)
                        print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
                        s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                        j=fix_JSON(s_tmp)
                        if "result" in j:
                            result=j["result"]
                            to_delete_chat_id.append(chat_id)
                            print(f"added to queue (chat_id):{chat_id}")
                            if "message_id" in result:
                                to_delete_id.append(result["message_id"])
                                print(f"added to queue:{result['message_id']}")
                            else:
                                print("not found in result: message_id")
                            if "date" in result:
                                to_delete_date.append(result["date"])
                                print(f"added to queue (date):{result['date']}")
                            else:
                                print("not found in result: date")
                        else:
                            print("not found in result: result")
                        res=restrict(chat_id,int(uid),int(date)+c_s["mute_timer"])#7 дней
                        print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
                    else:#разбан
                        if status=="member":
                            message=c_s["MSG"]["unban"]
                            message=message.replace("#N",name).replace("\\n","\n")
                            print(message)
                            send_text(chat_id,message)
                        else:
                            pass#кого-то забанили или он получил новые ограничения. не будем выводить сообщений

        time.sleep(s.poll_pause)