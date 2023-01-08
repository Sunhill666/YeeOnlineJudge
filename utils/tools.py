import random
from zipfile import ZipFile

from organization.models import User


def get_random_string(mode="mixDigitLetter", length=16):
    # 按照不同模式生成随机字符串
    upper_letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower_letter = "abcdefghigklmnopqrstuvwxyz"
    digits = "0123456789"
    special_characters = "@_-.+"
    random_map = {"digit": digits, "upper": upper_letter, "lower": lower_letter,
                  "mixDigitLetter": upper_letter + lower_letter + digits, "mixLetter": upper_letter + lower_letter,
                  "mixDigitLetterCharacter": upper_letter + lower_letter + digits + special_characters}
    return get_random(random_map[mode], length)


def get_random(random_list, length=16):
    """
    生成一个指定长度的随机字符串
    """
    str_list = [random.choice(random_list) for i in range(length)]
    random_str = ''.join(str_list)
    return random_str


def get_available_username(prefix, suffix, length):
    username_list = list()
    for i in range(length):
        ok = True
        while ok:
            if prefix and suffix:
                left_len = 13 - 2 - len(prefix) - len(suffix)
                username = "{prefix}_{name}_{suffix}".format(
                    prefix=prefix,
                    name=get_random_string(mode="mixDigitLetterCharacter", length=left_len),
                    suffix=suffix
                )
            elif prefix:
                left_len = 13 - 1 - len(prefix)
                username = "{prefix}_{name}".format(
                    prefix=prefix,
                    name=get_random_string(mode="mixDigitLetterCharacter", length=left_len)
                )
            elif suffix:
                left_len = 13 - 1 - len(suffix)
                username = "{name}_{suffix}".format(
                    name=get_random_string(mode="mixDigitLetterCharacter", length=left_len),
                    suffix=prefix
                )
            else:
                left_len = 13
                username = "{name}".format(
                    name=get_random_string(mode="mixDigitLetterCharacter", length=left_len)
                )
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                username_list.append(username)
                ok = False
    return username_list


def read_test_case(test_case):
    with ZipFile(test_case) as f:
        namelist = f.namelist()
        input_list = []
        output_list = []
        for name in namelist:
            if name.split('.')[1] == 'in':
                with f.open(name) as fin:
                    input_list.append(str(fin.read(), 'utf-8'))
            elif name.split('.')[1] == 'out':
                with f.open(name) as fot:
                    output_list.append(str(fot.read(), 'utf-8'))
            else:
                return None
    return input_list, output_list
