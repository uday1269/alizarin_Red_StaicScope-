import subprocess

res = subprocess.run(["sc", "query", "type=", "service", "state=", "all"], capture_output=True, text=True)
for block in res.stdout.split("\n\n"):
    if "mysql" in block.lower() or "mariadb" in block.lower():
        print(block)
