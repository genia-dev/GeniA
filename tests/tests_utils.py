import random
import string


# k8s namespace regex: [a-z0-9]([-a-z0-9]*[a-z0-9])?
def generate_namespace():
    chars = string.ascii_lowercase + string.digits
    middle_chars = chars + "-"
    length = random.randint(10, 16)

    start_char = random.choice(chars)
    start_char = "e2e-tests-" + start_char
    if length > 0:
        middle = "".join(random.choice(middle_chars) for _ in range(length - 1))
        end_char = random.choice(chars)
        return start_char + middle + end_char
    else:
        return start_char


def generate_random_string(length=10):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


# trick to bypass pytest capture the stdout & stderr
def bypass_pytest_print(message):
    with open("/dev/fd/1", "w") as f:
        print(message, file=f)
    raise ValueError
