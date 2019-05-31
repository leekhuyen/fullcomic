import re

def remove_consecutive_characters(comic_name, delimiter):
    s = comic_name[:1]
    remain = comic_name[1:]
    for c in remain:
        if s[len(s)-1] != delimiter or s[len(s)-1] != c:
            s += c

    return s

def convert(text):
    patterns = {
        '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
        '[đ]': 'd',
        '[èéẻẽẹêềếểễệ]': 'e',
        '[ìíỉĩị]': 'i',
        '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
        '[ùúủũụưừứửữự]': 'u',
        '[ỳýỷỹỵ]': 'y'
    }
    output = text
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        # deal with upper case
        output = re.sub(regex.upper(), replace.upper(), output)
    return output

def remove_special_character(text):
    return re.sub('[^A-Za-z0-9 ]+', '', text)

def generate_url_name(name):
    s1 = remove_consecutive_characters(name, ' ')
    if s1[len(s1)-1] == ' ':
        s1 = s1[:len(s1)-1]

    s2 = convert(s1)
    s2 = remove_special_character(s2)

    return s2.replace(' ', '-')
