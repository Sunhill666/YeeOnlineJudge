import random


def get_random_string(mode="mixDigitLetter", length=16):
    # 按照不同模式生成随机字符串
    upper_letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower_letter = "abcdefghigklmnopqrstuvwxyz"
    digits = "0123456789"
    special_characters = "!@#$%&_-.+="
    random_map = {"digit": digits, "upper": upper_letter, "lower": lower_letter,
                 "mixDigitLetter": upper_letter + lower_letter + digits, "mixLetter": upper_letter + lower_letter,
                 "mixDigitLetterCharcter": upper_letter + lower_letter + digits + special_characters}
    return get_random(random_map[mode], length)


def get_random(random_list, length=16):
    """
    生成一个指定长度的随机字符串
    """
    str_list = [random.choice(random_list) for i in range(length)]
    random_str = ''.join(str_list)
    return random_str
