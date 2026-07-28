x = 1
y = 2
z = x
x = y
y = z
print(x, y)

x = int(input())
y = int(input())

x = x / y
y = y / x

print(y)

x = int(input())
y = int(input())

x = x % y
x = x % y
y = y % x

print(y)




