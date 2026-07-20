number1=123
number2=-321
number3=120
rev=0
negative=False
if number2<0:
    number2*=-1
    negative=True
while number2>=1:
    rev=rev*10+number2%10
    number2//=10
if negative:
    print(rev*-1)
else:
    print(rev)


