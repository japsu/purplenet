
from random import choice
import string

def generate_random_string(length=16, chars=string.lowercase + string.digits):
    return ''.join([choice(chars) for i in range(length)])
