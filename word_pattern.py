from collections import *
pattern="aaaa"
s="dog cat cat dog"
new_pattern=list(pattern)
new_s=s.split(" ")
pattern_to_s={}
s_to_pattern={}
if len(new_s)!=len(new_pattern):
    print("not valid")
else:
    for i in range(len(new_s)):
        s_char=new_s[i]
        pattern_char=new_pattern[i]
        if s_char in s_to_pattern:
            if s_to_pattern[s_char]!=pattern_char:
                print("false")
                break
        if pattern_char in pattern_to_s:
            if pattern_to_s[pattern_char]!=s_char:
                print("false")
                break
        s_to_pattern[s_char]=pattern_char
        pattern_to_s[pattern_char]=s_char
    print("that was successfull")
