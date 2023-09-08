import random
import string

def generate_auth_key():
    key_length = 32
    key_characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    auth_key = "".join(random.choice(key_characters) for _ in range(key_length))
    return auth_key

if __name__ == "__main__":
    auth_key = generate_auth_key()
    print(auth_key)