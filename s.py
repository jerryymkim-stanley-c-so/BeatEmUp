# for stan to test stuff

DELIMITER = '|'
L = DELIMITER.join(['aaa', 'bbb', 'ccc'])
[a, *b] = L.split(DELIMITER)
print('a:', a)
print('b:', b)

print((1, 2, 3) * 10)