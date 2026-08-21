import subprocess

output = subprocess.check_output('tasklist /FI "IMAGENAME eq mysqld.exe"', shell=True).decode()
print("Tasklist for mysqld.exe:\n", output)
