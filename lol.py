import string, sys, random

sys.stdout.write(''.join(random.choices(string.ascii_letters,k=10)))