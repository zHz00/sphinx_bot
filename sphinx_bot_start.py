import time
import datetime
import random
import os

import settings as s
import make_log as l
from tg_lib import *

def reset_queues():
    global to_delete_chat_id,to_delete_id,to_delete_date
    global failed_tries_chat_id,failed_tries_date
    global active_q,active_q_group
    global reactions_from_restricted

    to_delete_chat_id=[]
    to_delete_id=[]
    to_delete_date=[]

    failed_tries_chat_id=[]
    failed_tries_date=[]
    active_q=dict()
    active_q_group=dict()

    reactions_from_restricted=dict()

reset_queues()#to create global variables

def process_timeout_wrong_answer():
    global failed_tries_chat_id,failed_tries_date
    for i in range(len(failed_tries_chat_id)):
        m_date=failed_tries_date[i]
        dif=int(datetime.datetime.now().timestamp())-m_date
        if dif>s.answer_retry_time:
            failed_tries_chat_id.pop(i)
            failed_tries_date.pop(i)
    return

def process_timeout_greeting():
    global to_delete_chat_id,to_delete_id,to_delete_date
    for i in range(len(to_delete_id)):
        m_chat_id=to_delete_chat_id[i]
        m_id=to_delete_id[i]
        m_date=to_delete_date[i]
        dif=int(datetime.datetime.now().timestamp())-m_date
        if dif>s.auto_delete_time:#1 hour by default
            res=delete_message(m_chat_id,m_id)
            if hasattr(res,"content")==False:
                print(f"message NOT deleted, [content] section absent. id={m_id},date={m_date}")
            else:
                print(res.content.decode("unicode-escape",errors='replace'))
                s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
                j=fix_JSON(s_tmp)
                if "ok" in j:
                    if j["ok"]==True:
                        print(f"message deleted. id={m_id},date={m_date}")
                        to_delete_chat_id.pop(i)
                        to_delete_id.pop(i)
                        to_delete_date.pop(i)
                        #we are modifying a list in a loop, controlled by that list. this is very bad thing, and we can get into trouble if we continue.
                        #so we just end a loop. if there are any other messages that must be deleted, this is fine. we'll delete them next time.
                        break
                    else:
                        print(f"message NOT deleted, [ok]==false. id={m_id},date={m_date}")
                        to_delete_chat_id.pop(i)
                        to_delete_id.pop(i)
                        to_delete_date.pop(i)
                        #if ok==false then no such message exists. removing from list. additionally see previous comment about break
                        break
                else:
                    print(f"message NOT deleted, [ok] section absent. id={m_id},date={m_date}")
    return


def make_question(chat_id,res):
    global active_q,active_q_group
    answer_callback(chat_id,res["callback_query"]["id"])
    ans_data=res["callback_query"]["data"].split("|")
    group_chat_id=int(ans_data[0])
    if chat_id in failed_tries_chat_id:
        send_text(chat_id,s.messages["early"].replace("#T",str(s.answer_retry_time)))
        return
    if group_chat_id not in s.chats:
        send_text(chat_id,"Chat NOT found")
        return
    q_id=random.randint(0,len(s.chats[group_chat_id]["Q"])-1)+1
    if q_id not in s.chats[group_chat_id]["Q"]:
        print(f"key error! {q_id} question not found! check ini file!")
        return
    text=s.messages["unmute_question"]+"\n\n"
    if len(ans_data)>1 and ans_data[1]=="another":
        text=s.messages["unmute_question_short"]+"\n\n"
    text+=s.chats[group_chat_id]["Q"][q_id]
    active_q[chat_id]=q_id
    active_q_group[chat_id]=group_chat_id
    send_text(chat_id,text)
    return

def check_answer(chat_id,res):
    global active_q, active_q_group
    global failed_tries_chat_id,failed_tries_date
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
        send_text(chat_id,s.messages["unmute_fail"].replace("#T",str(s.answer_retry_time)),keyboard)
        failed_tries_chat_id.append(chat_id)
        if "date" in res:
            failed_tries_date.append(res["date"])
        else:
            failed_tries_date.append(int(datetime.datetime.now().timestamp()))
            print("Not found date field in user answer")
    return

def show_chat_list_numbered(chat_id):
    text=s.messages["check"]+"\n"
    n=1
    for group_chat_id in s.chats.keys():
        res2=get_chat(group_chat_id)
        if hasattr(res2,"content")==False:
            print("error while getting chat!")
            continue
        s_tmp=res2.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
        j=fix_JSON(s_tmp)
        print(s_tmp.encode("utf-8",errors="replace").decode())
        if "result" in j and "title" in j["result"]:
            title=j["result"]["title"]+f" (id: {group_chat_id})"
        else:
            title=f"<NO TITLE> (id: {group_chat_id})"
        res=get_chat_member(group_chat_id,chat_id)
        if hasattr(res,"content")==False:
            print("error while getting chat member!")
            continue
        print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
        s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
        j=fix_JSON(s_tmp)
        if "result" in j and "status" in j["result"]:
            if j["result"]["status"]=="left":
                continue
            text+=f"{n}. "+title+"\n"
            #text+=j["result"]["status"]+"\n"
            if j["result"]["status"]=="restricted":
                if s.chats[group_chat_id]["mute_timer"]==0:
                    text+=s.messages["mode_restricted_forever"]
                else:
                    text+=s.messages["mode_restricted"].replace("#D",str(s.chats[group_chat_id]["mute_timer"]/86400.0))
            else:
                text+=s.messages["mode_allowed"]
        text+="\n\n"
        n+=1
    reply=make_starting_keyboard()
    send_text(chat_id,text,reply=reply)
    return

def show_chat_list_buttons(chat_id):
    text=s.messages["unmute"]+"\n"
    buttons='{"inline_keyboard":['
    n=1
    for group_chat_id in s.chats.keys():
        res=get_chat(group_chat_id)
        if hasattr(res,"content")==False:
            print("error while getting chat!")
            continue
        print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
        s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
        j=fix_JSON(s_tmp)
        if "result" in j and "title" in j["result"]:
            title=j["result"]["title"]+f" ({group_chat_id})"
        else:
            title=f"<NO TITLE> ({group_chat_id})"
        res=get_chat_member(group_chat_id,chat_id)
        if hasattr(res,"content")==False:
            print("error while getting chat member!")
            continue
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
    return

def make_starting_keyboard():
    button1=s.messages["check_button"]
    button2=s.messages["unmute_button"]
    return '{"keyboard":[[{"text":"'+button1+'"},{"text":"'+button2+'"}]],"resize_keyboard":true,"one_time_keyboard":true}'

def greeting(chat_id):
    reply=make_starting_keyboard()
    send_text(chat_id,s.messages["greeting"].replace("\\n","\n"),reply=reply)

def notify_unknown_command(chat_id):
    reply=make_starting_keyboard()
    send_text(chat_id,s.messages["unknown"].replace("\\n","\n"),reply=reply)


#page=0: last page
#page=1: previous page
#page number increasing towards beginning of file
def send_log_readable(chat_id,page,page_size=65536):
    size=os.path.getsize(s.log_readable)
    pos=page_size*(page+2)
    if pos>size:
        pos=size
    t=open(s.log_readable,"rb")
    to_read=page_size*2
    if to_read>size:
        to_read=size
    t.seek(-pos,os.SEEK_END)
    data=t.read(to_read)
    t.close()
    if size>page_size:
        search_end=len(data)-page_size
    else:
        search_end=page_size
    index=data.rfind(b'\n',0,search_end)
    if index==-1:
        index=0
    out_data="DUMMY"
    while data[index]>127:#we somehow find ourself in the middle of the character
        index+=1
        if index>to_read:
            #for unknown reason, all bytes are invalid
            out_data="INVALID UNICODE"
    try:
        out_data=data[index:].decode("utf-8",errors='ignore')
    except Exception as e:
        out_data="INVALID UNICODE: "+str(e)
    out_data=out_data.replace("\r\n","\n")#for windows
    date=datetime.datetime.now().timestamp()
    date_s=datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%dT%H-%M-%S")
    filename=f"logs-{date_s}-p{str(page)}.txt"
    t=open(filename,"w",encoding="utf-8")
    t.write(out_data)
    t.close()
    send_file(chat_id,f"page {page} from end",filename)
    os.remove(filename)
    return


    #while ch!="\n":
        #ch=t.read(1)

def react_to_public_commands(chat_id,res):
    if "text" in res["message"] and res["message"]["text"].startswith("test1147"):
        send_text(chat_id,"response785:"+res["message"]["text"][8:])
        #send_text(chat_id,"\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u041c\u0438\u0449\u0435\u043d\u043a\u043e")
        send_text(chat_id,"testing markdown (v2), this is link exapmle: #[link#]#(https://example.com/#)")
        return True
    return False

def react_to_private_commands(chat_id,res):
    if "text" in res["message"] and res["message"]["text"].startswith("test1147"):
        send_text(chat_id,"response784:"+res["message"]["text"][8:])
        #send_text(chat_id,"\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u041c\u0438\u0449\u0435\u043d\u043a\u043e")
        #send_text(chat_id,"testing markdown (v2), this is link exapmle: #[link1#]#(https://example.com/#)")
        send_text(chat_id,"testing markdown (v2), this is link exapmle: #[link1#]#(https://example.com/#), #[link2#]#(tg://user?id=8365073499#)")
        #this user id deleted long time ago. so we check if he will get a clickable link (not, he'll not)
        return True
    if "text" in res["message"] and res["message"]["text"].startswith("profile"):
        param_list=res["message"]["text"].split(" ")
        param=0 if len(param_list)!=2 else param_list[1]
        send_text(chat_id,f"Profile link: #[link#]#(tg://user?id={param}#)")
        return True
    if "text" in res["message"] and res["message"]["text"].startswith("test_result") and s.owner_id==chat_id:
        if os.path.exists("output.txt"):
            send_file(chat_id,"output","output.txt")
        else:
            send_text(chat_id,"File absent"+res["message"]["text"][8:])
        #send_text(chat_id,"\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u041c\u0438\u0449\u0435\u043d\u043a\u043e")
        return True
    if "text" in res["message"] and res["message"]["text"].startswith("test_command") and s.owner_id==chat_id:
        normal_path=os.getcwd()
        os.chdir(s.command_path)
        command="start cmd /c "+s.command+" ^>\""+normal_path+"\\output.txt\""
        os.system(command)
        os.chdir(normal_path)
        send_text(chat_id,"Command sent")
        return True
    if "text" in res["message"] and res["message"]["text"].startswith("logs") and s.owner_id==chat_id:
        params=res["message"]["text"].split(" ")
        page=0
        if len(params)>1:
            try:
                page=int(params[1])
            except:
                pass
        send_log_readable(chat_id,page)
        return True
    return False

def check_reactions_from_restricted(chat_id,res,c_s):
    global reactions_from_restricted
    if "user" not in res["message_reaction"]:#anonymous reaction
        return
    user=res["message_reaction"]["user"]
    reaction_count=len(res["message_reaction"]["new_reaction"])
    uid=user["id"]
    name=user["first_name"]
    if "last_name" in user:
        name+=" "+user["last_name"]
    if "username" in user:
        name+=" ("+user["username"]+")"
    res=get_chat_member(chat_id,uid)
    if hasattr(res,"content")==False:
        print("error while getting chat member!")
        return
    print(res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
    s_tmp=res.content.replace(b'\\"',b"*").decode("unicode-escape",errors='replace')
    j=fix_JSON(s_tmp)
    if "result" in j and "status" in j["result"]:
        if j["result"]["status"]=="restricted":#restricted user makes reactions!
            if reaction_count==0:
                return#reaction removed, don't increase counter
            index=str(chat_id)+"|"+str(uid)
            profile=c_s["MSG"]["profile"]
            id_link=f"#[{profile}#]#(tg://user?id="+str(uid)+"#)"
            if index not in reactions_from_restricted:
                reactions_from_restricted[index]=1
            else:
                reactions_from_restricted[index]+=1
            n_reactions=reactions_from_restricted[index]
            print(f"reaction made from restricted user: {uid}, N={n_reactions}")
            if int(s.chats[chat_id]["reactions_max"])==0:
                return
            if n_reactions>int(c_s["reactions_max"]):
                ban(chat_id,uid,0)
                send_text(chat_id,c_s["MSG"]["ban"].replace("#N",name).replace("#I",id_link).replace("\\n","\n"))
                reactions_from_restricted[index]=0
                return
            if n_reactions==int(c_s["reactions_final_warning"]):
                send_text(chat_id,c_s["MSG"]["reactions_final_warning"].replace("#N",name).replace("#I",id_link).replace("\\n","\n"))
                return
            if n_reactions==int(c_s["reactions_warning"]):
                send_text(chat_id,c_s["MSG"]["reactions_warning"].replace("#N",name).replace("#I",id_link).replace("\\n","\n"))
                return
    return

def check_new_member(date,chat_id,res,c_s):
    global to_delete_chat_id,to_delete_id,to_delete_date
    cm=res["chat_member"]
    user=cm["new_chat_member"]["user"]
    status=cm["new_chat_member"]["status"]
    is_member=False
    if status=="restricted":
        is_member=cm["new_chat_member"]["is_member"]
        print(f"is_member:{is_member}")
    if status=="member" or (status=="restricted" and is_member):#"is_member" means that new member already muted during previous join, and the mute is not expired
        #in this case, we set new mute timer effectively increasing mute time
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
            profile=c_s["MSG"]["profile"]
            id_link=f"#[{profile}#]#(tg://user?id="+str(uid)+"#)"
            message=message.replace("#N",name).replace("#I",id_link).replace("\\n","\n")
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
            actual_mute=True
            if (status=="restricted" and is_member):#new member is already muted, we must check current timer
                limit=int(cm["new_chat_member"]["until_date"])
                print(f"limit: {limit}, date: {date}, timer:{c_s['mute_timer']}")
                if limit>int(date)+c_s["mute_timer"]:
                    actual_mute=False
            if actual_mute:
                res=restrict(chat_id,int(uid),int(date)+c_s["mute_timer"])#7 дней
                if hasattr(res,"content")==True:
                    print("restricted: "+res.content.decode("unicode-escape",errors='replace').encode("utf-8",errors="replace").decode())
                else:
                    print("error while restricting!")
            else:
                print("Current mute limit is greater than new member mute limit, so limit will not be decreased. Skipping...")
        else:#remove restricion. this is called "unban" which is incorrect. user never was banned, only muted.
            if status=="member":
                status_old=status=cm["old_chat_member"]["status"]
                message=c_s["MSG"]["unban"]
                message=message.replace("#N",name).replace("\\n","\n")
                if status_old=="restricted" and len(name)>0:#can be also "administrator" or "owner". this must be ignored
                    print(message)
                    send_text(chat_id,message)
                else:
                    send_text(s.owner_id,"strange unban: "+message+"; id:"+str(cm["old_chat_member"]["user"]["id"]))
            else:
                pass#this section triggers when someone get banned by real admins or someone got restricted. so we don't need to show any messegas
    return

def update_handler(res):
    date=1
    chat_id=0
    if "message" in res:
        date=res["message"]["date"]
        chat_id=res["message"]["chat"]["id"]
    if "message_reaction" in res:
        date=res["message_reaction"]["date"]
        chat_id=res["message_reaction"]["chat"]["id"]
        print("old:"+str(res["message_reaction"]["old_reaction"]))
        print("new:"+str(res["message_reaction"]["new_reaction"]))
        if len(res["message_reaction"]["old_reaction"])==0:
            print("reaction set")
        if len(res["message_reaction"]["new_reaction"])==0:
            print("reaction removed")

    if "chat_member" in res:
        date=res["chat_member"]["date"]
        chat_id=res["chat_member"]["chat"]["id"]
    if "callback_query" in res:
        date=res["callback_query"]["message"]["date"]
        chat_id=res["callback_query"]["from"]["id"]

    date_s=datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%dT%H:%M:%S")#ftime.strftime("%B %d %Y", str(date))
    print(f"update_id={id}, {date_s}")
    l.make_log_record_raw(date_s,res)
    l.make_log_record_readable(date_s,chat_id,res)

    if "message" in res and res["message"]["chat"]["type"]!="private":#public commands
        if "text" not in res["message"]:
            return
        reacted=react_to_public_commands(chat_id,res)
        if reacted:
            return

    if "message" in res and res["message"]["chat"]["type"]=="private":
        if "text" not in res["message"]:
            return
        if chat_id in active_q:#мы задали вопрос
            check_answer(chat_id,res)
            return
        reacted=react_to_private_commands(chat_id,res)
        if reacted:
            return
        #here is processing of private commands except callback buttons
        if res["message"]["text"]=="/start":
            greeting(chat_id)
            return
        if res["message"]["text"]==s.messages["check_button"]:
            show_chat_list_numbered(chat_id)
            return
        if res["message"]["text"]==s.messages["unmute_button"]:
            show_chat_list_buttons(chat_id)
            return
        if True:#все остальные сообщения
            notify_unknown_command(chat_id)
            return

        
        return#nothing left to check

    if "callback_query" in res:
        make_question(chat_id,res)
        return

    #reacting to groups and supergroups and maybe something other
    c_s=dict()
    if chat_id not in s.chats:
        s.load_chat_settings(chat_id)
        #if this is first message in new chat, then settings file don't exist and we must load defaults
    c_s=s.chats[chat_id]
    if c_s["ignore"]==True:
        print(f"ignoring message from chat {chat_id}")
        return#public chat not in service, so ignore all messages
        #by default, this bot accepts all new chats and begin operating with default settings. but this can be a problem, if someone begins
        #to add your bot to unknown chats. if you set new_chats_allowed = 0 in settings_global.ini, then all new chats will get default settings
        #with "ignore" variable set to 1. you can manually enable chats later.

    if "message_reaction" in res:
        date=res["message_reaction"]["date"]
        chat_id=res["message_reaction"]["chat"]["id"]
        check_reactions_from_restricted(chat_id,res,c_s)

    if "chat_member" in res:
        check_new_member(date,chat_id,res,c_s)


if __name__=="__main__":
    s.load()
    init(s.token)
    reset_queues()
    id=-1
    sent_counter=3
    queue_msg=[]
    queue_member=[]
    while(1):
        print("begin poll pause...",end="")
        time.sleep(s.poll_pause)
        print("done", end="")
        process_timeout_wrong_answer()
        process_timeout_greeting()
        update_list=[]
        res=dict()
        timeout=5#default
        if len(queue_member)>0 or len(queue_msg)>0:
            timeout=s.poll_pause#if we have non-empty queue, don't wait full timeout. we have to manage the queue
        else:
            timeout=s.poll_wait_timeout
        (update_list,id_new)=(get_updates(timeout=timeout,id=(id+1)))
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
            update_handler(res)
        
        continue#end of main infinite loop
