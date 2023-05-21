import random
import re
from zipfile import ZipFile

from django.db.models import Q

from utils.judger.judgeclient import JudgeClient

TEMPLATE_BASE = """//PREPEND BEGIN
{prepend}
//PREPEND END
//TEMPLATE BEGIN
{template}
//TEMPLATE END
//APPEND BEGIN
{append}
//APPEND END"""

PREPEND_PATTERN = r"//PREPEND BEGIN\n([\s\S]+?)//PREPEND END"
TEMPLATE_PATTERN = r"//TEMPLATE BEGIN\n([\s\S]+?)//TEMPLATE END"
APPEND_PATTERN = r"//APPEND BEGIN\n([\s\S]+?)//APPEND END"


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
    str_list = [random.choice(random_list) for _ in range(length)]
    random_str = ''.join(str_list)
    return random_str


def get_available_username(prefix, suffix, length):
    username_list = list()
    for _ in range(length):
        ok = True
        while ok:
            if prefix and suffix:
                left_len = 20 - 2 - len(prefix) - len(suffix)
                username = "{prefix}_{name}_{suffix}".format(
                    prefix=prefix,
                    name=get_random_string(mode="mixDigitLetter", length=left_len),
                    suffix=suffix
                )
            elif prefix:
                left_len = 20 - 1 - len(prefix)
                username = "{prefix}_{name}".format(
                    prefix=prefix,
                    name=get_random_string(mode="mixDigitLetter", length=left_len)
                )
            elif suffix:
                left_len = 20 - 1 - len(suffix)
                username = "{name}_{suffix}".format(
                    name=get_random_string(mode="mixDigitLetter", length=left_len),
                    suffix=prefix
                )
            else:
                left_len = 20
                username = "{name}".format(
                    name=get_random_string(mode="mixDigitLetter", length=left_len)
                )
            from organization.models import User
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


def do_before(user_id, problem_id, status='Accepted', training=True, train_id=None):
    from submission.models import Submission
    if train_id:
        return Submission.objects.filter(Q(created_by=user_id) & Q(problem=problem_id) & Q(status=status)
                                         & Q(training=train_id)).count() > 1
    else:
        return Submission.objects.filter(Q(created_by=user_id) & Q(problem=problem_id) & Q(status=status)
                                         & Q(training__isnull=training)).count() > 1


def get_languages():
    client = JudgeClient()
    language_list = client.get_languages()
    languages = dict()
    for i in language_list:
        languages.update({i.get('id'): i.get('name')})
    return languages


def prase_template(template_str):
    prepend = re.search(PREPEND_PATTERN, template_str)
    template = re.search(TEMPLATE_PATTERN, template_str)
    append = re.search(APPEND_PATTERN, template_str)
    return {
        "prepend": prepend.group(1) if prepend else "",
        "template": template.group(1) if template else "",
        "append": append.group(1) if template else ""
    }


def build_template(prepend, template, append):
    return TEMPLATE_BASE.format(prepend=prepend, template=template, append=append)


def default_statistics():
    return {
        "Commit": 0,
        "In Queue": 0,
        "Processing": 0,
        "Accepted": 0,
        "Wrong Answer": 0,
        "Time Limit Exceeded": 0,
        "Compilation Error": 0,
        "Runtime Error": 0,
        "Internal Error": 0,
        "Exec Format Error": 0
    }
