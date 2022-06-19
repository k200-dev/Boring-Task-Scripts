import os


def start(name, scriptname, dir):
    os.chdir(dir)
    os.system(f"pm2 start {scriptname} --time --name {name} ")
    print(f"[+] Started {name} ")


names = []
scriptnames = []
dirs = []

for x in range(len(names)):
    start(names[x - 1], scriptnames[x - 1], dirs[x - 1])
