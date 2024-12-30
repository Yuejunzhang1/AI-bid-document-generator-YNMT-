# coding=utf-8
import json
import uuid
import openai
from flask import Flask, request, jsonify, url_for, Response, send_from_directory
import os
from werkzeug.utils import secure_filename
from alldemo111.server.llm import llm_invoke
from alldemo111.server.utils import GetFileContent, JsontoWord
from openai import OpenAI
app = Flask(__name__)
app.config['UPLPAD_FOLDER'] = './files'
app.config['WORD_FOLDER'] = './word'

# 设置允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/preview_file', methods=['POST'])
# def preview_file():
#     data = request.get_json()
#     fileid = data.get('fileid')
#     print(data)
#     return {'bd_file_path':fileid}


@app.route('/cheak_openai_parmas', methods=['POST'])
def cheak_openai_parmas():
    data = request.get_json()
    print('####', data, type(data))
    api_key = data.get('api_key')
    print(api_key)
    base_url = data.get('base_url')
    print(base_url)
    model_name = data.get('model_name')
    print(model_name)
    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "你好"}
            ]
        )
        return jsonify({"status": 200, "msg": '参数验证成功，注册成功！'})
    except openai.NotFoundError as e:
        return json.dumps({"status": 0, "err": '请求url错误！'})

    except openai.AuthenticationError as e:
        return json.dumps({"status": 0, "err": 'api_key错误'})

    except openai.BadRequestError as e:
        return json.dumps({"status": 0, "err": '模型错误！'})

    except openai.APIConnectionError as e:

        return json.dumps({"err": "连接错误！", "status": 0})
    except Exception as e:
        # return jsonify({"status": 0, "err": '发生了其他错误'}), 500
        return json.dumps({"err": "其他错误！", "status": 0})

@app.route('/upload', methods=['POST'])
def upload_file():
    global qa_file_path
    # 检查是否有文件在请求中
    if 'bd_file' not in request.files:
        return jsonify({"status": 0, "err": "没有上传招标文件"})
    bd_file = request.files['bd_file']
    # 如果用户没有选择文件，浏览器可能会提交一个没有文件名的空部分
    if bd_file.filename == '':
        return jsonify({"status": 0, "err": "没有上传招标文件"})

    if bd_file and allowed_file(bd_file.filename):
        print(app.config['UPLPAD_FOLDER'])
        filename = secure_filename(bd_file.filename)
        fileid = str(uuid.uuid4()) + '.' + filename
        bd_file_path = os.path.join(app.config['UPLPAD_FOLDER'], fileid)
        print(bd_file_path)
        bd_file.save(bd_file_path)
        bd_file_path_download_url = url_for('download_file', filename=bd_file_path, _external=True)
        print(bd_file_path_download_url)
        if 'qa_file' in request.files:
            qa_file = request.files['qa_file']
            if qa_file.filename != '':
                qa_file_path = os.path.join(app.config['UPLPAD_FOLDER'], 'QA' + fileid)
                print(qa_file_path)
                qa_file.save(qa_file_path)
            return jsonify(
                {"status": 200, "fileid": fileid})
        else:
            return jsonify(
                {"status": 200, "fileid": fileid})
    else:
        return jsonify({"status": 0, "err": "只支持pdf、doc、docx文件"})


@app.route('/extract', methods=['POST'])
def extract_fields():
    data = request.get_json()
    print('####', data)
    fileid = data.get('fileid')
    base_url = data.get('base_url')
    print(base_url)
    modle_name = data.get('modle_name')
    print(modle_name)
    api_key = data.get('api_key')
    print(api_key)
    fileds = data.get('fileds')
    fileds = json.loads(fileds)
    user_words = data.get('user_words')
    print(user_words)
    task_words = data.get('task_words')
    print(task_words)
    aaaaa = {}
    for i in fileds:
        aaaaa[i["readLabel"]] = i["promptWords"]
    print('####:', aaaaa)
    if not fileid or not fileds:
        return jsonify({"status": 0, "err": "没有文件id或字段列表"})

    '''读取bd_file内容'''
    bd_file_path = os.path.join(app.config['UPLPAD_FOLDER'], fileid)
    if not os.path.exists(bd_file_path):
        return jsonify({"status": 0, "err": "错误的文件id"})
    bd_content = GetFileContent(file_path=bd_file_path)

    qa_file_path = os.path.join(app.config['UPLPAD_FOLDER'], 'QA' + fileid)
    qa_content = None
    if os.path.exists(qa_file_path):
        '''读取qa_file内容'''
        print('qa_file_path:', qa_file_path)
        qa_content = GetFileContent(file_path=qa_file_path)
        print('qa_content1111:', qa_content)

    user_prompt = (f"# 角色：{user_words}\n"
                   "# 需要提取的【文本】：\n"
                   f"文档1:{bd_content}\n"
                   f"文档2:{qa_content}\n"
                   "\n"
                   "# 提取重点注意: \n"
                   "优先从`文档1`中提取，如果没有提取到，再从`文档2`中提取。\n"
                   "# 任务\n"
                   f"{task_words}\n"
                   "#【字段列表】：\n"
                   f"{list(aaaaa.keys())}\n"
                   "\n"
                   "#注意事项\n"
                   "1.如果字段缺失或无法识别，请使用“无”。否则会受到惩罚！\n"
                   "2.确保所有金额需包含原本的单位。\n"
                   "3.确保所有时间字段都为14位标准时间格式。\n"
                   "4.返回的示例格式必须为:\n"
                   "```python"
                   "{\n"
                   "\"项目名称\":\"湖南财信金融控股集团有限公司滨江金融中心T2写字楼室内装修工程设计、施工、采购工程总承包\",\n"
                   "\"招标人\":\"湖南财信金融控股集团有限公司\",\n"
                   "\"工程地点\":\"工程地点\"\n"
                   "}\n"
                   "```\n否则会收到严重惩罚！！！！")
    print('user#####:', user_prompt)
    '''请求大模型，返回结果'''
    extracted_data = llm_invoke(base_url, api_key, modle_name, user_prompt)
    print('@@@@@')
    return Response(json.dumps({"status": 200, "data": extracted_data}), mimetype='application/json')


@app.route('/generate_word', methods=['POST'])
def json_to_word():
    bbbbb = {}
    data = request.get_json()
    print('######', data)
    fileds = data.get('fileds')
    print("####", fileds)
    a = json.loads(fileds)
    # print('#####', a)
    for i in a:
        bbbbb[i["readLabel"]] = i["promptWords"]
    # print('####:', bbbbb)
    if not data:
        return jsonify({"status": 0, "err": "没有提供生成word的数据"})
    word_file_name = JsontoWord(app.config['WORD_FOLDER'],bbbbb)
    # word_file_name = JsontoWord(app.config['WORD_FOLDER'], fileds)
    print('word_file_name:', word_file_name)
    download_url = url_for('download_file', filename=word_file_name, _external=True)
    print('download_url:', download_url)
    return jsonify({"status": 200, "url": download_url})


@app.route('/downlaodfile/<filename>', methods=['GET'])
def download_file(filename):
    print("app.config['WORD_FOLDER']", app.config['WORD_FOLDER'])
    print('filename：', filename)
    if '-' in filename:
        return send_from_directory(directory=app.config['UPLPAD_FOLDER'], path=filename, as_attachment=True)
    else:
        return send_from_directory(directory=app.config['WORD_FOLDER'], path=filename, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLPAD_FOLDER']):
        os.makedirs(app.config['UPLPAD_FOLDER'])
    if not os.path.exists(app.config['WORD_FOLDER']):
        os.makedirs(app.config['WORD_FOLDER'])
    # 启动Flask应用
    app.run(host='0.0.0.0', port=8080, debug=False)
