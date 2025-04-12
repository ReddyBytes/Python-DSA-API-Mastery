def find_target(arr,target):
    for i in range(0,len(arr)):
        if arr[i]==target:
            return f"{target} is present at {i} index position "
    return f"{target} is not present in the {arr}"  # returns single string as output
    #return target, "is not present in the ", arr # returns tuple as output
        
# print(find_target([1,2,3,4,5],4))


def binary_search(arr,target):
    sorted_array=sorted(arr)
    print(sorted_array)
    start=0
    end=len(arr)-1
    while start<=end:
        mid=(start+end)//2
        if sorted_array[mid]==target:
            return f"{sorted_array[mid]} is present at {mid} index"
        elif sorted_array[mid]<target:
            start=mid+1
        elif sorted_array[mid]>target:
            end=mid-1

# print(binary_search([23,54,12,4,324,64,76,345,1],345))




# s=["azala","arun","syam",10,2,"dastagiri"]
# s.sort(key=str)
# print(s)
#
# # ss=sorted(s,key=int)
# # print(ss)



#### selection sort

# def selection_sort(arr):
#     n=len(arr)
#     for i in range(0,n):
#         min_index=i
#         for j in range(i+1,n):
#             if arr[j]<arr[min_index]:
#                 min_index=j
#         arr[i],arr[min_index]=arr[min_index],arr[i]
#     return arr

# unsorted_arr=[5,3,4,1,65,23,1,413,1,23,4,5,6]
# print("unsorted_arr :",unsorted_arr)
# print("sorted arr :",selection_sort(unsorted_arr))

# def sum_values(arr):
#     sum=0
#     for i in range(len(arr)):
#         sum+=arr[i]
#     return sum
# print(sum_values([1,10]))



# list=[1,4,6,3,7,356,86]
# s=sorted(list)


def  binary_search_value(arr,target):
    sorted_arr=sorted(arr)
    low=0
    high=len(arr)-1
    while True:
        mid=(low + high)//2
        mid_number=arr[mid]
        if mid>0 and arr[mid]==target:
            return mid
        elif arr[mid]