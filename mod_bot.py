import time
import json
import datetime
import random
import os

import settings as s
from tg_lib import *


if __name__=="__main__":
    to_delete_chat_id=[]
    to_delete_id=[]
    to_delete_date=[]
    active_q=dict()
    active_q_group=dict()
    reactions_from_restricted=dict()
    q_id=0
    s.load()
    init(s.token)
    id=-1
    sent_counter=3
    queue_msg=[]
    queue_member=[]
    while(1):
        time.sleep(s.poll_pause)

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
        update_list=[]
        res=dict()
        (update_list,id_new)=(get_updates(id+1))
        if id_new!=-1:
            id=id_new
        #if res.contents!=""
        for u in update_list:
            if "chat_member" in u:
                queue_member.append(u)
            else:
                if len(u)>0:
                    queue_msg.append(u)
        if len(queue_member)>0:
            res=queue_member.pop(0)
        else:
            if len(queue_msg)>0:
                res=queue_msg.pop(0)
        if len(res)>0:
            date=1
            chat_id=0
            if "message" in res:
                date=res["message"]["date"]
                chat_id=res["message"]["chat"]["id"]
                if "text" in res["message"] and res["message"]["text"].startswith("test1147"):
                    send_text(chat_id,"response784:"+res["message"]["text"][8:])
                    #send_text(chat_id,"\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u041c\u0438\u0449\u0435\u043d\u043a\u043e")
                    continue
                if "text" in res["message"] and res["message"]["text"].startswith("test_result") and s.owner_id==chat_id:
                    if os.path.exists("output.txt"):
                        send_file(chat_id,"output","output.txt")
                    else:
                        send_text(chat_id,"File absent"+res["message"]["text"][8:])
                    #send_text(chat_id,"\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u041c\u0438\u0449\u0435\u043d\u043a\u043e")
                    continue
                if "text" in res["message"] and res["message"]["text"].startswith("test_command") and s.owner_id==chat_id:
                    normal_path=os.getcwd()
                    os.chdir(s.command_path)
                    command="start cmd /c "+s.command+" ^>\""+normal_path+"\\output.txt\""
                    os.system(command)
                    os.chdir(normal_path)
                    send_text(chat_id,"Command sent")
                    continue
            if "message_reaction" in res:
                date=res["message_reaction"]["date"]
                chat_id=res["message_reaction"]["chat"]["id"]
            if "chat_member" in res:
                date=res["chat_member"]["date"]
                chat_id=res["chat_member"]["chat"]["id"]
            if "callback_query" in res:
                date=res["callback_query"]["message"]["date"]
                chat_id=res["callback_query"]["from"]["id"]

            date_s=datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%dT%H:%M:%S")#ftime.strftime("%B %d %Y", str(date))
            print(f"update_id={id}, {date_s}")
            t=open("messages_log.txt","a",encoding="utf-8",errors="replace")
            txt=json.dumps(res,ensure_ascii=False)
            json.dump(res,t,ensure_ascii=False)
            #t.write(txt)
            t.write("\n")
            t.close()
            t=open("message_log_readable.txt","a",encoding="utf-8",errors="replace")
            try:
                if "message" in res:
                    m=res["message"]
                    type=m["chat"]["type"]
                    from_u=m["from"]["first_name"]
                    if "text" in m:
                        text=m["text"]
                    else:
                        text="Enter?"
                    t.write(f"{date_s}: [{chat_id} ({type})][{from_u}]:{text}\n")
                if "callback_query" in res:
                    c_id=res["callback_query"]["id"]
                    from_u=m["from"]["first_name"]
                    data=res["callback_query"]["data"]
                    t.write(f"{date_s}: [{chat_id}][{from_u}]:callback, id={c_id},data={data}\n")
                if "chat_member" in res:
                    cm=res["chat_member"]
                    user=cm["new_chat_member"]["user"]
                    from_u=user["first_name"]
                    status=cm["new_chat_member"]["status"]
                    t.write(f"{date_s}: [{chat_id}][{from_u}]:chat_mamber, new_status={status}\n")


            except:
                t.write(f"{date}: Exception\n")
            t.close()

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
                            if j["result"]["status"]=="left":
                                continue
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
                        n+=1
                    send_text(chat_id,text)
                    continue
                if res["message"]["text"]==s.messages["unmute_button"]:
                    text=s.messages["unmute"]+"\n"
                    buttons='{"inline_keyboard":['
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
                            if j["result"]["status"]=="left":
                                continue
                            buttons+='[{"text":"'+title+'","callback_data":"'+str(group_chat_id)+'"}],'
                    if buttons[-1]==",":
                        buttons=buttons[:-1]
                    buttons+="]}"
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
        
            if "message_reaction" in res:
                date=res["message_reaction"]["date"]
                chat_id=res["message_reaction"]["chat"]["id"]
                if "user" not in res["message_reaction"]:#anonymous reaction
                    continue
                user=res["message_reaction"]["user"]
                uid=user["id"]
                name=user["first_name"]
                if "last_name" in user:
                    name+=" "+user["last_name"]
                if "username" in user:
                    name+=" ("+user["username"]+")"
                res=get_chat_member(chat_id,uid)
                print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
                s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                j=fix_JSON(s_tmp)
                if "result" in j and "status" in j["result"]:
                    if j["result"]["status"]=="restricted":#restricted user makes reactions!
                        index=str(chat_id)+"|"+str(uid)
                        if index not in reactions_from_restricted:
                            reactions_from_restricted[index]=1
                        else:
                            reactions_from_restricted[index]+=1
                        n_reactions=reactions_from_restricted[index]
                        print(f"reaction made from restricted user: {uid}, N={n_reactions}")
                        if int(s.chats[chat_id]["reactions_max"])==0:
                            continue
                        if n_reactions>int(s.chats[chat_id]["reactions_max"]):
                            ban(chat_id,uid,0)
                            send_text(chat_id,s.chats[chat_id]["MSG"]["ban"].replace("#N",name).replace("\\n","\n"))
                            reactions_from_restricted[index]=0
                            continue
                        if n_reactions==int(s.chats[chat_id]["reactions_final_warning"]):
                            send_text(chat_id,s.chats[chat_id]["MSG"]["reactions_final_warning"].replace("#N",name).replace("\\n","\n"))
                            continue
                        if n_reactions==int(s.chats[chat_id]["reactions_warning"]):
                            send_text(chat_id,s.chats[chat_id]["MSG"]["reactions_warning"].replace("#N",name).replace("\\n","\n"))
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
