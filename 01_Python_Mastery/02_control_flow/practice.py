# Practice

# g="Angry"
# a=""
# if g == "Angry" and a or g!="Angry":
#     print("Solved")
# else :
#     print("NOt")



# for i in range(10):
#     if i==4:
#         break
#     else:
#         print(i,end=", ")
# import copy
# a=[1,2,4,1,[23,25],45]
# b=copy.copy(a)
# # b[4].append(1)
# print("shallow")
# print(a)
# print(b)
# print(id(a[4]))
# print(id(b[4]))

# c=copy.deepcopy(a)
# c[4].append(1)
# print("deepcopy")
# print(a)
# print(c)
# print(id(a[4]))
# print(id(c[4]))




# import time
# start=time.time()
# i=1
# while i<=5000:
#     if i>0:
#         print("positive")
#     if i<0:
#         print("negative")
#     if i==0:
#         print("zero")
    
# end=time.time()
# print("total time taken is  : ",end-start)
# # total time taken is  :  0.004374980926513672



# for i in range(101):
#     if i%3==0 and i%5==0:
#         print("fizzbuzz")
#     elif i%3==0:
#         print("fizz")
#     elif i%5==0:
#         print("buzz")
#     else:
#         print(i)
