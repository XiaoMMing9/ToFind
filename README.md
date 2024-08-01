# ToFind
同源码网站收集工具
发现网站特征指纹，通过Fofa搜寻同源网站

## 摘要

这是一个发现网站指纹的工具，依据css、Api等来发现网站指纹，调用Fofa Api搜索同源网站

## 更新日志

### 版本更新(2024/8/1)

v2.0.2

增加根据获取到的ico的url计算ico的hash值的功能

### 版本更新(2024/7/27)

v2.0.1

更新获取`api`逻辑，排除`jquery.js`、`bootstrap.css`等引用的`api`接口

降低指纹中`.css`、`.js`、`.png`、`.jpg`、`.ico`的`api`占比，放大`.html`、`.php`接口的比例

### 版本更新(2024/7/16)

v2.0.0

支持任意`url`，附加`http`、`https`协议，支持批量读取url，修复xlsx导出功能

## 使用方式

### 0x01

通过`requests.txt`文件下载`python3`模板包

```bash
pip install -r requests.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

![image-20240713104509957](images/同源码网站收集工具/image-20240713104509957.png)

### 0x02

配置`config.json`文件设置`Fofa key`

![image-20240713105007932](images/同源码网站收集工具/image-20240713105007932.png)

### 0x03

![image-20240713105831167](images/同源码网站收集工具/image-20240713105831167.png)

用法

```bash
python ToFind.py -u http://localhost:4000/                       (提取本地4000端口web服务的网站指纹)        
python ToFind.py -u http://localhost:4000/ -p hexo               (提取web网站指纹并且附加参数“hexo”，如果提取的指纹为“/login”，最后的指纹为 "/login" && "hexo")
python ToFind.py -u http://localhost:4000/ -f                    (输出网站指纹，并且使用Fofa查询同源的网站并显示在命令行中)
python ToFind.py -u http://localhost:4000/ -f -o 1.txt           (输出网站指纹，使用Fofa查询同源的网站将其保存在1.txt文件中)
python ToFind.py -u http://localhost:4000/ -f -o 1.xlsx          (输出网站指纹，使用Fofa查询同源的网站将其保存在1.xlsx文件中)
python ToFind.py -r 1.txt -f -o out.xlsx                         (批量读取1.txt中的url通过Fofa搜索数据导出至out.xlsx)
```

批量测试：

![image-20240716095456086](images/同源码网站收集工具/image-20240716095456086.png)

![image-20240716102017407](images/同源码网站收集工具/image-20240716102017407.png)

结果图

![image-20240716102159147](images/同源码网站收集工具/image-20240716102159147.png)

![image-20240716102346780](images/同源码网站收集工具/image-20240716102346780.png)

![image-20240716102303040](images/同源码网站收集工具/image-20240716102303040.png)

## 同源测试

### 0x01

```bash
https://jwxt.lcu.edu.cn/jwglxt/xtgl/login_slogin.html
```

![image-20240713110853527](images/同源码网站收集工具/image-20240713110853527.png)

```bash
python3 ToFind.py -u https://jwxt.lcu.edu.cn/jwglxt/xtgl/login_slogin.html -f | more
```

![image-20240713111154485](images/同源码网站收集工具/image-20240713111154485.png)

![image-20240713111301822](images/同源码网站收集工具/image-20240713111301822.png)

![image-20240713111308158](images/同源码网站收集工具/image-20240713111308158.png)
### 0x02

```bash
http://speak13.com:81/
```

![image-20240713111739290](images/同源码网站收集工具/image-20240713111739290.png)

```bash
python3 ToFind.py -u http://speak13.com:81/ -f | more
```

![image-20240713111814174](images/同源码网站收集工具/image-20240713111814174.png)

![image-20240713111935578](images/同源码网站收集工具/image-20240713111935578.png)

![image-20240713111959722](images/同源码网站收集工具/image-20240713111959722.png)

### 0x03

(hexo)

![image-20240713114435230](images/同源码网站收集工具/image-20240713114435230.png)

```bash
python3 ToFind.py -u http://192.168.1.3/ -f | more
```

![image-20240713114638317](images/同源码网站收集工具/image-20240713114638317.png)

![image-20240713114603431](images/同源码网站收集工具/image-20240713114603431.png)

![image-20240713114700558](images/同源码网站收集工具/image-20240713114700558.png)

## 末尾

如有侵权请联系我删除
