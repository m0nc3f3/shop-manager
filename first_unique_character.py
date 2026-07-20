from collections import Counter
s="leetcode"
counter=Counter(s)
for i in range(len(s)):
    if counter[s[i]]==1:
        print(i)
        
