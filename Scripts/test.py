import subprocess

proc = subprocess.Popen(["nslookup", "-q=aaaa", "reddit.com"], stdout=subprocess.PIPE, bufsize=1)

print("\nBELOW\n")

# print (str(proc.communicate())[2:-1])