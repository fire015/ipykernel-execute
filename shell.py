# pip install ipykernel
# Source from https://github.com/ipython/ipykernel/blob/master/ipykernel/tests/test_kernel.py

from jupyter_client import manager
from subprocess import STDOUT
from time import time
import os

STARTUP_TIMEOUT = 60
TIMEOUT = 60

os.environ["JUPYTER_PATH"] = os.getcwd()

def start_new_kernel(**kwargs):
    #kwargs['stderr'] = STDOUT
    #kwargs['stdout'] = STDOUT

    return manager.start_new_kernel(startup_timeout=STARTUP_TIMEOUT, kernel_name="rms", **kwargs)

def get_reply(kc, msg_id, timeout=TIMEOUT, channel='shell'):
    t0 = time()
    while True:
        get_msg = getattr(kc, f'get_{channel}_msg')
        reply = get_msg(timeout=timeout)
        if reply['parent_header']['msg_id'] == msg_id:
            break
        # Allow debugging ignored replies
        print(f"Ignoring reply not to {msg_id}: {reply}")
        t1 = time()
        timeout -= t1 - t0
        t0 = t1
    return reply

def assemble_output(get_msg):
    """assemble stdout/err from an execution"""
    stdout = ''
    stderr = ''
    while True:
        msg = get_msg(timeout=1)
        msg_type = msg['msg_type']
        content = msg['content']
        if msg_type == 'status' and content['execution_state'] == 'idle':
            # idle message signals end of output
            break
        elif msg['msg_type'] == 'stream':
            if content['name'] == 'stdout':
                stdout += content['text']
            elif content['name'] == 'stderr':
                stderr += content['text']
            else:
                raise KeyError("bad stream: %r" % content['name'])
        else:
            # other output, ignored
            pass
    return stdout, stderr

def execute(code='', kc=None, **kwargs):
    msg_id = kc.execute(code=code, **kwargs)
    reply = get_reply(kc, msg_id, TIMEOUT)

    return msg_id, reply['content']




# with open('test.py') as f:
#     code = f.read()

km, kc = start_new_kernel()
msg_id, content = execute(code="from flask import Flask", kc=kc)
stdout, stderr = assemble_output(kc.get_iopub_msg)
print(content)
#print(stdout)
msg_id, content = execute(code="app = Flask('test'); print(app)", kc=kc)
stdout, stderr = assemble_output(kc.get_iopub_msg)
print(content)
print(stdout)
kc.stop_channels()
km.shutdown_kernel(now=True)