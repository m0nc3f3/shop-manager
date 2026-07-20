from collections import Counter
ransomeNote="aab"
magazine="b"
counter_ransomeNote=Counter(ransomeNote)
counter_magazine=Counter(magazine)
for k,v in counter_ransomeNote.items():
    if counter_ransomeNote[k]!=counter_magazine[k]:
        print(False)
    else:
        print(False)
