import cl_bd
import dl_mode
import psutil
import ctypes
import sys

#sys.stdout = open('info.log', 'w')
#sys.stderr = open('error.log', 'w')

# def check_program_running():
#     current_process = psutil.Process()
#     print(current_process.pid, current_process.name())
#     for process in psutil.process_iter():
#         print(process.pid, process.name())
#         if process.pid != current_process.pid and process.name() == current_process.name():
#             return True
#     return False
#不管了毁灭吧，注意别手贱点好几次就行。。。。。



#if check_program_running():
if False:
    print("Program is already running. Exiting...")
    ctypes.windll.user32.MessageBoxW(0, "进程已启动", "BilibiliAudioDownloader", 0x10)
    exit()
else:
    dl_mode.chackFFMPEG()
    cl_bd.check_clipboard


