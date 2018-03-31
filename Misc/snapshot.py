import random as rand

def print_snap(snap):
    for item in snap:
        print len(item), item
        print

def req_print(snap):
    s = ""
    for i in range(len(snap)):
        curr = snap[i]
        for j in range(len(curr)):
            s += str(curr[j])
            if(j != len(curr) - 1):
                s += ','
        if(i != len(snap) - 1):
            s += '#'

    print s
            

def make_snap():
    snap = []
    part = []
    for i in  range(0,7):
        part = []
        for j in range(0, 24):
            part.append(rand.uniform(100,500))
            #part.append(1)

        snap.append(part)

    req_print(snap)

make_snap()
