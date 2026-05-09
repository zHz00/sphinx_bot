import pytest
import tg_lib
import requests_mock
import requests
import json

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