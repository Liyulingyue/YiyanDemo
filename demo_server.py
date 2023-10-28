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
Question_and_tripe_Answer = ["","","",""]


def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/Introduce_the_Book", methods=['POST'])
async def IntroduceBook():
    """
        给出答案之书的介绍和使用说明。
    """
    IntroduceText = f"""
        答案之书内置了{MAX_PAGE_ID}个答案，当你感到迷茫的时候，可以随机抽取一个语句，指引你的选择。
        
        你可以通过以下对话方式，触发答案之书的不同功能：
        1. `答案之书，刷新！`
            刷新答案之书的答案排序。
        2. `答案之书，翻开第66页。`
            查看答案之书第66页的内容。
        3. `答案之书，我是小帅，我很纠结要不要去跟小美表白，请帮帮我。`
            答案之书会随机抽取一个结果，并且给你接下来的行动提示。
    """
    return make_json_response({"message": IntroduceText})

@app.route("/Get_Answer_of_Number", methods=['POST'])
async def GetAnswerofNumber():
    """
        输入一个数字，查询答案之书的内容
    """
    num = request.json.get('number', "")
    if int(num) < 1 or int(num) > 268:
        return make_json_response({"message": "超出了答案之书的页码范围，请重新输入"})
    answer = answerBook[str(num)]
    prompt = "答案之书中该数字对应的内容是(message)，根据答案之书中的答案(message)，生成一段不超过100字的含义解释"
    return make_json_response({"message": answer, "prompt":prompt})

@app.route("/Shuffle_Book", methods=['POST'])
async def ShuffleBook():
    """
        对书本中的内容进行乱序组合
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

@app.route("/Get_Question_and_Find_Three_Answers", methods=['POST'])
async def GetQuestionandFindThreeAnswers():
    """
        在用户有疑惑或者问题的时候，随机翻开答案之书，抽取三个回复
    """
    for i in range(1,4):
        num = random.randint(MIN_PAGE_ID, MAX_PAGE_ID)
        answer = answerBook[str(num)]
        Question_and_tripe_Answer[i] = answer
    question = request.json.get('question', "")
    Question_and_tripe_Answer[0] = question
    # prompt = "答案之书中该数字对应的内容是(message)，根据答案之书中的答案(message)，生成一段不超过100字的含义解释，并针对用户困惑或疑问的事情(question)给出详细建议。"
    # return make_json_response({"message": answer, "question":question, "prompt":prompt})
    return make_json_response({"message": "答案之书根据你的问题，为你抽取了三个不同的选择，请选择答案。\n回复`第一个答案`即可查看第一个选择。"})

@app.route("/Git_Choosed_Answer", methods=['POST'])
async def GitChoosedAnswer():
    """
        在用户有疑惑或者问题的时候，随机翻开答案之书，抽取三个回复
    """
    question = Question_and_tripe_Answer[0]
    idx = request.json.get('number', "")
    answer = Question_and_tripe_Answer[idx]
    prompt = "答案之书中该数字对应的内容是(message)，根据答案之书中的答案(message)，生成一段不超过100字的含义解释，并针对用户困惑或疑问的事情(question)给出详细建议。"
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
    app.run(debug=True, host='127.0.0.1', port=8082)