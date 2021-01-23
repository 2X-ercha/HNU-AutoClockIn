import requests
import base64
import json
import os

headers_1 = {
    "Cookie": "arccount62298=c; arccount62019=c",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66"
}

headers_2 = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "fangkong.hnu.edu.cn",
    "Origin": "https://fangkong.hnu.edu.cn",
    "Referer": "https://fangkong.hnu.edu.cn/app/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75"
}

# 获取变量

usr = os.getenv("usr")
pwd = os.getenv("pwd")
sckey = os.getenv("sckey")
RealAddress = os.getenv("RealAddress")
l = os.getenv("RealProvince_City_County").split(",")
RealCity = l[1]
RealCounty = l[2]
RealProvince = l[0]

# step 1: 获取验证码Token及图片

def ClockIn():
    try:
        token_json = requests.get("https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode", headers=headers_1)

        if token_json.status_code!=200: print("Token爬取失败，正在重试")
        while (token_json.status_code!=200):
            token_json = requests.get("https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode", headers=headers_1)

        data = json.loads(token_json.text)
        token = data["data"]["Token"]

        img_url = "https://fangkong.hnu.edu.cn/imagevcode?token=" + token
        with open("img.jpg", "wb") as img:
            img.write(requests.get(img_url).content)

        # 解析验证码

        with open("img.jpg",'rb') as f:
            img = base64.b64encode(f.read())
        data = '{"image":"%s"}'%str(img)[2:]

        response = requests.post('https://www.paddlepaddle.org.cn/paddlehub-api/image_classification/chinese_ocr_db_crnn_mobile', headers=headers_1, data=data)
        result = response.json()['result'][0]["data"][0]["text"]

        # step 2: 模拟登录操作

        data = {
            "Code": "202001120130",
            "Password": "s2002092517S",
            "Token": token,
            "VerCode": result
        }

        session = requests.Session()
        response = session.post("https://fangkong.hnu.edu.cn/api/v1/account/login", headers=headers_2, data=json.dumps(data))

        if response.json()["code"] != 0:
            print("验证码错误")
            requests.get("http://sc.ftqq.com/"+ sckey +".send?text=打卡失败啦&desp=验证码错误，正在重试")
            ClockIn()
        else:
            # step 3: 模拟打卡操作

            data = {
                "BackState": 1,
                "MorningTemp": "36.5",
                "NightTemp": "36.5",
                "RealAddress": RealAddress,
                "RealCity": RealCity,
                "RealCounty": RealCounty,
                "RealProvince": RealProvince,
                "tripinfolist": []
            }

            response = session.post("https://fangkong.hnu.edu.cn/api/v1/clockinlog/add", headers=headers_2, data=json.dumps(data))

            msg = response.json()["msg"]
            print(msg)
            requests.get("http://sc.ftqq.com/"+ sckey +".send?text=打卡成功啦！&desp=" + msg)
    except:
        print("Error")
        requests.get("http://sc.ftqq.com/"+ sckey +".send?text=打卡失败啦！&desp=打卡失败，正在重试")
        ClockIn()

if __name__ == '__main__':
    ClockIn()