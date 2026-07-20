nums1=[4,9,5]
nums2=[9,4,9,8,4]
intersection=set()
for num1 in nums1:
    for num2 in nums2:
        if num1==num2:
            intersection.add(num1)
print(list(intersection))