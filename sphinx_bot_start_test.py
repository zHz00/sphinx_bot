import pytest
import requests_mock
import requests
import json
from urllib.parse import urlencode,parse_qs

import tg_lib
import settings as s
import sphinx_bot_start

def test1():
    assert(True)

update1={
            "result":
                [{
                    "update_id": 744471325,
                    "message":
                        {
                            "message_id": 35024,
                            "from":
                                {
                                    "id": 812327862,
                                    "is_bot": False,
                                    "first_name": "Виктор",
                                    "last_name": "Николаев",
                                    "username": "PosledovatelMidii"
                                },
                            "chat":
                                {
                                    "id": -1001144274214, 
                                    "title": "Caves of Qud chat", 
                                    "username": "Cavesofcudchat", 
                                    "type": "supergroup"
                                },
                            "date": 1774791370,
                            "message_thread_id": 35021,
                            "reply_to_message":
                                {
                                    "message_id": 35021,
                                    "from":
                                        {
                                            "id": 1828077664, 
                                            "is_bot": False,
                                            "first_name": "Mike",
                                            "username": "Cathedralheather"
                                        },
                                    "chat":
                                        {
                                            "id": -1001144274214,
                                            "title": "Caves of Qud chat",
                                            "username": "Cavesofcudchat",
                                            "type": "supergroup"
                                        },
                                    "date": 1774791307,
                                    "text": "I play ark survival evolved nowadays"
                                },
                            "text": "I've heard only trash being talked about this game, but the biggest trashtalkers are guys with 5000+ hours"
                        }
                }]
        }

def test2():
    with requests_mock.Mocker() as m:
        m.post('http://test.com', json=update1)
        res=tg_lib.temp_func()
        res_json=json.loads(res.text)
        assert res_json==update1

def test_get_updates():
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=update1)
        tg_lib.init(test_token)
        result=tg_lib.get_updates()
        assert result is not None

# #01: user enters chat
def test_new():
    tmsgs=json.load(open("test_data/01_user_new_msg.json","r",encoding="utf-8"))
    treacts=json.load(open("test_data/01_user_new_react.json","r",encoding="utf-8"))
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        request=dict()
        request['result']=[tmsgs[0]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request)

        request=tmsgs[1]#answer to posting
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request)

        request=tmsgs[2]#answer to posting
        url=tg_lib.req_prefix+test_token+"/restrictChatMember"
        m.post(url=url,json=request)

        s.chats_folder="test_chats/"
        s.settings_folder="test_settings/"
        s.load()
        tg_lib.init(test_token)
        
        id=-1
        update_list,id=tg_lib.get_updates()
        assert len(update_list)==1
        assert id==tmsgs[0]["update_id"]
        res=update_list[0]
        chat_id=res["chat_member"]["chat"]["id"]
        assert chat_id==tmsgs[0]["chat_member"]["chat"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==3

        #restrict message
        answer=parse_qs(m.request_history[1].body)
        for k in answer.keys():
            answer[k]=answer[k][0]
        for k in answer.keys():
            assert str(answer[k])==str(treacts[1][k])

        #actual restriction
        answer=parse_qs(m.request_history[2].body)
        for k in answer.keys():
            answer[k]=answer[k][0]
        for k in answer.keys():
            assert str(answer[k])==str(treacts[2][k])

# #02: user writes /start to bot
def test_start():
    tmsgs=json.load(open("test_data/02_user_start_msg.json","r",encoding="utf-8"))
    treacts=json.load(open("test_data/02_user_start_react.json","r",encoding="utf-8"))
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        request=dict()
        request['result']=[tmsgs[0]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request)

        request=tmsgs[1]#answer to posting
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request)

        s.chats_folder="test_chats/"
        s.settings_folder="test_settings/"
        s.load()
        tg_lib.init(test_token)
        
        id=-1
        update_list,id=tg_lib.get_updates()
        assert len(update_list)==1
        assert id==tmsgs[0]["update_id"]
        res=update_list[0]
        chat_id=res["message"]["chat"]["id"]
        assert chat_id==tmsgs[0]["message"]["chat"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==2
        answer=parse_qs(m.request_history[1].body)
        for k in answer.keys():
            answer[k]=answer[k][0]
        for k in answer.keys():
            assert str(answer[k])==str(treacts[1][k])


# #03: "status" button
def test_status():
    tmsgs=json.load(open("test_data/03_user_status_msg.json","r",encoding="utf-8"))
    treacts=json.load(open("test_data/03_user_status_react.json","r",encoding="utf-8"))
    def matcher1(r):
        if r.text.find("chat_id=-1001144274214")!=-1:
            return True
        return False
    def matcher2(r):
        if r.text.find("chat_id=-1001287084754")!=-1:
            return True
        return False
    def matcher3(r):
        if r.text.find("chat_id=-1001489654859")!=-1:
            return True
        return False
        
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        request=dict()
        request['result']=[tmsgs[0]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request)

        request=tmsgs[1]
        url=tg_lib.req_prefix+test_token+"/getChat"
        m.post(url=url,json=request,additional_matcher=matcher1)
        request=tmsgs[2]
        url=tg_lib.req_prefix+test_token+"/getChatMember"
        m.post(url=url,json=request,additional_matcher=matcher1)

        request=tmsgs[3]
        url=tg_lib.req_prefix+test_token+"/getChat"
        m.post(url=url,json=request,additional_matcher=matcher2)
        request=tmsgs[4]
        url=tg_lib.req_prefix+test_token+"/getChatMember"
        m.post(url=url,json=request,additional_matcher=matcher2)

        request=tmsgs[5]
        url=tg_lib.req_prefix+test_token+"/getChat"
        m.post(url=url,json=request,additional_matcher=matcher3)
        request=tmsgs[6]
        url=tg_lib.req_prefix+test_token+"/getChatMember"
        m.post(url=url,json=request,additional_matcher=matcher3)

        request=tmsgs[7]#answer to posting
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request)


        s.chats_folder="test_chats/"
        s.settings_folder="test_settings/"
        s.load()
        tg_lib.init(test_token)
        
        id=-1
        update_list,id=tg_lib.get_updates()
        assert len(update_list)==1
        assert id==tmsgs[0]["update_id"]
        res=update_list[0]
        chat_id=res["message"]["chat"]["id"]
        assert chat_id==tmsgs[0]["message"]["chat"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==8
        for i in range(7):
            answer=parse_qs(m.request_history[i+1].body)
            for k in answer.keys():
                answer[k]=answer[k][0]
            for k in answer.keys():
                assert str(answer[k])==str(treacts[i+1][k])


# #04: "i'm not a bot" button
def test_not_bot():
    tmsgs=json.load(open("test_data/04_user_not_bot_msg.json","r",encoding="utf-8"))
    treacts=json.load(open("test_data/04_user_not_bot_react.json","r",encoding="utf-8"))
    def matcher1(r):
        if r.text.find("chat_id=-1001144274214")!=-1:
            return True
        return False
    def matcher2(r):
        if r.text.find("chat_id=-1001287084754")!=-1:
            return True
        return False
    def matcher3(r):
        if r.text.find("chat_id=-1001489654859")!=-1:
            return True
        return False
        
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        request=dict()
        request['result']=[tmsgs[0]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request)

        request=tmsgs[1]
        url=tg_lib.req_prefix+test_token+"/getChat"
        m.post(url=url,json=request,additional_matcher=matcher1)
        request=tmsgs[2]
        url=tg_lib.req_prefix+test_token+"/getChatMember"
        m.post(url=url,json=request,additional_matcher=matcher1)

        request=tmsgs[3]
        url=tg_lib.req_prefix+test_token+"/getChat"
        m.post(url=url,json=request,additional_matcher=matcher2)
        request=tmsgs[4]
        url=tg_lib.req_prefix+test_token+"/getChatMember"
        m.post(url=url,json=request,additional_matcher=matcher2)

        request=tmsgs[5]
        url=tg_lib.req_prefix+test_token+"/getChat"
        m.post(url=url,json=request,additional_matcher=matcher3)
        request=tmsgs[6]
        url=tg_lib.req_prefix+test_token+"/getChatMember"
        m.post(url=url,json=request,additional_matcher=matcher3)

        request=tmsgs[7]#answer to posting
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request)


        s.chats_folder="test_chats/"
        s.settings_folder="test_settings/"
        s.load()
        tg_lib.init(test_token)
        
        id=-1
        update_list,id=tg_lib.get_updates()
        assert len(update_list)==1
        assert id==tmsgs[0]["update_id"]
        res=update_list[0]
        chat_id=res["message"]["chat"]["id"]
        assert chat_id==tmsgs[0]["message"]["chat"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==8
        for i in range(7):
            answer=parse_qs(m.request_history[i+1].body)
            for k in answer.keys():
                answer[k]=answer[k][0]
            for k in answer.keys():
                assert str(answer[k])==str(treacts[i+1][k])

# #05: user selected chat, got question and answered wrong
def test_wrong_answer():
    tmsgs=json.load(open("test_data/05_user_selected_chat_wrong_answer_msg.json","r",encoding="utf-8"))
    treacts=json.load(open("test_data/05_user_selected_chat_wrong_answer_react.json","r",encoding="utf-8"))
    #we need to test url-encoded string in request with "ordinary" string, so we make url with urlencode
    #then we remove "key=" from it and check corresponding url with find()
    def matcher_question(r):
        test_text=urlencode({"key":"Для прохождения проверки необходимо ответить на вопрос"}).replace("key=","")
        #t=open("matcher.txt","a",encoding="utf-8")
        #t.write("1.\n"+r.text+"\n"+test_text+"\n")
        #t.close()
        if r.text.find(test_text)!=-1:
            return True
        return False
    def matcher_wrong(r):
        test_text=urlencode({"key":"Ответ неправильный"}).replace("key=","")
        #t=open("matcher.txt","a",encoding="utf-8")
        #t.write("2.\n"+r.text+"\n"+test_text+"\n")
        #t.close()
        if r.text.find(test_text)!=-1:
            return True
        return False
    def matcher_update0(r):
        if r.text.find("offset")==-1:
            return True
        return False
    def matcher_update1(r):
        if r.text.find("offset")!=-1:
            return True
        return False
        
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        request=dict()
        request['result']=[tmsgs[0]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request,additional_matcher=matcher_update0)

        request=tmsgs[1]
        url=tg_lib.req_prefix+test_token+"/answerCallbackQuery"
        m.post(url=url,json=request)

        request=tmsgs[2]
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request,additional_matcher=matcher_question)

        s.chats_folder="test_chats/"
        s.settings_folder="test_settings/"
        s.load()
        tg_lib.init(test_token)
        sphinx_bot_start.reset_queues()
        
        id=-1
        update_list,id=tg_lib.get_updates()
        assert len(update_list)==1
        assert id==tmsgs[0]["update_id"]
        res=update_list[0]
        chat_id=res["callback_query"]["from"]["id"]
        assert chat_id==tmsgs[0]["callback_query"]["from"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==3
        for i in range(2):
            answer=parse_qs(m.request_history[i+1].body)
            for k in answer.keys():
                answer[k]=answer[k][0]
            for k in answer.keys():
                assert str(answer[k])==str(treacts[i+1][k])

        #we checked that user correctly got a question, now we must check answer

        request=dict()
        request['result']=[tmsgs[3]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request,additional_matcher=matcher_update1)

        request=tmsgs[4]
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request,additional_matcher=matcher_wrong)

        update_list,id=tg_lib.get_updates(id=1)#non-zero id, so mock will return second update
        assert len(update_list)==1
        assert id==tmsgs[3]["update_id"]
        res=update_list[0]
        chat_id=res["message"]["from"]["id"]
        assert chat_id==tmsgs[3]["message"]["from"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==5
        #we had additional getUpdates requset and it was not logged in treacts array, so we skip it and compare
        #last requset made (m.request_history[4]) with last request logged treacts[3]
        #this is incosistency bc other requests present in file one by one
        answer=parse_qs(m.request_history[4].body)
        for k in answer.keys():
            answer[k]=answer[k][0]
        for k in answer.keys():
            assert str(answer[k])==str(treacts[3][k])

# #06: user selected chat, got question and answered right
def test_right_answer():
    tmsgs=json.load(open("test_data/06_user_selected_chat_right_answer_msg.json","r",encoding="utf-8"))
    treacts=json.load(open("test_data/06_user_selected_chat_right_answer_react.json","r",encoding="utf-8"))
    #we need to test url-encoded string in request with "ordinary" string, so we make url with urlencode
    #then we remove "key=" from it and check corresponding url with find()
    def matcher_question(r):
        test_text=urlencode({"key":"Для прохождения проверки необходимо ответить на вопрос"}).replace("key=","")
        #t=open("matcher.txt","a",encoding="utf-8")
        #t.write("1.\n"+r.text+"\n"+test_text+"\n")
        #t.close()
        if r.text.find(test_text)!=-1:
            return True
        return False
    def matcher_right(r):
        test_text=urlencode({"key":"Вы дали правильный ответ"}).replace("key=","")
        #t=open("matcher.txt","a",encoding="utf-8")
        #t.write("2.\n"+r.text+"\n"+test_text+"\n")
        #t.close()
        if r.text.find(test_text)!=-1:
            return True
        return False
    def matcher_update0(r):
        if r.text.find("offset")==-1:
            return True
        return False
    def matcher_update1(r):
        if r.text.find("offset")!=-1:
            return True
        return False
        
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        request=dict()
        request['result']=[tmsgs[0]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request,additional_matcher=matcher_update0)

        request=tmsgs[1]
        url=tg_lib.req_prefix+test_token+"/answerCallbackQuery"
        m.post(url=url,json=request)

        request=tmsgs[2]
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request,additional_matcher=matcher_question)

        s.chats_folder="test_chats/"
        s.settings_folder="test_settings/"
        s.load()
        tg_lib.init(test_token)
        sphinx_bot_start.reset_queues()
        
        id=-1
        update_list,id=tg_lib.get_updates()
        assert len(update_list)==1
        assert id==tmsgs[0]["update_id"]
        res=update_list[0]
        chat_id=res["callback_query"]["from"]["id"]
        assert chat_id==tmsgs[0]["callback_query"]["from"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==3
        for i in range(2):
            answer=parse_qs(m.request_history[i+1].body)
            for k in answer.keys():
                answer[k]=answer[k][0]
            for k in answer.keys():
                assert str(answer[k])==str(treacts[i+1][k])

        #we checked that user correctly got a question, now we must check answer

        request=dict()
        request['result']=[tmsgs[3]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request,additional_matcher=matcher_update1)

        request=tmsgs[4]
        url=tg_lib.req_prefix+test_token+"/restrictChatMember"
        m.post(url=url,json=request)

        request=tmsgs[5]
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request,additional_matcher=matcher_right)



        update_list,id=tg_lib.get_updates(id=1)#non-zero id, so mock will return second update
        assert len(update_list)==1
        assert id==tmsgs[3]["update_id"]
        res=update_list[0]
        chat_id=res["message"]["from"]["id"]
        assert chat_id==tmsgs[3]["message"]["from"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==6
        #we had additional getUpdates requset and it was not logged in treacts array, so we skip it and compare
        #last requsets made (m.request_history[4] and [5]) with last request logged treacts[3] and [4]
        #this is incosistency bc other requests present in file one by one
        for i in range(4,6):
            answer=parse_qs(m.request_history[i].body)
            for k in answer.keys():
                answer[k]=answer[k][0]
            for k in answer.keys():
                assert str(answer[k])==str(treacts[i-1][k])

# #07: user writes incorrect command to bot
def test_wrongs_command():
    tmsgs=json.load(open("test_data/07_user_wrong_command_msg.json","r",encoding="utf-8"))
    treacts=json.load(open("test_data/07_user_wrong_command_react.json","r",encoding="utf-8"))
    with requests_mock.Mocker() as m:
        test_token="TEST123456"

        request=dict()
        request['result']=[tmsgs[0]]
        url=tg_lib.req_prefix+test_token+"/getUpdates"
        m.post(url=url,json=request)

        request=tmsgs[1]#answer to posting
        url=tg_lib.req_prefix+test_token+"/sendMessage"
        m.post(url=url,json=request)

        s.chats_folder="test_chats/"
        s.settings_folder="test_settings/"
        s.load()
        tg_lib.init(test_token)
        
        id=-1
        update_list,id=tg_lib.get_updates()
        assert len(update_list)==1
        assert id==tmsgs[0]["update_id"]
        res=update_list[0]
        chat_id=res["message"]["chat"]["id"]
        assert chat_id==tmsgs[0]["message"]["chat"]["id"]

        sphinx_bot_start.update_handler(res)
        assert len(m.request_history)==2
        answer=parse_qs(m.request_history[1].body)
        for k in answer.keys():
            answer[k]=answer[k][0]
        for k in answer.keys():
            assert str(answer[k])==str(treacts[1][k])