import sys
text = sys.stdin.read()
print(text[::-1], flush=True)
sys.exit(0)