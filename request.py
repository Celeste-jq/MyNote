# 爬外网
import requests
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}
proxies = {
     'http': 'socks5://127.0.0.1:1089',
     'https': 'socks5://127.0.0.1:1089'
 }
response = requests.get("https://openai.com/", proxies=proxies, headers=headers, timeout=4)
data = response.text
print(f'查询代理的地理位置，返回的结果是{data}')