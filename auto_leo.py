#!/usr/bin/env python3
"""
通过 pexpect 驱动 leo_or_chain_main.py 的交互菜单，用于实验脚本自动化。
所有容器的 create/start/position_update/remove 均通过 leo_or_chain_main 完成。
用法:
  sudo ./myenv/bin/python auto_leo.py setup   # yes -> create -> start -> position_update -> no
  sudo ./myenv/bin/python auto_leo.py teardown # no -> remove -> no
"""
import os
import sys
import pexpect

# PyInquirer list 选项用方向键选择：Enter=选第一项，Down+Enter=选第二项，以此类推
ARROW_DOWN = "\x1b[B"
ENTER = "\r"

def select_list_index(child, index):
    """在 list 中选中第 index 项（0-based），然后 Enter 确认。"""
    for _ in range(index):
        child.send(ARROW_DOWN)
    child.send(ENTER)

def run_setup(child):
    """流程: yes(重生成配置) -> create -> yes -> start -> yes -> position_update -> no(退出)"""
    # 1. Whether to regenerate...
    # choices: ["yes", "no"] -> yes = index 0
    child.expect(["regenerate", "Whether", "configuration"], timeout=30)
    select_list_index(child, 0)  # yes

    # 2. What is the command of your created block chain? -> create
    # choices: create, start, stop, remove, inspect, delete_logs, position_update
    child.expect(["command", "block chain", "created"], timeout=60)
    select_list_index(child, 0)  # create

    # 3. Continue the program? -> yes
    child.expect(["Continue", "program"], timeout=600)  # create 可能很久
    select_list_index(child, 0)  # yes

    # 4. What is the command? -> start
    child.expect(["command", "block chain", "created"], timeout=30)
    select_list_index(child, 1)  # start

    # 5. Continue the program? -> yes
    child.expect(["Continue", "program"], timeout=600)  # start 可能很久
    select_list_index(child, 0)  # yes

    # 6. What is the command? -> position_update (第 7 项，index 6)
    child.expect(["command", "block chain", "created"], timeout=30)
    select_list_index(child, 6)  # position_update

    # 7. Continue the program? -> no (退出)
    child.expect(["Continue", "program"], timeout=30)
    select_list_index(child, 1)  # no

    child.expect(pexpect.EOF, timeout=10)

def run_teardown(child):
    """流程: no(不重生成) -> remove -> no(退出)"""
    # 1. Whether to regenerate...
    child.expect(["regenerate", "Whether", "configuration"], timeout=30)
    select_list_index(child, 1)  # no

    # 2. What is the command? -> remove (第 4 项，index 3)
    child.expect(["command", "block chain", "created"], timeout=30)
    select_list_index(child, 3)  # remove

    # 3. Continue the program? -> no
    child.expect(["Continue", "program"], timeout=300)
    select_list_index(child, 1)  # no

    child.expect(pexpect.EOF, timeout=30)

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("setup", "teardown"):
        print("Usage: auto_leo.py setup | teardown", file=sys.stderr)
        sys.exit(1)
    mode = sys.argv[1]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    cmd = "leo_or_chain_main.py"
    if os.path.exists("myenv/bin/python"):
        cmd = "./myenv/bin/python " + cmd
    else:
        cmd = sys.executable + " " + cmd
    full_cmd = "sudo " + cmd if os.geteuid() != 0 else cmd

    child = pexpect.spawn(full_cmd, encoding="utf-8", timeout=600)
    child.logfile = sys.stdout

    try:
        if mode == "setup":
            run_setup(child)
        else:
            run_teardown(child)
    except pexpect.TIMEOUT:
        print("auto_leo.py: timeout", file=sys.stderr)
        sys.exit(2)
    except pexpect.EOF:
        pass
    finally:
        child.close()
    sys.exit(child.exitstatus if child.exitstatus is not None else 0)

if __name__ == "__main__":
    main()
