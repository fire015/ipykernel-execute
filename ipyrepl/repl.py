import os
from . import kernel


KERNEL_NAME = os.getenv('KERNEL_NAME', 'python')


def execute(code):
    with kernel.get_kernel(KERNEL_NAME) as kc:
        msg_id, content = kernel.execute(kc=kc, code=code)
        stdout, stderr = kernel.assemble_output(kc.get_iopub_msg)

    return content, stdout
