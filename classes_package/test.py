mapdata = {}

f = open('map.txt')

curr_layer = None
for row in f.read().split('\n'):
    if 'Layer' in row:
        curr_layer = row
        mapdata[curr_layer] = []
    elif row:
        mapdata[curr_layer].append([int(c) for c in row])

f.close()
