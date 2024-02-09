import clipboard
import dl_mode
import re
import threading

def check_clipboard():
    previous_content = clipboard.paste()
    
    while True:
        current_content = clipboard.paste()
        
        if current_content != previous_content:
            dw(current_content)  # 调用dw函数
            
        previous_content = current_content

# 在这里定义dw函数
def dw(content):
    print("当前剪贴板内容：",content)
    if check_url(content):
        print("检测到B站链接")
        threading.Thread(target=dl_mode.main, args=(content,)).start()
    elif content == "exit":
        exit(0)


def check_url(content):
    pattern = r"https://www.bilibili.com/video/(\w+)/"
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    else:
        return None

if __name__ == "__main__":
    dl_mode.chackFFMPEG()
    check_clipboard()