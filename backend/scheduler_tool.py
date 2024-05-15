# schedule_tool.py
import subprocess
import schedule
import time
import sys


def start_program(cmd):
    return subprocess.Popen(cmd, shell=True)


def check_and_restart(cmd, processes):
    if processes[cmd].poll() is not None:
        print(f"程序 {cmd} 已終止，正在重新啟動...")
        processes[cmd] = start_program(cmd)
    else:
        print(f"程序 {cmd} 仍在運行。")


# 假設命令行參數列出了所有需要啟動和監控的程序
commands = sys.argv[1:]

processes = {cmd: start_program(cmd) for cmd in commands}

for cmd in commands:
    schedule.every(10).seconds.do(check_and_restart, cmd, processes)

while True:
    schedule.run_pending()
    time.sleep(1)
