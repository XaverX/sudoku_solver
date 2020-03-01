# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 12:08:59 2019

sudoku-solver

@author: Berthold
"""

import datetime as DT
# import operator as OP
import itertools as IT
# import collections as CL
import json as JS

"""

sudoku-solver
will write a 3x3-square
of some smaller 3x3-grids

you may enter some preset values
if done it will try to solve

"""


#
rows = 'ABCDEFGHI'
cols = '123456789'
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
areas = 'rstuvwxyz'
mrk_line = "+---1-+---2-+---3-+++---4-+---5-+---6-+++---7-+---8-+---9-+"
sep_line = "+-----+-----+-----+++-----+-----+-----+++-----+-----+-----+"
blk_line = "+-@---+-----+-----+++-@---+-----+-----+++-@---+-----+-----+"
#
XX = {}  # already known/set numbers on position
PP = {}  # possible numbers at position
QQ = {}  # field located in which groups
CCs = {}  # dict of colums
RRs = {}  # dict of rows
AAs = {}  # dict of areas/blocks
VVV = []
#


def solve_grid(h=0):
    print('solving', h)
    check_posbl()
    reduce_posbl(h)
    cc = detect_miss()
    if cc == -1:
        print("doesn't look well - there is a mismtch in the data")
    elif cc == +1:
        print("can't solve more - don't know further rules to do so")
    else:
        print("seems to be solved - no idea what to do now :-)")


def f(L):
    s = '_'
    for n in L:
        s += str(n)
    return s


def reduce_posbl(h=0, u=0):
    # a) find only singles, pairs, triplets, asf...
    # b) find insights once, doubles, triples, asf...
    VV = []
    CC = dict([])
    DD = dict([])

    while True:

        #
        # 1a - find a lonely possible number
        #
        VV.clear()
        for z, v in XX.items():
            # iterate over all basic locations
            if v == 0:
                # find a not set one with only 1 possibility add to list
                if len(PP[z]) == 1:
                    VV.append(z)
        if len(VV) > 0:
            # check reduced remaining possibilities to set further values
            print(f'1a {len(VV):2}', '\tset this: ', end="")
            for z in VV:
                # list gives positions for setting values
                v = PP[z].pop()
                set_value(z, v)
                print(z, "=", v, ", ", sep="", end="")
            else:
                print("\b\b  ")
            check_posbl()
            if h:
                break
            continue

        #
        # 1b - find a number that appears only once in group
        #
        cc = 0
        st = ""
        for z in areas + cols + rows:
            # iterate over all blocks/groups aand get it to work on
            if z in areas:
                ZZ = AAs[z]
            elif z in cols:
                ZZ = CCs[z]
            elif z in rows:
                ZZ = RRs[z]
            else:
                ZZ = []
            CC.clear()  # counter for appearance of number v
            DD.clear()  # last position of number if count=1 the only one
            for zz in ZZ:
                # iterate over all possibilties in current chosen block
                # count there appearance
                # and only for count = 1 interested location
                for v in PP[zz]:
                    CC[v] = CC.get(v, 0) + 1
                    DD[v] = DD.get(v, zz)
            for v, c in CC.items():
                # get the once with count=1 and location to set them
                if c == 1:
                    cc += 1  # is there something todo
                    zz = DD.get(v)
                    set_value(zz, v)
                    if st.rfind(zz) < 0:
                        st += f'{zz}={v}, '
        if cc > 0:
            # check reduced remaining possibilities to set further values
            print(f'1b {cc:2}', '\tset this: ', st, sep="", end="")
            print("\b\b  ")
            check_posbl()
            if h:
                break
            continue

        #
        # 2a - couples of pair numbers
        #
        cc = 0
        st = ""
        for z in areas + cols + rows:
            # iterate over all blocks/groups and get a block to work on
            if z in areas:
                ZZ = AAs[z]
            elif z in cols:
                ZZ = CCs[z]
            elif z in rows:
                ZZ = RRs[z]
            else:
                ZZ = []
            CC.clear()
            DD.clear()
            for zz in ZZ:
                # iterate over all possibilties in current chosen block
                if len(PP[zz]) != 2:
                    continue
                vv = list(PP[zz])
                vv = str(vv[0]) + str(vv[1])
                CC[vv] = CC.get(vv, 0) + 1
                DD[vv] = DD.get(vv, []) + [zz]
            for kk, vv in DD.items():
                if len(vv) == 2:
                    if st.find(f'{vv}') < 0:
                        st += f'{vv}:{set([int(kk[0]), int(kk[1])])}, '
                    for zz in ZZ:
                        if (PP[zz] == set([])) or (zz in vv):
                            continue
                        if int(kk[0]) in PP[zz]:
                            cc += 1  # something todo
                            PP[zz].discard(int(kk[0]))
                        if int(kk[1]) in PP[zz]:
                            cc += 1  # something todo
                            PP[zz].discard(int(kk[1]))
        if cc > 0:
            # check reduced remaining possibilities to set further values
            print(f'2a {cc:2}', '\treduced by: ', st, sep="", end="")
            print("\b\b  ")
            check_posbl()
            if h:
                break
            continue

        #
        # 2b - find a pair of numbers that appears exactly twice in group
        #
        cc = 0
        st = ""
        for z in areas + cols + rows:
            # iterate over all blocks/groups aand get it to work on
            if z in areas:
                ZZ = AAs[z]
            elif z in cols:
                ZZ = CCs[z]
            elif z in rows:
                ZZ = RRs[z]
            else:
                ZZ = []
            for xy in [[x, y] for x in nums for y in nums if x < y]:
                # get all number pairs and count for appearance
                # check for existence in exact 2 locations
                DD.clear()  # last position
                vv = str(xy[0]) + str(xy[1])
                c = 0
                for zz in ZZ:
                    # iterate over all possibilties in current chosen block
                    if set(xy).issubset(PP[zz]):
                        # if both then count
                        c += 1
                        DD[vv] = DD.get(vv, []) + [zz]
                    elif {xy[0]}.issubset(PP[zz]) or {xy[1]}.issubset(PP[zz]):
                        # if only one of them exit loop
                        break
                    if c >= 3:
                        # to much of that pairs
                        break
                else:
                    # for does not break we have pairs on 2 locations
                    for dd in DD.values():
                        for zz in dd:
                            for v in nums:
                                if (v not in xy) and (v in PP[zz]):
                                    cc += 1
                                    PP[zz].discard(v)
                                    if st.find(f'{dd}') < 0:
                                        st += f'{dd}:{set([xy[0], xy[1]])}, '
        if cc > 0:
            # check reduced remaining possibilities to set further values
            print(f'2b {cc:2}', '\treduced by: ', st, sep="", end="")
            print("\b\b  ")
            check_posbl()
            if h:
                break
            continue
        if u != 0:
            break

        #
        # NX - find multiples of n that appears exactly n-times in group
        #
        cc = 0
        CC.clear()
        for z in rows + cols:  # + areas
            # iterate over all blocks/groups aand get it to work on
            if z in areas:
                ZZ = AAs[z]
            elif z in cols:
                ZZ = CCs[z]
            elif z in rows:
                ZZ = RRs[z]
            else:
                ZZ = []

            DD.clear()
            for zz in ZZ:
                if XX[zz] == 0:
                    # print(z, zz, PP[zz])
                    DD[zz] = PP[zz]

            N = []
            Q = []
            for v in nums:
                for dd in DD.values():
                    if dd.__contains__(v):
                        if v not in N:
                            N.append(v)
            # print('>>> ', z, DD)
            # print('> ', N, ' <')
            if len(N) >= 2:  # find remaining n-tuples,2,3,4,5,6
                for n in [[i, j] for i in N for j in N
                          if i < j]:
                    Q.clear()
                    Y = set(n)
                    for (xx, pp) in DD.items():
                        if pp.issubset(Y):  # Y.issuperset(pp):
                            Q.append(xx)
                    if len(n) == len(Q):
                        # CC[z + f(n)] = Q.copy()
                        if (len(Q) < len(N)) or (CC.get(z, []) == []):
                            CC[z] = CC.get(z, []) + [tuple([n, Q.copy()])]
            if len(N) >= 3:
                for n in [[i, j, k] for i in N for j in N for k in N
                          if i < j and j < k]:
                    Q.clear()
                    Y = set(n)
                    for (xx, pp) in DD.items():
                        if pp.issubset(Y):  # Y.issuperset(pp):
                            Q.append(xx)
                    if len(n) == len(Q):
                        # CC[z + f(n)] = Q.copy()
                        if (len(Q) < len(N)) or (CC.get(z, []) == []):
                            CC[z] = CC.get(z, []) + [tuple([n, Q.copy()])]
            if len(N) >= 4:
                for n in [[i, j, k, l] for i in N for j in N
                          for k in N for l in N
                          if i < j and j < k and k < l]:
                    Q.clear()
                    Y = set(n)
                    for (xx, pp) in DD.items():
                        if pp.issubset(Y):  # Y.issuperset(pp):
                            Q.append(xx)
                    if len(n) == len(Q):
                        # CC[z + f(n)] = Q.copy()
                        if (len(Q) < len(N)) or (CC.get(z, []) == []):
                            CC[z] = CC.get(z, []) + [tuple([n, Q.copy()])]
            if len(N) >= 5:
                for n in [[i, j, k, l, m] for i in N for j in N
                          for k in N for l in N for m in N
                          if i < j and j < k and k < l and l < m]:
                    Q.clear()
                    Y = set(n)
                    for (xx, pp) in DD.items():
                        if pp.issubset(Y):  # Y.issuperset(pp):
                            Q.append(xx)
                    if len(n) == len(Q):
                        # CC[z + f(n)] = Q.copy()
                        if (len(Q) < len(N)) or (CC.get(z, []) == []):
                            CC[z] = CC.get(z, []) + [tuple([n, Q.copy()])]
            if len(N) >= 6:
                for n in [[i, j, k, l, m, o] for i in N for j in N
                          for k in N for l in N for m in N for o in N
                          if i < j and j < k and k < l and l < m and m < o]:
                    Q.clear()
                    Y = set(n)
                    for (xx, pp) in DD.items():
                        if pp.issubset(Y):  # Y.issuperset(pp):
                            Q.append(xx)
                    if len(n) == len(Q):
                        # CC[z + f(n)] = Q.copy()
                        if (len(Q) < len(N)) or (CC.get(z, []) == []):
                            CC[z] = CC.get(z, []) + [tuple([n, Q.copy()])]
        DD.clear()
        TTT = []
        # bring n-tuples in order of length in Q
        for n in range(2, 4):  # maxrange <= 7
            for xxx, yyy in CC.items():
                for t in yyy:
                    xy, dd = t
                    if len(xy) != n:
                        continue
                    Q.clear()
                    Q.append(xxx + f(xy))
                    for d in dd:
                        Q.append(d)
                    TTT.append(Q.copy())
                    # combine tuples with permutation of possible numbers
                    DD[xxx + f(xy)] = [tp for tp in IT.permutations(xy)]
        # print(TTT)
        # print(DD)

        HH = []
        HHH = []
        for ttt in TTT:
            # print(DD[ttt[0]])
            # print('\t', ttt[1:])
            zzz = ttt[1:]
            iii = len(DD[ttt[0]])
            jjj = len(zzz)
            # print(iii, jjj, ttt[0], zzz)
            # build sets of positions and possible numbers
            for ii in range(iii):
                uuu = DD[ttt[0]][ii]  # permutations
                # print(uuu, zzz)
                HH.clear()
                for jj in range(jjj):
                    # print(jj, uuu[jj], PP[zzz[jj]])
                    if uuu[jj] in PP[zzz[jj]]:
                        HH.append(tuple([zzz[jj], uuu[jj]]))
                    else:
                        break
                else:
                    if len(HH) == jjj:
                        HHH.append(HH.copy())
        ft = DT.datetime.now()
        fn = f'{ft.year:04}{ft.month:02}{ft.day:02}'
        fn += f'{ft.hour:02}{ft.minute:02}{ft.second:02}'
        fn += f'{ft.microsecond:06}' + '.sudoku'
        save_file(fn)
        for HH in HHH:
            print(f'Z{cc:2}/{len(HHH):2}', '\ttry this: ', end="")
            for H in HH:
                set_value(H[0], H[1])
                print(H[0], "=", H[1], ", ", sep="", end="")
            print("\b\b  ")
            check_posbl()
            reduce_posbl(h=0, u=1)
            bb = detect_miss()
            print(bb)
            if bb == 0:
                break
            cc += 1
            load_file(fn)

        if cc >= len(HHH):
            # check reduced remaining possibilities to set further values
            print('NX', cc)
            check_posbl()
#            if h:
#                break
#            continue

        # nothing was changed and no-one hasn't used continue for looping
        break


def detect_miss():
    z = 0
    v = 0
    p = 0
    e = 0
    for tt in [(zz, vv, pp)
               for zz, vv in XX.items()
               for yy, pp in PP.items()
               if yy == zz]:
        zz, vv, pp = tt
        z += 1
        if vv != 0:
            v += 1
        if pp == set([]):
            p += 1
        if (vv == 0) and (pp == set([])):
            e += 1
    if (e > 0) or (p > v):
        return -1
    elif (z > v) or (z > p):
        return +1
    else:
        return 0


def check_posbl(f=False):
    for xx, vv in XX.items():
        # print('!:', xx, vv, QQ[xx], PP[xx], flush=True)
        if f:
            PP[xx] = set(nums)
        if vv > 0:
            PP[xx].clear()
            z = QQ[xx][0]
            YY = RRs[z]
            for yy in YY:
                if yy != xx:
                    PP[yy].discard(vv)
            z = QQ[xx][1]
            YY = CCs[z]
            for yy in YY:
                if yy != xx:
                    PP[yy].discard(vv)
            z = QQ[xx][2]
            YY = AAs[z]
            for yy in YY:
                if yy != xx:
                    PP[yy].discard(vv)


def draw_grid_line(z="|", L={}):
    num_element = "     |"
    t = ""
    x = z.upper()
    if z.islower():
        z = "|"
    for m in range(9):
        if m % 3 == 0:
            t += z
            z = "||"
        y = str(m+1)
        u = L.get(x+y, 0)
        if u != 0:
            v = str(u) * 5 + "|"
            t += v
        else:
            t += num_element
    print(t)


def draw_grid():
    print("\n")
    m = 0
    while True:
        if m % 3 == 0:
            t = blk_line
            t = t.replace('@', areas[m+0], 1)
            t = t.replace('@', areas[m+1], 1)
            t = t.replace('@', areas[m+2], 1)
            print(t.upper())
        else:
            print(sep_line)
        draw_grid_line(rows[m].lower(), XX)
        draw_grid_line(rows[m].upper(), XX)
        m += 1
        if m >= 9:
            print(mrk_line)
            break
        if m % 3 == 0:
            print(sep_line)


def make_grid():
    XX.clear()  # already known/set numbers on position
    PP.clear()  # possible numbers at position
    QQ.clear()  # field located in which groups
    CCs.clear()  # dict of colums
    RRs.clear()  # dict of rows
    AAs.clear()  # dict of areas/blocks
    # rows
    for r in rows:
        RR = []
        for c in cols:
            z = r + c
            RR.append(z)
        RRs.setdefault(r, RR)
    # columns
    for c in cols:
        CC = []
        for r in rows:
            z = r + c
            CC.append(str(z))
        CCs.setdefault(c, CC)
    # areas
    for n in [0, 1, 2]:  # row group
        for p in [0, 1, 2]:  # col group
            AA = []
            for m in [0, 1, 2]:  # rows in group
                for q in [0, 1, 2]:  # cols in group
                    r = n * 3 + m
                    c = p * 3 + q
                    z = rows[r] + cols[c]
                    XX.setdefault(z, 0)
                    PP.setdefault(z, set(nums))
                    QQ.setdefault(z, tuple([rows[r], cols[c], areas[n*3+p]]))
                    AA.append(z)
            AAs.setdefault(areas[n * 3 + p], AA)


def set_value(p, v):
    if len(p) != 2:
        return
    p = p.upper()
    if (p[0] < 'A') or (p[0] > 'I'):
        return
    if (p[1] < '1') or (p[1] > '9'):
        return
    if (v < 0) or (v > 9):
        return
    XX.update({p: v})


def enter_grid(region={}, single={},
               complete=[], f=False):
    ZZ = []
    if f:
        for p, q, v in zip(rows, cols, nums):
            set_value(p + q, v)
        return
    for k, v in region.items():
        if k in cols:
            ZZ = CCs[k]
        elif k.upper() in rows:
            ZZ = RRs[k.upper()]
        elif k.lower() in areas:
            ZZ = AAs[k.lower()]
        else:
            return
    for k, v in single.items():
        if k in PP.keys():
            ZZ.append(k)
    if len(complete) > 0:
        v = ""
        for e in complete:
            v += str(e)
        for r in sorted(RRs.keys()):
            ZZ.extend(RRs.get(r))
    #
    i = 0
    for zz in ZZ:
        if (v[i] != " "):
            set_value(zz, int(v[i]))
        i += 1


def load_file(f=''):
    if f == '':
        return
    print('loading data from file:', f)
    try:
        with open(f, "r") as fp:
            XX.update(JS.load(fp))
            check_posbl(True)
    except FileNotFoundError:
        pass


def save_file(f=''):
    if f == '':
        return
    print('saving data to file:', f)
    try:
        with open(f, "x") as fp:
            JS.dump(XX, fp)
    except FileExistsError:
        print('take another name!', f)


def tell_help():
    print()
    print('fill r/c/a:  i:[A|n=]{0-9}9[,{0-9}9 ...]     solve grid:  s')
    print('enter value: e:An=0                          tell 1 step: t')
    print('fix content: f[:{0-9}]                       step back:   b')
    print('load a set:  l:filename                      clear/reset: c')
    print('write file:  w:filename                      exit/leave:  x')


#   MAIN
make_grid()
while True:
    draw_grid()
    check_posbl()
    tell_help()
    ww = input('choose a command: ')
    if ww == "":
        continue
    vv = ""
    if (len(ww) > 1) and (ww[1] in
       [':', '.', '=', ';', ',', '#', ' ', '_', '+', '-']):
        vv = ww[2:]
    ww = ww[0].lower()
    if ww == 'x':
        break
    if ww == 's':
        solve_grid(0)
    if ww == 't':
        solve_grid(1)
    if ww == 'c':
        make_grid()
    if ww == 'z':
        enter_grid(f=True)
    if ww == 'i':
        if vv.find('=') == 1:
            V = vv.split('=', 1)
            V[0] = V[0][0].upper()
            V[1] = V[1][0:9]
            if (V[0].isalnum()) and (V[1].isdigit()):
                enter_grid(region={V[0]: V[1]})
        elif vv.find(',') >= 0:
            V = vv.split(',', 9)
            i = 0
            for vv in V:
                V[i] = (vv + '         ')[0:9]
                i += 1
            while len(V) < 9:
                V.append('         ')
            enter_grid(complete=V)
    if ww == 'e':
        VVV.clear()
        if vv.find(',') == 4:
            VVV = vv.split(',')
        else:
            VVV.append(vv)
        for vv in VVV:
            if vv.find('=') == 2:
                V = vv.split('=', 1)
                V[0] = V[0][0:2].upper()
                V[1] = V[1][0]
                if (V[0] in PP.keys()) and (V[1].isdigit()):
                    enter_grid(single={V[0]: V[1]})
    if ww == 'l':
        load_file(vv)
    if ww == 'w':
        save_file(vv)
    if ww == 'f':
        pass
    if ww == 'b':
        pass
