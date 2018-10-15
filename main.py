import os

from cek import (
    Clova, SpeechBuilder, ResponseBuilder
)

import boto3
from boto3.dynamodb.conditions import Key, Attr

from flask import Flask, request, jsonify

# 設定
application_id = "com.genso.check"
clova = Clova(application_id=application_id, default_language="ja", debug_mode=False)
speech_builder = SpeechBuilder(default_language='ja')
response_builder = ResponseBuilder(default_language='ja')

# 起動時に実行
@clova.handle.launch
def launch_request_handler(clova_request):
    return clova.response("こんにちは，元素番号を教えてください")


# 終了時に実行
@clova.handle.end
def end_handler(clova_request):
    return

# インテントを取得したら実行
@clova.handle.intent("ElementalCheck")
def intent_handler(clova_request):
    res=None
    # Konamonスロットタイプの単語を取得
    number = clova_request.slot_value('num')
    if(int(number)>=1 and int(number)<=20):
        res = make_element_info_name_by_num(str(number))
    else:
        res = clova.response(str("現在登録されていません"))
    return res

# デフォルトはこれを実行
@clova.handle.default
def default_handler(clova_request):
    return clova.response("すみません．もう一度お願いします")

app = Flask(__name__)

@app.route('/', methods=['POST'])
def my_service():
    resp = clova.route(request.data, request.headers)
    resp = jsonify(resp)
    # make sure we have correct Content-Type that CEK expects
    resp.headers['Content-Type'] = 'application/json;charset-UTF-8'
    return resp

#元素名の回答を出力
def make_element_info_name_by_num(num):
    try:
        element_info = get_element_info_for(num)
        message = ''
        reprompt = None
        end_session = False
        if element_info is None:
            # 元素名が見つからない場合
            message = '{} 番の情報が見つかりませんでした。もう一度教えてください。'.format(
                num
            )
            reprompt = '元素番号を教えてください。'
        else:
            # 元素名が見つかった場合
            message = '元素番号 {} 番の元素名は、{}、元素記号は、{} です。'.format(
                num,
                element_info['yomi'],
                element_info['symbol']
            )
            end_session = True
        # build response
        response = response_builder.simple_speech_text(message, end_session=end_session)
        if reprompt is not None:
            response = response_builder.add_reprompt(response, reprompt)
        return response
    except Exception as e:
        raise e

#DynamoDB
def get_element_info_for(num):
    #指定した元素番号の元素名を取得する
    #存在しない場合はNoneを返す。
    if num is None or '' == num:
        raise ValueError('num is None or empty...')
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Elements')
        response = table.get_item(
            Key={
                'num': num
            }
        )
        result = None
        item = response.get('Item', None)
        if item:
            result = item
        return result
    except Exception as e:
        raise e

if __name__ == "__main__":
    app.run()
