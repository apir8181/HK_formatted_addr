import langconv
import hk_wiki

def remove_spaces_utf8(addr):
    space = u" "
    ret = u""
    for c in addr:
        print c
        if c != space:
            ret += c
    return ret

def traditional_to_simple(s):
    return langconv.Converter("zh-hans").convert(s)

def simple_to_traditional(s):
    return langconv.Converter("zh-hant").convert(s)
