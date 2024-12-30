import time
import requests
import base64
# def is_text_page(page):
#     text = page.get_text("text")  # 尝试提取文本
#     if text:
#         return True
#     else:
#         return False
#
# def analyze_pdf(pdf_path):
#     document = fitz.open(pdf_path)
#     page = document[1]
#     if is_text_page(page):
#         print(f"是文本内容。")
#     else:
#         print(f"是图片内容。")
#     document.close()
#
# # 使用示例
# analyze_pdf("/Users/yuejunzhang/Desktop/中建招标/alldemo/server/答疑文件.pdf")

def get_access_token():
    api_key = 'q5Hhi6lYHwV3oysXAXPyG3Z8'
    secret_key = '3U8pVAPT3tk1Ufv9CunGyFP1EuJ8lDwX'
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    access_token = response.json().get("access_token")
    print('access_token:', access_token)
    return access_token

def get_task_id(file_path, access_token):
    request_host = "https://aip.baidubce.com/rest/2.0/ocr/v1/doc_convert/request"
    # 二进制方式打开文件
    f = open(file_path, 'rb')
    pdffile = base64.b64encode(f.read())
    params = {"pdf_file": pdffile}
    request_url = request_host + "?access_token=" + access_token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, headers=headers, data=params)
    task_id = response.json().get('result').get('task_id')
    return task_id

def get_word_address(task_id, access_token):
    # access_token = '24.6a0779b58203ad0067ae6c70e2accdb1.2592000.1734780557.282335-116343279'
    request_host = "https://aip.baidubce.com/rest/2.0/ocr/v1/doc_convert/get_request_result"
    params = {"task_id": f"{task_id}"}
    print(params)
    request_url = request_host + "?access_token=" + access_token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, headers=headers, data=params)
    print(response.json())
    time.sleep(7.5)
    response = requests.post(request_url, headers=headers, data=params)
    word_path = response.json().get('result').get('result_data').get('word')
    print(word_path)
    return word_path

def get_word_text(word_path,task_id):
    url = word_path
    response = requests.get(url)
    with open(f'./ocrpdftoword/{task_id}.docx',mode='wb')as f:
        f.write(response.content)

    return f'./ocrpdftoword/{task_id}.docx'

if __name__ == '__main__':
    pass
    # access_token = get_access_token()
    # task_id = get_task_id('/Users/yuejunzhang/Desktop/中建招标/alldemo/server/答疑文件.pdf', access_token)
    # word_path = get_word_address(task_id, access_token)
    # get_word_text(word_path,task_id)


