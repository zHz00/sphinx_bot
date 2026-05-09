import json
import settings as s

rare_types=["animation",
    "audio",
    "document",
    "photo",
    "sticker",
    "story",
    "video",
    "video_note",
    "voice",
    "checklist",
    "contact",
    "dice",
    "game",
    "poll",
    "venue",
    "location",
    "invoice",
    "successful_payment",
    "refunded_payment",
    "giveaway",
    "new_chat_members",
    "left_chat_member",
    "new_chat_title",
    "new_chat_photo"
    ]

def make_log_record_raw(date_s,res):
    t=open(s.log_raw,"a",encoding="utf-8",errors="replace")
    t.write(date_s+": ")
    txt=json.dumps(res,ensure_ascii=False)
    json.dump(res,t,ensure_ascii=False)
    #t.write(txt)
    t.write("\n")
    t.close()
    return

def make_log_record_readable_str(date_s,msg):
    t=open(s.log_readable,"a",encoding="utf-8",errors="replace")
    t.write(date_s+": "+msg)
    t.write("\n")
    t.close()
    return

def make_log_record_readable(date_s,chat_id,res):
    t=open(s.log_readable,"a",encoding="utf-8",errors="replace")
    try:
        if "message" in res:
            m=res["message"]
            type=m["chat"]["type"]
            from_u=m["from"]["first_name"]
            text=None
            if "text" in m:
                text=m["text"]
            for rt in rare_types:
                if rt in m:
                    text="["+rt+"]"
            if text is None:
                text="[Unknown message type]"
            t.write(f"{date_s}: [{chat_id} ({type})][{from_u}]:{text}\n")
        if "callback_query" in res:
            m=res["callback_query"]
            c_id=res["callback_query"]["id"]
            from_u=m["from"]["first_name"]
            data=res["callback_query"]["data"]
            t.write(f"{date_s}: [{chat_id}][{from_u}]:callback, id={c_id},data={data}\n")
        if "chat_member" in res:
            cm=res["chat_member"]
            user=cm["new_chat_member"]["user"]
            from_u=user["first_name"]
            status=cm["new_chat_member"]["status"]
            t.write(f"{date_s}: [{chat_id}][{from_u}]:chat_member, new_status={status}\n")
        if "message_reaction" in res:
            date=res["message_reaction"]["date"]
            chat_id=res["message_reaction"]["chat"]["id"]
            from_u="---"
            if "user"in res["message_reaction"]:
                user=res["message_reaction"]["user"]
                from_u=user["first_name"]
            else:
                from_u="Unkonwn user"
            t.write(f"{date_s}: [{chat_id}][{from_u}]:reaction\n")

    except Exception as e:
        t.write(f"{date_s}: Exception: {str(e)}\n")
    t.close()
    return
