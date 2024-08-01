import base64
import requests
from bs4 import BeautifulSoup
import re
import random
import math
import argparse
import json
import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import mmh3
import codecs


def get_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    #获取源代码
    try:
        s = requests.get(url, headers=headers, verify=False)
        if str(s.status_code)[0] == '2':
            return s.text,url
        else:
            if url.startswith('http://'):
                url = 'https://' + url[len('http://'):]
            elif url.startswith('https://'):
                url = 'http://' + url[len('https://'):]
            s = requests.get(url, headers=headers, verify=False)
            return s.text, url
    except:
        if url.startswith('http://'):
            url = 'https://' + url[len('http://'):]
        elif url.startswith('https://'):
            url = 'http://' + url[len('https://'):]
        try:
            s = requests.get(url, headers=headers, verify=False)
            return s.text,url
        except:
            return '',url
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
                else:
                    css_links.append(requests.compat.urljoin(url, href))
    all_classes = set()
    for css_link in css_links:
        try:
            css_content = requests.get(css_link, headers=headers, verify=False, timeout=10).text  # 下载CSS
            if css_content:
                class_pattern = r'\.([\w\-]+)'
                matches = re.findall(class_pattern, css_content)
                all_classes.update(matches)
        except :
            return []
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
    pattern = r"['\"]((\/|\.\/)[^\n\r'\"?]+)(\?[^\n\r'\" ]*)?['\"]"
    matches = re.findall(pattern, source_code)
    # 将匹配的路径添加到列表中，去掉.css和.js后缀
    apis = []
    exclude_api = ['/', '//', '/favicon.ico', '/login', '/register', '/login.html', '/register.html']  # 排除的滥用接口
    exclude_list = ['bootstrap', 'chosen', 'bootbox', 'awesome', 'animate', 'picnic', 'cirrus', 'iconfont', 'jquery','layui', 'swiper']  # 排除的插件库
    for match in matches:
        match = match[0]  # 由于 findall 返回的是元组，需要取第一个元素
        match = re.sub(r'\?.*$', '', match)  # 去除查询参数
        # 仅当路径与 exclude_api 列表中的任意一个完全匹配时，才会被排除
        if match and match not in exclude_api:
            contains_excluded_str = False
            for ex_str in exclude_list:
                if ex_str in match:
                    contains_excluded_str = True
                    break
            # 如果路径不包含任意一个 exclude_list 中的字符，则添加到 apis 列表中
            if not contains_excluded_str:
                apis.append(match)
    return apis

def extract_base_url(url):
    if url.startswith('https://'):
        pattern = r'https://([a-zA-Z0-9.-]+)\.(cn|com)'
        match = re.match(pattern, url)
        if match:
            base_url = f"https://{match.group(1)}.{match.group(2)}"
            return base_url
        else:
            return None
    elif url.startswith('http://'):
        pattern = r'http://([a-zA-Z0-9.-]+)\.(cn|com)'
        match = re.match(pattern, url)
        if match:
            base_url = f"http://{match.group(1)}.{match.group(2)}"
            return base_url
        else:
            return None


    pattern = r'https://([a-zA-Z0-9.-]+)\.(cn|com)'
    match = re.match(pattern, url)
    if match:
        base_url = f"https://{match.group(1)}.{match.group(2)}"
        return base_url
    else:
        return None


def icon_hashs(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    s, url = get_text(url)
    base_url = extract_base_url(url)
    #print(base_url)
    apis=get_text_api(s)
    if len(apis) > 0:
        filtered_apis = [api for api in apis if api.endswith(('.ico'))]
    icons = filtered_apis
    for api in icons:
        api = base_url + api
        #print(api)
        favicon_response = requests.get(api, headers=headers, verify=False)
        if favicon_response.status_code == 200:
            favicon_hashs = mmh3.hash(codecs.lookup('base64').encode(favicon_response.content)[0])
            #print('icon_hash="{}"'.format(favicon_hash))
        return 'icon_hash="{}"'.format(favicon_hashs)



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
def save_to_file(data, filename, filetype, size_value, url,fingerprint):
    #数据保存到文件
    if filetype == 'txt':
        with open(filename, 'a+', encoding='utf-8') as f:
            f.write(f"提取Url: {url}\n")
            f.write(f"Size: {size_value}\n")
            f.write(f"指纹：{fingerprint}\n")
            for item in data:
                f.write("%s\n" % item)
    elif filetype == 'xlsx':
        df_data = pd.DataFrame(data, columns=["URL", "IP", "Port"])
        metadata = {"URL": f"{url}", "Size": size_value ,"fingerprint" : fingerprint}
        file_exists = os.path.exists(filename)
        if not file_exists:
            with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
                df_metadata_header = pd.DataFrame(columns=["URL", "Size" ,"fingerprint"])
                df_metadata_header.to_excel(writer, index=False, startrow=0, header=True)
                df_metadata = pd.DataFrame([metadata])
                df_metadata.to_excel(writer, index=False, header=False, startrow=1)
                header_df = pd.DataFrame(columns=["URL", "IP", "Port"])
                header_df.to_excel(writer, index=False, startrow=2, header=True)
                df_data.to_excel(writer, index=False, header=False, startrow=3)
        else:
            with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                workbook = writer.book
                sheet = workbook.active
                df_metadata_header = pd.DataFrame(columns=["URL", "Size", "fingerprint"])
                for r in dataframe_to_rows(df_metadata_header, index=False, header=True):
                    sheet.append(r)
                df_metadata = pd.DataFrame([metadata])
                for r in dataframe_to_rows(df_metadata, index=False, header=False):
                    sheet.append(r)
                header_df = pd.DataFrame(columns=["URL", "IP", "Port"])
                for r in dataframe_to_rows(header_df, index=False, header=True):
                    sheet.append(r)
                for r in dataframe_to_rows(df_data, index=False, header=False):
                    sheet.append(r)
                workbook.save(filename)

def main(url, param=None, output_file=None, execute_fofa=False, readfile=None):
    #批量读取Url
    if readfile:
        with open(readfile, 'r') as f:
            urls = f.readlines()
        for url in urls:
            url = url.strip()
            process_url(url, param, output_file, execute_fofa)
    else:
        process_url(url, param, output_file, execute_fofa)

def process_url(url, param=None, output_file=None, execute_fofa=False):
    start_url = url
    s,url = get_text(url)
    icon_hash = icon_hashs(url)
    if s == '':
        print(f"{start_url}访问不可达")
        return ''
    apis = get_text_api(s)
    if len(apis) > 0:
        filtered_apis = [api for api in apis if api.endswith(('.css', '.js', '.ico', '.png', '.jpg'))]
        other_apis = [api for api in apis if not api.endswith(('.css', '.js', '.ico', '.png', '.jpg'))]
        if len(other_apis) > 6:
            sqrt_number_other = math.ceil(math.sqrt(len(other_apis)))
            random_other_apis = random.sample(other_apis, min(sqrt_number_other, len(other_apis) ))#为了提高平衡性
            joined_apis = random_other_apis
        else:
            if len(filtered_apis) > 3:
                sqrt_number_api = math.floor(math.sqrt(len(filtered_apis)))
                random_filtered_apis = random.sample(filtered_apis, min(sqrt_number_api, len(filtered_apis)))
            elif filtered_apis:
                random_filtered_apis = filtered_apis
            else:
                random_filtered_apis = []
            joined_apis = other_apis + random_filtered_apis

        if len(joined_apis) > 7 :
            sqrt_number = math.ceil(math.sqrt(len(joined_apis)))
            random_apis = random.sample(joined_apis, min(sqrt_number,len(joined_apis)))
            joined_apis = '" && "'.join(random_apis)
        else:
            joined_apis = '" && "'.join(joined_apis)
    classes = set(get_text_css_class(s)).intersection(get_all_css_classes(url, s))
    if len(classes) > 0:
        classes = sorted(classes)
        if len(classes) > 9:
            sqrt_number_classes = math.ceil(math.sqrt(len(classes)))
            random_classes = random.sample(classes, min(sqrt_number_classes, len(classes)))
            joined_classes = '" && "'.join(random_classes)
        else:
            joined_classes = '" && "'.join(classes)
    else:
        print("没有找到共同的类名。")
        joined_classes = ''
    if joined_classes and joined_apis and icon_hash:
        fingerprint = '("' + joined_apis + '") || ("' + joined_classes + '") || (' + icon_hash + ')'
    elif joined_classes:
        fingerprint = '"' + joined_classes + '"'
    elif joined_apis:
        fingerprint = '"' + joined_apis + '"'
    else:
        fingerprint =  + icon_hash
    powerby_str = get_power(s)
    if powerby_str:
        fingerprint = '( ' + fingerprint + ' )' + ' && "' + powerby_str + '"'
    if param:
        fingerprint = '( ' + fingerprint + ' )' + ' && "' + param + '"'
    print('Url\n' + url)
    print('构造的指纹如下\n' + fingerprint)
    if execute_fofa:
        results = fofa(base64.b64encode(fingerprint.encode()).decode())
        result_data = results.get('results', [])
        size_value = results.get('size', 0)  # 获取size值
        if output_file:
            filetype = output_file.split('.')[-1]
            save_to_file(result_data, output_file, filetype, size_value,url,fingerprint)
        else:
            print(f"通过Fofa共搜索出{size_value}条数据")
            for item in result_data:
                print(item)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="依据css类 Api等来发现网站指纹,通过Fofa寻找同源码网站,使用Fofa查询之前要在json文件中添加Fofa key")
    parser.add_argument('-u', '--url', type=str, required=False, metavar='', help='网站Url')
    parser.add_argument('-p', '--param', type=str, required=False, metavar='',
                        help='输入要添加的参数,不要带问号、双引号这些特殊字符,要不然Fofa搜索时会报错的')
    parser.add_argument('-f', '--fofa', action='store_true', help='是否执行Fofa搜索,不带-f选项只会输出框架指纹')
    parser.add_argument('-o', '--output', type=str, required=False, metavar='', help='输出文件名,可以是txt或xlsx格式')
    parser.add_argument('-r', '--readfile', type=str, required=False, metavar='', help='从txt文件中读取URL')

    args = parser.parse_args()
    if args.output:
        valid_formats = ['.txt', '.xlsx']
        file_format = '.' + args.output.split('.')[-1].lower()
        if file_format not in valid_formats:
            print("输出文件格式必须是txt或xlsx")
            exit()
    if args.output:
        if os.path.exists(args.output):
            if args.output.endswith('.xlsx'):
                wb = Workbook()
                wb.save(args.output)
            else:
                with open(args.output, 'w') as file:
                    pass  # 创建空文件
    main(args.url, args.param, args.output, args.fofa, args.readfile)

