from collections import defaultdict
from collections import Counter
# array=["eat","tea","tan","ate","nat","bat"]
# dictionarry=defaultdict(list)
# for word in array:
#     sorted_word_list=sorted(word)
#     sorted_word="".join(sorted_word_list)
#     print(sorted_word)
#     dictionarry[sorted_word].append(word)
# print(dictionarry)
nums=[3,3,4]
counter=Counter(nums)
maximum=max(list(counter.values()))
for k,v in counter.items():
    if v==maximum:
        print(k)