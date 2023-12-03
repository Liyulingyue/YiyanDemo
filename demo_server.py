#!/usr/env python3
# -*- coding: UTF-8 -*-

from flask import Flask, request, send_file, make_response
from flask_cors import CORS
import json
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://yiyan.baidu.com"}})

with open("answersbook.json", "r", encoding='utf-8') as f:
    answerBook = json.load(f)
MIN_PAGE_ID = 1
MAX_PAGE_ID = 268


def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/Introduce_the_Book", methods=['POST'])
async def IntroduceBook():
    """
        展示答案之书的使用方法，可以通过`如何使用答案之书`，`答案之书的使用方法`等类似的语句触发。
    """
    IntroduceText = f"""
        答案之书内置了{MAX_PAGE_ID}个答案，当你感到迷茫的时候，可以随机抽取一个语句，指引你的选择。
        
        你可以通过以下对话方式，触发答案之书的不同功能：
        0. `展示答案之书的使用方法`
            展示答案之书的使用方法，和各个功能的触发样例语句。
        1. `答案之书，刷新！`
            刷新答案之书的答案排序。
        2.  样例1：
                `答案之书，我是小帅，我很纠结要不要去跟小美表白，请帮帮我。`
                答案之书会随机抽取一个结果，并且给你接下来的行动提示。
            样例2：
                `答案之书，我有个问题，今晚该不该点外卖`
                答案之书会随机抽取一个结果，并且给你接下来的行动提示。
            推荐参考样例2进行提问，即“答案之书，我有个问题，`你的问题`”
    """
    return make_json_response({"message": IntroduceText})

@app.route("/Shuffle_Book", methods=['POST'])
async def ShuffleBook():
    """
        重置或者刷新答案之书的内容。当用户需要重排、乱序、刷新答案之书的内容时，触发此功能。
    """
    mylist = list(range(MIN_PAGE_ID, MAX_PAGE_ID+1))
    random.shuffle(mylist)
    for i in range(MIN_PAGE_ID, MAX_PAGE_ID+1):
        source_id = i
        target_id = mylist[i-1]
        tmp = answerBook[str(source_id)]
        answerBook[str(source_id)] = answerBook[str(target_id)]
        answerBook[str(target_id)] = tmp
    return make_json_response({"message": "书本已重置。"})

@app.route("/Answer_Question_in_Random", methods=['POST'])
async def AnswerQestioninRandom():
    """
        给予用户回答，当用户提问“答案之书，我有个问题，<用户的问题>”时触发此功能。
        具体来说，当用户向答案之书提问时或者感到困惑向答案之书咨询时，随机打开答案之书，给出建议。
        一些使用样例：
        答案之书，我有个问题，我今晚该加班吗
        答案之书，我应该点外卖吗？
        答案之书，请告诉我今晚去公园合不合适
        答案之书，我很纠结，请告诉我该不该向小美表白
    """
    num = random.randint(MIN_PAGE_ID, MAX_PAGE_ID)
    question = request.json.get('question', "")
    answer = answerBook[str(num)]
    # prompt = "答案之书中该数字对应的内容是(message)，根据答案之书中的答案(message)，对用户困惑或疑问的事情(question)给出非常详细建议。"
    prompt = "根据答案之书中的答案(message)，针对用户困惑或疑问的事情(question)给出非常详细建议。最终以json的形式回复用户{‘答案’：答案之书的答案，'解释说明'：一言生成的结果}。"
    return make_json_response({"message": answer, "question":question, "prompt":prompt})


@app.route("/logo.png")
async def plugin_logo():
    """
        注册用的：返回插件的logo，要求48 x 48大小的png文件.
        注意：API路由是固定的，事先约定的。
    """
    return send_file('logo.png', mimetype='image/png')


@app.route("/.well-known/ai-plugin.json")
async def plugin_manifest():
    """
        注册用的：返回插件的描述文件，描述了插件是什么等信息。
        注意：API路由是固定的，事先约定的。
    """
    host = request.host_url
    with open(".well-known/ai-plugin.json", encoding="utf-8") as f:
        text = f.read().replace("PLUGIN_HOST", host)
        return text, 200, {"Content-Type": "application/json"}


@app.route("/.well-known/openapi.yaml")
async def openapi_spec():
    """
        注册用的：返回插件所依赖的插件服务的API接口描述，参照openapi规范编写。
        注意：API路由是固定的，事先约定的。
    """
    with open(".well-known/openapi.yaml", encoding="utf-8") as f:
        text = f.read()
        return text, 200, {"Content-Type": "text/yaml"}

@app.route('/')
def index():
    return 'welcome to my webpage!'

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)