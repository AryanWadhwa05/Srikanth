import random
import string
import numpy as np

#input1 = input("Enter your information here: ")
input1 = input("Enter your information here: ")
if len(input1)==16:
    list2=list(input1)[4:12]
    input2=''.join(list2)

    l = []
    for i in range(22):
        lower_upper_alphabet = string.ascii_letters
        random_letter = random.choice(lower_upper_alphabet)
        l.append(random_letter)  
        
    print(l)
    print(list2)

    str1=''.join([''.join(l[0:5]),''.join(list2[0:2])])
    str2=''.join([''.join(list2[2:4]),''.join(l[5:12])])
    str3=''.join([''.join(l[12:16]),''.join(list2[4:6])])
    str4=''.join([''.join(list2[6:8]),''.join(l[16:222])])
    print(l)
    print(str1)
    token=str1+'-'+str2+'-'+str3+'-'+str4
    print(token)
    
else:
    print("Your information isn't quite right")
