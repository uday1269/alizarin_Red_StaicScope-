import subprocess

res = subprocess.run(["wmic", "process", "where", "name='mysqld.exe'", "get", "ProcessId,CommandLine,ExecutablePath"], capture_output=True, text=True)
print(res.stdout)
