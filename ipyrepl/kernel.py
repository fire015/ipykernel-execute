# Source adapted from https://github.com/ipython/ipykernel/blob/master/ipykernel/tests/test_kernel.py

from jupyter_client import manager
from queue import Empty
from time import time
from contextlib import contextmanager
import atexit

STARTUP_TIMEOUT = 60
TIMEOUT = 60

KM = None
KC = None


def start_new_kernel(**kwargs):
    """start a new kernel, and return its Manager and Client"""
    return manager.start_new_kernel(startup_timeout=STARTUP_TIMEOUT, **kwargs)


def flush_channels(kc=None):
    """flush any messages waiting on the queue"""
    if kc is None:
        kc = KC
    for get_msg in (kc.get_shell_msg, kc.get_iopub_msg):
        while True:
            try:
                msg = get_msg(timeout=0.1)
            except Empty:
                break


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


def execute(code='', kc=None, **kwargs):
    """wrapper for doing common steps for validating an execution request"""
    if kc is None:
        kc = KC
    msg_id = kc.execute(code=code, **kwargs)
    reply = get_reply(kc, msg_id, TIMEOUT)

    return msg_id, reply['content']


def start_global_kernel(kernel_name):
    """start the global kernel (if it isn't running) and return its client"""
    global KM, KC
    if KM is None:
        KM, KC = start_new_kernel(kernel_name=kernel_name)
        atexit.register(stop_global_kernel)
    else:
        flush_channels(KC)
    return KC


@contextmanager
def get_kernel(kernel_name='python'):
    """Context manager for the global kernel instance
    Returns
    -------
    kernel_client: connected KernelClient instance
    """
    yield start_global_kernel(kernel_name)


def stop_global_kernel():
    """Stop the global shared kernel instance, if it exists"""
    global KM, KC
    KC.stop_channels()
    KC = None
    if KM is None:
        return
    KM.shutdown_kernel(now=True)
    KM = None


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
