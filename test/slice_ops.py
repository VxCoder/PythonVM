lst = [1, 2, 3, 4, 5, 6]
print lst[0:-1:2]

a_list = ['1', '2', '3', '4', '5', '6']
a_list[1:] = lst[1:]
print a_list

a_list[:3] = lst[:3]
print a_list

a_list[2:4] = lst[2:4]
print a_list

a_list[:] = lst[:]
print a_list

del lst[1:]
print lst

del lst[:3]
print lst

del a_list[2:4]
print a_list

del a_list[:]
print a_list
