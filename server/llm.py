import json
import re

from openai import OpenAI
from zhipuai import ZhipuAI
def llm_invoke(base_url:str,api_key:str,model:str,prompt:str):
    try:
        # 调用ChatGPT API
        client = OpenAI(base_url=base_url,api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个善于阅读招标文件的AI阅读助手，能专业、准确的对文件进行深入分析，寻找特定信息，旨在帮助您快速理解招标流程和投标相关事宜。"},
                {"role": "user", "content": prompt}
            ],
            top_p = 0.7,
            temperature = 0.90,
            max_tokens = 4095,
        )
        output = response.choices[0].message.content
        print('######')
        print(output)
        # 使用正则表达式提取dict数据
        output_dict = re.search(r'```.*?(\{.*?\}.*?).*?```', output, re.S).group(1)
        print(output_dict, type(output_dict))
        try:
            output_dict = json.loads(output_dict)
            print(output_dict)
        except:
            output_dict = output_dict[::-1].replace(',', '', 1)[::-1]
            output_dict = json.loads(output_dict)
        print(output_dict, type(output_dict))
        return output_dict

    except Exception as e:
        print(e)


# llm_invoke('https://api.moonshot.cn/v11','sk-jVugDGCT2vigriUGygB6zQO27x1JYD5Cm2wnxWbmSPEwj2GP','moonshot-v1-81k','你好')

# check_model 检查模型

"""智谱ai"""
# api_key错误:openai.AuthenticationError: Error code: 401 - {'error': {'code': '1000', 'message': '身份验证失败。'}}
# {"status": 0, "err": "无效的apikey！"}

# model错误openai.BadRequestError: Error code: 400 - {'error': {'code': '1211', 'message': '模型不存在，请检查模型代码。'}}
# {"status": 0, "err": "不存在的model！"}

# 请求url错误openai.NotFoundError: Error code: 404 - {'timestamp': '2024-11-20T07:40:11.069+00:00', 'status': 404, 'error': 'Not Found', 'path': '/v3/chat/completions'}
# {"status": 0, "err": "url.not_found 请求地址错误！"}


"""月之暗面"""
# model错误openai.NotFoundError: Error code: 404 - {'error': {'message': 'Not found the model moonshot-v1-8k1 or Permission denied', 'type': 'resource_not_found_error'}}
# {"status": 0, "err": "不存在的model！"}

# api_key错误openai.AuthenticationError: Error code: 401 - {'error': {'message': 'Invalid Authentication', 'type': 'invalid_authentication_error'}}
# {"status": 0, "err": "无效的apikey！"}

#请求url错误openai.NotFoundError: Error code: 404 - {'code': 5, 'error': 'url.not_found', 'message': '没找到对象', 'method': 'POST', 'scode': '0x5', 'status': False, 'ua': 'OpenAI/Python 1.54.4', 'url': '/v11/chat/completions'}
# {"status": 0, "err": "url.not_found 请求地址错误！"}


# 成功 {"status": 200, "msg": "注册成功！"}