import os
import re
import json
import time
import eyed3
import requests
import colorama
from time import sleep
from colorama import Fore, Back, Style
from eyed3.id3.frames import ImageFrame

colorama.init(autoreset=True)
PROXY=""
PROXY_USED_TIMES=0

rate="128k"
REMOVE_ORIGINAL=True
USE_PROXY=False
GLOBE_SLEEP_TIME=60*5

Headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "origin": "https://www.bilibili.com/",
        "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        "cache-control":"max-age=0"
    }

def getPathTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]" # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title) # 替换为下划线
    return new_title

def mkdir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

###bilibili aid and bvid convert model start###
table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF' # 码表
tr = {} # 反查码表
# 初始化反查码表
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6] # 位置编码表
XOR = 177451812 # 固定异或值
ADD = 8728348608 # 固定加法值

def toAid(x):
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58 ** i
    return (r - ADD) ^ XOR

def toBvid(x):
	x=(x^XOR)+ADD
	r=list('BV1  4 1 7  ')
	for i in range(6):
		r[s[i]]=table[x//58**i%58]
	return ''.join(r)
###bilibili aid and bvid convert model end###

def toLrcTime(time):
    m, s = divmod(time, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d.%02d" % (m, s, h)

def manage_bili_json_to_lrc(json_str):
    json_str = json.loads(json_str)["body"]
    lrc = ""
    for i in json_str:
        lrc += "[" + str(toLrcTime(i["from"])) + "]" + i["content"] + "\n"
    return lrc

def chackFFMPEG():
    if os.system("ffmpeg -version") != 0:
        print(Back.RED +"Error: ", "ffmpeg not found,装个ffmpeg呗~~~")
        exit(1)

def toMp3(file_path):
    if file_path.endswith(".m4a"):
        os.system("ffmpeg -i " + '"' + file_path + '"' +" -ab "+rate+" -f mp3 -acodec libmp3lame -y " + '"' + file_path[:-4] + '"' + ".mp3")
        if REMOVE_ORIGINAL:
            try:
                os.remove(file_path)
            except:
                pass
        return file_path[:-4] + ".mp3"
    else:
        return file_path

def get_proxy():
    return requests.get("http://demo.spiderpy.cn/get/?type=https").json()

def getUntillSuccess(URL, Headers):
    global PROXY
    global PROXY_USED_TIMES
    if USE_PROXY:
        if PROXY != "" and PROXY_USED_TIMES <= 10:
            pass
        else:
            PROXY = get_proxy().get("proxy")
            PROXY_USED_TIMES = 0
        while True:
            try:
                PROXY_USED_TIMES += 1
                res = requests.get(URL, headers=Headers, proxies={"https": PROXY},).text
                if json.loads(res)["code"] == 0:
                    return res
            except:
                PROXY = get_proxy().get("proxy")
                PROXY_USED_TIMES = 0
    else:
        while True:
            try:
                res = requests.get(URL, headers=Headers).text
                try:
                    json.loads(res)["code"]
                except:
                    return res
                if json.loads(res)["code"] == 0:
                    return res
                else:
                    print(Back.RED + "Error: ", res)
                    sleep(GLOBE_SLEEP_TIME)
            except Exception as e:
                print(Back.RED + "Error: ", "网络错误，检查网络环境","\n",e)
                exit(1)

def downloadAudio(URL,Headers,local_filename):
    if os.path.exists(local_filename):
        return
    response = requests.get(URL,headers=Headers)
    with open(local_filename, 'wb') as f:
        f.write(response.content)

def rename(file_path, cidArry ,res , globe_title, title,cidList):
    mkdir("img_cache")
    if not os.path.exists("./img_cache/"+str(res["data"]["aid"])+"_cover.jpg"):
        downloadAudio(res["data"]["pic"], Headers, "./img_cache/"+str(res["data"]["aid"])+"_cover.jpg")
    sub_lrc = manage_bili_json_to_lrc(getUntillSuccess("https:" + cidArry["BAD_sub_url"], Headers))
    with open("./"+globe_title + "/" + getPathTitle(title) +".lrc", "w", encoding="utf-8") as f:
        f.write(sub_lrc)
    audiofile = eyed3.load(file_path)
    tupTime=time.localtime(res["data"]["ctime"])#以实际做后更改时间为准，不是pubdate
    dateToTag=time.strftime("%Y-%m-%d", tupTime)
    audiofile.tag.release_date = dateToTag
    if cidArry["part"] == "" or len(cidList) == 1:
        audiofile.tag.title = res["data"]["title"]
    else:
        audiofile.tag.title =cidArry["part"] + res["data"]["title"]
    audiofile.tag.artist = res["data"]["owner"]["name"]+" - "+str(res["data"]["owner"]["mid"])
    audiofile.tag.album = res["data"]["bvid"]
    audiofile.tag.images.set(ImageFrame.FRONT_COVER, open('./img_cache/'+str(res["data"]["aid"])+'_cover.jpg','rb').read(), 'image/jpeg')
    audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
    print(Back.GREEN +"写入metadata成功" ,res['data']["title"],"\n"*2)

def main(URL):
    if URL.find("bv") != -1 or URL.find("BV") != -1 or URL.find("Bv") != -1 or URL.find("bV") != -1 :
        bvid = re.search(r'/BV(\w+)/*', URL , re.IGNORECASE).group(1)
        bvid = "BV" + bvid
        aid = toAid(bvid)
    else:
        aid = re.search(r'/av(\d+)/*', URL , re.IGNORECASE).group(1)
        #bvid=toBvid(aid)
    print(Back.GREEN + "Info: ", "aid is : ", aid)
    res=json.loads(getUntillSuccess("https://api.bilibili.com/x/web-interface/view?aid={aid}".format(aid=aid), Headers))
    cidList = res["data"]["pages"]
    globe_title = res["data"]["title"]
    globe_title=getPathTitle(globe_title)
    mkdir(globe_title)
    for idx,cidArry in enumerate(cidList):
        cid=cidArry["cid"]
        title=cidArry["part"]
        video_api_link="https://api.bilibili.com/x/player/playurl?avid={avid}&cid={cid}&fnval=80"
        video_resp_txt = getUntillSuccess(video_api_link.format(avid=aid,cid=cid), Headers)
        video_resp_obj=json.loads(video_resp_txt)
        audio_url=video_resp_obj["data"]["dash"]["audio"][-1]["baseUrl"]
        # 质量控制见上一行
        cidArry["BAD_sub_url"]=json.loads(getUntillSuccess("https://api.bilibili.com/x/player/v2?aid={aid}&cid={cid}".format(aid=aid,cid=cid),Headers))["data"]["subtitle"]["subtitles"][0]["subtitle_url"]
        if title == "":
            title = res["data"]["title"]+" -p" + str(idx+1)      
        print(Back.GREEN + "Info: ", "Downloading: ", title)
        downloadAudio(audio_url, Headers, "./"+globe_title + "/" + getPathTitle(title) + ".m4a")
        print(Back.GREEN + "Info: ", "Downloaded: ", title)
        toMp3(file_path="./"+globe_title + "/" + getPathTitle(title) + ".m4a")
        if REMOVE_ORIGINAL:
            try:
                os.remove("./"+globe_title + "/" + getPathTitle(title) + ".m4a")
            except:
                pass
        rename("./"+globe_title + "/" + getPathTitle(title) + ".mp3",cidArry,res,globe_title,title,cidList)

if __name__ == "__main__":
    chackFFMPEG()
    main(input("video url:"))
    #main("https://www.bilibili.com/video/av106")