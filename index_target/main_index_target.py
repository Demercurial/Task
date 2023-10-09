
def find_target_index(nums:list,target:int)-> list:
# Из массива целых чисел и одним целым значением возвращает 
# индексы двух чисел массива так, что бы их сумма равнялась 
# исходному целому значению
    k = 0
    for i in range(len(nums)):
        k += 1
        for j in range(k,len(nums)):
            if nums[i] + nums[j] == target:
                return [i,j]           
            
nums = [0,0]
target = 0
print(find_target_index(nums,target))
