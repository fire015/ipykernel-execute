# ipykernel-execute

Execute code through ipykernel in python. See `shell.py` for example.

## Custom kernel

To create the `rms` kernel...

```
python -m venv rms-kernel
source rms-kernel/bin/activate
pip install ipykernel Flask
```