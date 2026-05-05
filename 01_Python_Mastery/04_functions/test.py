


# a=1
# b=20
# print("c=",a+b)

# def addition(a,b):
#     c=a+b
#     # d=b-a
#     def sub(a,b):
#         d=b-a
#         print("inner func")
#         return d
#     print("start")
#     res=sub(1,2)
#     return c
#     print("after return")

# result=addition(12,23)
# print(result)


# def isprime(num):
#     for i in range(2,(num//2)+1): # 2,3,4,5,6,7
#         if num%i == 0:  
#             return "not a prime number"
#     else:
#         return "Prime number"

# # res=isprime(17)
# # print(res)


# for j in range(1,101):
#     if isprime(j)=="Prime number":
#         print(j)


# postitionl arguments
# def sum(a,b):
#     return float(a+b)
# print(sum(2,4))

# default parameters
# def sum(a,b=10):
#     return float(a+b)
# print(sum(2,))

# keyword arguments
# def student(age,name):
#     o=f"{name} age is {age} "
#     return 
# res=student(name="koko",age=13)
# print(res)



#list of arguments
# def addt(*args):
#     int_s=0
#     str_s=""
#     for i in args:
#         if type(i) == int:
#             int_s+=i
#         if type(i)== str:
#             str_s+=i
#     return int_s,str_s
# res=addt(23,45,23,1,12,342,42,31,3,1,"rama","sita",True)
# print(res)



# def display(**kwargs):
#     print(kwargs)
#     # output=''' my friend name is {name} and his/her age is {age}'''.format_map(kwargs)
#     return ""

# res=display(name="ramu",age=12)
# print(res)

# print(name="ramu")

# def display(username, password,*args,**kwargs ):
#     print("mandatory arguments =",username,password)
#     if len(args)>0:
#         print("optionla args",args)
#         output=args.join[str(i) for i in args]
#         return output
#     if len(kwargs)>0:
#         print("optionla kwargs received :",kwargs)
#         for k,v in kwargs.items():
#           print(k , "===",v)


# res=display("name","avav",2,4,"sra",sepea="|")
# print(res)



# def envnumbers(start,end):
#     even=[]
#     for i in range(start,end+1):
#         if i%2==0:
#             even.append(i)
#     return even

# res=envnumbers(1,2000)
# print(res)



# def envnumbers(start,end):
    
#     for i in range(start,end+1):
#         if i%2==0:
#             yield i
    

# res=envnumbers(1,20)
# for i in res:
#     print(i)
#     continue


# def generator1():
#     print("first value")
#     yield 10
#     print("second value")
#     yield 20
# res=generator1()
# for i in  res:
#     print("inside loop")
#     print(i)


# def min_max(numbers):
#     return min(numbers), max(numbers)   # returns (min, max) tuple

# high = min_max([3, 1, 4, 1, 5])   # tuple unpacking
# print(high)





# a,b,c=(1,2,3)
# print(a,b,c)
# x=10
# def display():

#     global x
#     x+=1
#     return x

# print(display())
# print(x)



# x = "global"                          # G: global scope

# def outer():
#     # x = "enclosing"                   # E: enclosing scope

#     def inner():
#         x = "local"                   # L: local scope
#         print(x)                      # finds "local" first (L)

#     def inner_no_local():
#         print(x)                      # no local x → finds "enclosing" (E)

#     inner()             # prints "local"
#     inner_no_local()    # prints "enclosing"

# outer()
# print(x)                # prints "global" (G)



# def outer():
#     x=10
#     print("enclosed ")
#     def inner():
#         print(x)
        
#     return inner()
# f=outer()
# f()


# x=[1,3,[5,23],123]
# y=x[:]
# x.append(10)
# print(x)
# print(y)



# x=[1,2,3]

# def display(y):
#     y.append(100)
# display(x)
# print(x)




# add=lambda *args:[i**2 for i in args]
# print(add(10,20,23,32,32,31,3))

st=["run","walk","strike","pull","eat","sleep"]

# res=map(lambda x:x+"ing",st)
# print(list(res))

l=[1,4,6,2,5,7,4,8,4,8,97,5,43]

# res=filter(lambda x:x%2==0 ,l)
# from functools import reduce
# res=reduce(lambda a,b:a+b,l)
# print((res))


d={"a":12,"c":1,"z":3,"x":5}

# print(d.items())
# res={d[0]:d[1] for d in sorted(list(d.items()),key=lambda x:x[1])}
res=sorted(list(d.items()))
print(res)