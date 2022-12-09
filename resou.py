import requests
import json
import re

import hoshino
from hoshino import Service
from hoshino.typing import CQEvent

sv = Service(
    name="resou",  # 功能名
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="工具",  # 分组归类
    help_='''[微博/百度/知乎/贴吧热搜] (+数字)获取热搜榜(不加数字默认前10位)
[百度百科] +关键词''',  # 帮助说明

)


def render_forward_msg(msg_list: list, uid=2854196306, name='小冰'):
	forward_msg = []
	for msg in msg_list:
		forward_msg.append({
			"type": "node",
			"data": {
				"name": str(name),
				"uin": str(uid),
				"content": msg
			}
		})
	return forward_msg


@sv.on_prefix('微博热搜')
async def weiboresou(bot, ev: CQEvent):
    groupid = ev.group_id
    content = ev.message.extract_plain_text()
    if content.isdigit():
        cnt = min(int(content), 50)
    else:
        if content == '':
            cnt = 10
        else:
            return
    await bot.send(ev,'获取中')
    url = 'https://weibo.com/ajax/side/hotSearch'
    srcurl = "https://s.weibo.com/weibo?q="
    res = requests.get(url)
    r = res.json()["data"]["realtime"][:cnt]
    msg_list = ['微博热搜榜']
    for i,obj in enumerate(r):
        code = str(obj["word"].encode('utf-8'))[2:-1]
        code = code.replace('\\x','%')
        url = srcurl+code
        result = '%d、%s\nhot:%d\n链接:%s'%(i+1,obj["word"],obj["num"],url)
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list)
    await bot.send_group_forward_msg(group_id=groupid, messages=forward_msg)


@sv.on_prefix('百度热搜')
async def baiduresou(bot, ev: CQEvent):
    groupid = ev.group_id
    content = ev.message.extract_plain_text()
    if content.isdigit():
        cnt = min(int(content), 30)
    else:
        if content == '':
            cnt = 10
        else:
            return
    await bot.send(ev,'获取中')
    url='https://top.baidu.com/board?tab=realtime'
    res=requests.get(url)
    r=res.text
    data = re.search('(<!--s-data:)({.+})(-->)', r)
    r=json.loads(data.groups()[1])["data"]["cards"][0]["content"][:cnt]
    msg_list = ['百度热搜榜']
    for i,obj in enumerate(r):
        result = '%d、%s\nhot:%s\n链接:%s'%(i+1,obj["desc"],obj["hotScore"],obj["appUrl"])
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list)
    await bot.send_group_forward_msg(group_id=groupid, messages=forward_msg)


@sv.on_prefix('知乎热搜')
async def zhiresou(bot, ev: CQEvent):
    groupid = ev.group_id
    content = ev.message.extract_plain_text()
    if content.isdigit():
        cnt = min(int(content), 50)
    else:
        if content == '':
            cnt = 10
        else:
            return
    await bot.send(ev,'获取中')
    url='https://www.zhihu.com/billboard'
    res=requests.get(url)
    r=res.text
    data = re.search('("hotList":\\[{)(.+?)(}\\])', r)
    data=data.groups()[1]
    msg_list=["知乎热搜榜"]
    for i,obj in enumerate(data.split('},{')[:cnt]):
        dic=json.loads("{"+obj+"}")["target"]
        result = '%d、%s\nhot:%s\n链接:%s'%(i+1,dic["titleArea"]["text"],dic["metricsArea"]["text"],dic["link"]["url"])
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list)
    await bot.send_group_forward_msg(group_id=groupid, messages=forward_msg)


@sv.on_prefix('贴吧热搜')
async def tiebaresou(bot, ev: CQEvent):
    groupid = ev.group_id
    content = ev.message.extract_plain_text()
    if content.isdigit():
        cnt = min(int(content), 30)
    else:
        if content == '':
            cnt = 10
        else:
            return
    await bot.send(ev,'获取中')
    url='https://tieba.baidu.com/hottopic/browse/topicList'
    res=requests.get(url)
    r=res.json()["data"]["bang_topic"]["topic_list"][:cnt]
    msg_list = ['贴吧热议榜']
    for i,obj in enumerate(r):
        result = '%d、%s\nhot:%d\n链接:%s'%(i+1,obj["topic_name"],obj["discuss_num"],obj["topic_url"])
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list)
    await bot.send_group_forward_msg(group_id=groupid, messages=forward_msg)


#下载网页内容
def download(url):
    if url is None:
        return None
    # 浏览器请求头
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
    headers={'User-Agent':user_agent}
    r = requests.get(url,headers=headers)
    if r.status_code == 200:
        r.encoding = 'utf-8'
        return r.text
    return None


#提取百科词条简介
def get_data(html):
    #regex = re.compile('<meta name="description" content="(.*?)">')
    regex = re.compile('<div class="lemma-summary" label-module="lemmaSummary">(\s*)<div class="para" label-module="para">([\s\S]*?)</div>(\s*)</div>')
    data = re.findall(regex, html)[0][1]
    return data


@sv.on_prefix('百度百科')
async def baikedataget(bot, ev: CQEvent):
    keyword = ev.message.extract_plain_text()
    if keyword=='':
        return
    url = 'http://baike.baidu.com/item/{}'.format(keyword)
    html_cont = download(url)
    try:
        data = get_data(html_cont)
        data = re.sub(r'<([\s\S]*?)>|&nbsp;|\n','',data)
        await bot.send(ev,data,at_sender=True)
    except Exception as e:
        await bot.send(ev,f'词条“{keyword}”不存在',at_sender=True) 
