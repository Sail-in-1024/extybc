"""
一个简单的 REPL 实现。

你可以像 Python REPL 或 IDLE 那样直接输入代码，按回车运行。

适用于猿编程的Skulpt环境。
"""

# 导入 Skulpt 扩展
import platform
if platform.python_implementation() == 'Skulpt':
    import extybc
import sys
from types import SimpleNamespace


extybc._init()

sys.ps1 = '>>> '
sys.ps2 = '... '

def error_handler(exc: Exception):
    print(type(exc).__qualname__ + ': ' + str(exc))

def exec_handler(source):
    try:
        exec(_repl_info_.expression)
    except Exception as exec_exc:
        error_handler(exec_exc)

_repl_info_ = SimpleNamespace(
                                extybc = extybc,
                                sys = sys,
                                expression = None,
                                )

print()
print('Python', sys.version, 'on ybc')
print('Type "help", "copyright", "credits" or "license" for more information.')

del platform
del extybc
del sys
del SimpleNamespace

while True:
    _repl_info_.expression = input(_repl_info_.sys.ps1)
    if _repl_info_.expression.rstrip().endswith(':'):
        while True:
            addition = input(_repl_info_.sys.ps2)
            _repl_info_.expression += '\n' + addition
            if not addition.startswith(('\t', ' ')) and not addition.rstrip().endswith((':', '(', '[', '{', '\\')):
                break
        del addition
        exec_handler(_repl_info_.expression)
    else:
        try:
            result = eval(_repl_info_.expression)
        except SyntaxError:
            exec_handler(_repl_info_.expression)
        except Exception as e:
            error_handler(e)
            del e
        except SystemExit as e:
            exit_code = None
            if hasattr(e, 'code'):
                exit_code = e.code
            if exit_code is None:
                exit_code = 0
            print(f'Progress finished with exit code {exit_code}.')
            break
        else:
            _repl_info_.sys.displayhook(result)
