import base64
import requests
from bs4 import BeautifulSoup
import re
import random
import math
import argparse
import json
import pandas as pd

def get_text(url):
    #获取源代码
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    s = requests.get(url, headers=headers,verify=False)
    return s.text
def get_all_css_classes(url,text):
    #获取全部<link rel="stylesheet" type="text/css" href="" />加载的css中所有的类名
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    soup = BeautifulSoup(text, 'html.parser')
    css_links = []
    exclude_list = ['bootstrap', 'chosen', 'bootbox', 'awesome', 'animate', 'picnic', 'cirrus', 'iconfont', 'jquery', 'layui', 'swiper']     # 排除的插件库
    for link in soup.find_all('link', rel='stylesheet'):  # 获取外部css的链接
        href = link.get('href')
        if href and re.search(r'\.css(\?.*)?$', href):
            if not any(exclude in href for exclude in exclude_list):
                if href.startswith('http'):
                    css_links.append(href)
                    print(href)
                else:
                    css_links.append(requests.compat.urljoin(url, href))
                    print(requests.compat.urljoin(url, href))
    all_classes = set()
    for css_link in css_links:
        css_content = requests.get(url=css_link,headers=headers,verify=False).text # 下载css
        if css_content:
            classes = set()
            class_pattern = r'\.([\w\-]+)'
            matches = re.findall(class_pattern, css_content)
            classes.update(matches)
            all_classes.update(classes)
    return sorted(all_classes)    #返回css类名
def get_text_css_class(text):
    #获取源码中的类名
    soup = BeautifulSoup(text, 'html.parser')
    # 找到所有的标签，并提取它们的 class 属性
    all_classes = set()  # 使用集合来存储唯一的类名，避免重复
    for tag in soup.find_all(True):  # 查找所有标签
        classes = tag.get('class')  # 获取标签的 class 属性值
        if classes:  # 如果存在 class 属性
            all_classes.update(classes)  # 将类名添加到集合中
    return sorted(all_classes)
def get_text_api(source_code):
    #获取源码中的api接口
    # 使用正则表达式查找以"/"或'/'开头，并以".css"或".js"结尾的字符串
    pattern = r"['\"](\/[^\n\r'\"]*?)?['\"]"
    matches = re.findall(pattern, source_code)
    # 将匹配的路径添加到列表中，去掉.css和.js后缀
    apis = []
    exclude_list = ['/', '/favicon.ico', '/login', '/register', '/login.html', '/register.html']  # 排除的插件库
    for match in matches:
        match = re.sub(r'\?.*$', '', match)
        # 如果路径不包含 .css 或 .js 后缀，则添加到 cleaned_paths
        if not re.search(r'\.(css|js)([^\w.]|$)', match):
            if match != '' and match not in exclude_list:
                apis.append(match)
    return apis
def get_power(text):
    #获取power by/powered by后的内容
    pattern = r'(?:powered by|power by)\s+(<a\s+[^>]*href="([^"]+)"[^>]*>|[^<>\s]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        if match.group(2):  # 如果匹配的是<a href="...">
            return match.group(2)  # 返回URL
        else:
            return match.group(1)  # 返回单词或短语
    return None
def fofa(base):
    #通过fofa查询第一页最大条数为500的指纹数据
    with open('config.json', 'r') as f:
        config = json.load(f)
        fofa_api_key = config['fofa_api_key']
    url = f'https://fofa.info/api/v1/search/all?&key={fofa_api_key}&qbase64={base}&size=500'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    s = requests.get(url, headers=headers)
    return s.json()
def save_to_file(data, filename, filetype, size_value):
    #数据保存到文件
    if filetype == 'txt':
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Size: {size_value}\n")
            for item in data:
                f.write("%s\n" % item)
    elif filetype == 'xlsx':
        df = pd.DataFrame(data, columns=["URL", "IP", "Port"])
        df.loc[0, 'URL'] = f"Size: {size_value}"
        df.to_excel(filename, index=False)
def main(url, param=None, output_file=None, execute_fofa=False):
    s = get_text(url)
    apis = get_text_api(s)
    if len(apis) > 0:
        sqrt_number_api = math.floor(math.sqrt(len(apis)))
        random_apis = random.sample(apis, sqrt_number_api)
        joined_apis = '" && "'.join(random_apis)
    else:
        print("没有找到接口")
        joined_apis = ''
    classes = set(get_text_css_class(s)).intersection(get_all_css_classes(url, s))
    if len(classes) > 0:
        classes = sorted(classes)
        sqrt_number_classes = math.ceil(math.sqrt(len(classes)))
        random_classes = random.sample(classes, sqrt_number_classes)
        joined_classes = '" && "'.join(random_classes)
    else:
        print("没有找到共同的类名。")
        joined_classes = ''
    if joined_classes and joined_apis:
        fingerprint = '("' + joined_apis + '") || ("' + joined_classes + '")'
    elif joined_classes:
        fingerprint = '"' + joined_classes + '"'
    else:
        fingerprint = '"' + joined_apis + '"'
    powerby_str = get_power(s)
    if powerby_str:
        fingerprint = '( ' + fingerprint + ' )' + ' && "' + powerby_str + '"'
    if param:
        fingerprint = '( ' + fingerprint + ' )' + ' && "' + param + '"'
    print('构造的指纹如下\n' + fingerprint)
    if execute_fofa:
        results = fofa(base64.b64encode(fingerprint.encode()).decode())
        result_data = results.get('results', [])
        size_value = results.get('size', 0)  # 获取size值
        if output_file:
            filetype = output_file.split('.')[-1]
            save_to_file(result_data, output_file, filetype, size_value)
        else:
            print(f"通过Fofa共搜索出{size_value}条数据")
            for item in result_data:
                print(item)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="依据css类 Api等来发现网站指纹,通过Fofa寻找同源码网站,使用Fofa查询之前要在json文件中添加Fofa key")
    parser.add_argument('-u', '--url', type=str, required=True, metavar='', help='网站Url')
    parser.add_argument('-p', '--param', type=str, required=False, metavar='',
                        help='输入要添加的参数,不要带问号、双引号这些特殊字符,要不然Fofa搜索时会报错的')
    parser.add_argument('-f', '--fofa', action='store_true', help='是否执行Fofa搜索,不带-f选项只会输出框架指纹')
    parser.add_argument('-o', '--output', type=str, required=False, metavar='', help='输出文件名,可以是txt或xlsx格式')

    args = parser.parse_args()
    if args.output:
        valid_formats = ['.txt', '.xlsx']
        file_format = args.output[-4:].lower()  # 获取文件名后缀并转为小写
        if file_format not in valid_formats:
            print("输出文件格式必须是txt或xlsx")
            exit()
    main(args.url, args.param, args.output, args.fofa)
