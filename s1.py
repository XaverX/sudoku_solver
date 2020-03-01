# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 20:31:25 2019
Sudoku-Solver
@author: Berthold
"""

import datetime as DT
# import operator as OP
import itertools as IT
# import collections as CL
import json as JS

"""

sudoku-solver

"""


#
rows = 'ABCDEFGHI'
cols = '123456789'
areas = 'rstuvwxyz'
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
mrk_line = "+---1-+---2-+---3-+++---4-+---5-+---6-+++---7-+---8-+---9-+"
sep_line = "+-----+-----+-----+++-----+-----+-----+++-----+-----+-----+"
blk_line = "+-@---+-----+-----+++-@---+-----+-----+++-@---+-----+-----+"
sudoku = '.sudoku'
#
XX = {}  # already known set of numbers on explicit position
PP = {}  # still possible numbers at position if XX not set to one
QQ = {}  # field is located in which groups
CCs = {}  # dict of colums
RRs = {}  # dict of rows
AAs = {}  # dict of areas/blocks
OO = {}  # dict of currently unsolvable n-tuples
FF = []  # plan for solving with back tracing
VVV = []  # temporary list of locations to work on
#


def solve_grid(h=0):
    print('solving', h)
    check_posbl()
    if h != 0:
        reduce_posbl([1, 2, 3], -1)
    else:
        # reduce_posbl([1, 2, 3])
        reduce_posbl([1, 2, 3, 4, 5, 6])
    cc = detect_miss()
    print()
    if cc == -1:
        print_all_nums()
        print_all_psbl()
        print("doesn't look well - there is a mismtch in the data")
    elif cc == +1:
        print_remaining()
        if h == 0:
            print("can't solve more - don't know further rules to do so")
            plan4backtracking()
            execute_planning()
    else:
        print("seems to be solved - no idea what to do now :-)")
    print()


def plan4backtracking():
    FF.clear()
    ff = []
    for oo in OO.values():
        ll, ss = oo
        for tt in IT.permutations(ss, len(ll)):
            ff.clear()
            for uu, vv in zip(ll, list(tt)):
                if vv not in PP[uu]:
                    break
                ff.append(tuple([uu, vv]))
            else:
                FF.append(ff.copy())


def execute_planning():
    ft = DT.datetime.now()
    fn = f'{ft.year:04}{ft.month:02}{ft.day:02}'
    fn += f'{ft.hour:02}{ft.minute:02}{ft.second:02}'
    fn += f'{ft.microsecond:06}' + sudoku
    save_file(fn)
    for ff in FF:
        print()
        print('trying: ', ff)
        for fl, fv in ff:
            set_value(fl, fv)
#            print(fl, "=", fv, ", ", sep="", end="")
#        print("\b\b  ")
        check_posbl()
        reduce_posbl([1, 2, 3])
        bb = detect_miss()
        print(bb, '\n')
        if bb == 0:
            break
        print("that didn't work - removing", ff)
        load_file(fn)


def print_remaining():
    for sgrp, ctnt in OO.items():
        print(sgrp, ctnt)
    print()


def print_all_nums():
    for j in rows:
        for zz in RRs[j]:
            print(XX[zz], end="  ")
        print()
    print()


def print_all_psbl():
    for j in rows:
        for zz in RRs[j]:
            if len(PP[zz]) > 0:
                print(zz, PP[zz], end='\t')
            else:
                print(zz, '{--}', end='\t')
        print()
    print()


def assoc_location(zz):
    L = []
    K = set([])
    tt = QQ[zz]
    K.update(set(RRs[tt[0]]))
    K.update(set(CCs[tt[1]]))
    K.update(set(AAs[tt[2]]))
    L = sorted(list(K))
    L.remove(zz)
    return L


def reduce_posbl(Psteps, h=0):
    Pmodes = ['a', 'b']  # appearance of n numbers at n locations
    # a: lonely without any others
    # b: within others but not elsewhere
    # Psteps = [1, 2, 3]  # at which n for n-tuples - , 3, 4, 5
    # step count for appearance of dedicated numbers
    ZZ = []
    VV = []
    KK = []
    while True:
        print('---------------> start loop')
        check_posbl()
        OO.clear()
        for xi, xj in IT.product(Psteps, Pmodes):
            print('## new step ##', xi, xj)
            ZZ.clear()
            # iterate over all blocks/groups and get one to work on
            z_count = 0
            for z in '0' + areas + cols + rows:
                if (xi == 1) and (xj == 'a'):
                    if (z == '0'):
                        for zz, vv in XX.items():  # iterate all locations
                            # print(zz, vv, PP[zz], sep='\t')
                            if (vv == 0):  # find a not set
                                ZZ.append(zz)  # and (len(PP[z]) == 1)
                    else:
                        continue
                else:
                    if (z == '0'):
                        continue
                    elif z in areas:
                        ZZ = AAs[z].copy()
                    elif z in cols:
                        ZZ = CCs[z].copy()
                    elif z in rows:
                        ZZ = RRs[z].copy()
        # xi step counts the to be compared numbers
        # xj step shows how to compare the numbers
        # ZZ holds the locations on which we compare
                for t in IT.combinations(nums, xi):
                    tt = set(t)
                    # print('## new combi ##', z, tt)
                    # the n-tuples of watched number-combinations
                    p_count = 0
                    x_count = 0
                    VV.clear()
                    KK.clear()
                    # VV.append(tuple([z, xi, xj, tt]))
                    VV.append((z, tt, xi, xj))
                    for zz in ZZ:
                        if XX[zz] > 0:
                            continue
                        KK.append((zz, PP[zz]))
                        if False:
                            pass
                        elif (xj == 'a') and (xi in [1, 2, 3, 4, 5, 6]):
                            if tt.issuperset(set(PP[zz])):
                                p_count += 1
                                VV.append((zz, PP[zz]))
                                KK.pop()
                        elif (xj == 'b') and (xi in [1, 2, 3, 4, 5, 6]):
                            LL = PP[zz].intersection(tt)
                            if (len(LL) > 0):
                                p_count += 1
                                VV.append((zz, PP[zz]))
                                KK.pop()
                                if (len(LL) < min(xi, 2)):
                                    x_count += 1
                    # end for zz in ZZ:
                    LL = set([])
                    if (p_count == xi) and (x_count == 0):
                        for i, vv in enumerate(VV):
                            if i == 0:
                                pWhere, pSet, pStep, pMode = vv
                                continue
                            zz, kk = vv
                            LL.update(kk)
                    if not LL.issuperset(tt):
                        continue
                    LL = set([])
                    if pMode == 'b':
                        for vv in KK:
                            zz, kk = vv
                            LL.update(kk)
                        LL.intersection_update(tt)
                        if len(LL) > 0:
                            continue

                    VVV = []
                    for i, vv in enumerate(VV):
                        if i == 0:
                            continue
                        zz, kk = vv
                        VVV.append(zz)
                    KKK = []
                    for i, vv in enumerate(KK):
                        zz, kk = vv
                        KKK.append(zz)

                    ZZZ = []
                    if pWhere == '0':
                        ZZZ = VVV.copy()
                    elif pWhere in areas:
                        ZZZ = AAs[pWhere].copy()
                    elif pWhere in cols:
                        ZZZ = CCs[pWhere].copy()
                    elif pWhere in rows:
                        ZZZ = RRs[pWhere].copy()
                    print(pSet, '===', pWhere, pStep, pMode)
                    print(VVV, '<->', KKK)
                    if pMode == 'a':
                        oName = ""
                        for oN in sorted(list(pSet)):
                            oName += str(oN)
                        oName = pWhere + "-" + oName
                        OO.setdefault(oName, (VVV, pSet))
                    for zz in ZZZ:
                        if (h != 0) and (z_count >= 1):
                            break  # verlassen um von vorn = 1a zu beginnen
                        for ii in pSet:
                            if False:
                                pass
                            elif pStep == 1:
                                if (zz in VVV):
                                    z_count += 1
                                    print('(1++', zz, ii, PP[zz], end='')
                                    set_value(zz, ii)
                                    PP[zz] = set([])
                                    print(' > ', PP[zz], end=') ')
                                    for yy in assoc_location(zz):
                                        if ii not in PP[yy]:
                                            continue
                                        print('(1--', yy, ii, PP[yy], end='')
                                        PP[yy].discard(ii)
                                        print(' > ', PP[yy], end=') ')
                            elif pStep >= 2:
                                if (zz in VVV):
                                    if PP[zz].intersection(pSet) != PP[zz]:
                                        z_count += 1
                                        print('(2++', zz, pSet, PP[zz], end='')
                                        PP[zz].intersection_update(pSet)
                                        print(' > ', PP[zz], end=') ')
                                else:
                                    if ii in PP[zz]:
                                        print('(2--', zz, ii, PP[zz], end='')
                                        PP[zz].discard(ii)
                                        print(' > ', PP[zz], end=') ')
                            else:
                                print('???', zz)
                    print()
                    if (h != 0) and (z_count >= 1):
                        break  # verlassen um von vorn = 1a zu beginnen
                # end for t in IT.combinations(nums, xi):
                if (h != 0) and (z_count >= 1):
                    break  # verlassen um von vorn = 1a zu beginnen
            # end for z in '0' + areas + cols + rows:
            if (z_count >= 1):
                break  # verlassen um von vorn = 1a zu beginnen
        # end for xi, xj in IT.product(Psteps, Pmodes):
        if (h == 0) and (z_count >= 1):
            continue
        if (h != 0) or (z_count == 0):
            break  # while True - Notausgang
    #  end while True:


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
    for xx in XX.keys():
        if f:
            PP[xx] = set(nums)
    for xx, vv in XX.items():
        # print('!:', xx, vv, QQ[xx], PP[xx], flush=True)
        YY = []
        if vv > 0:
            PP[xx].clear()
            z = QQ[xx][0]
            YY = RRs[z].copy()
            for yy in YY:
                if yy != xx:
                    PP[yy].discard(vv)
            z = QQ[xx][1]
            YY = CCs[z].copy()
            for yy in YY:
                if yy != xx:
                    PP[yy].discard(vv)
            z = QQ[xx][2]
            YY = AAs[z].copy()
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
    RR = []
    for r in rows:
        RR.clear()
        for c in cols:
            z = r + c
            RR.append(z)
        RRs.setdefault(r, RR.copy())
    # columns
    CC = []
    for c in cols:
        CC.clear()
        for r in rows:
            z = r + c
            CC.append(str(z))
        CCs.setdefault(c, CC.copy())
    # areas
    AA = []
    for n in [0, 1, 2]:  # row group
        for p in [0, 1, 2]:  # col group
            AA.clear()
            for m in [0, 1, 2]:  # rows in group
                for q in [0, 1, 2]:  # cols in group
                    r = n * 3 + m
                    c = p * 3 + q
                    z = rows[r] + cols[c]
                    XX.setdefault(z, 0)
                    PP.setdefault(z, set(nums))
                    QQ.setdefault(z, tuple([rows[r], cols[c], areas[n*3+p]]))
                    AA.append(z)
            AAs.setdefault(areas[n * 3 + p], AA.copy())


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
    XYZ = []
    if f:
        for p, q, v in zip(rows, cols, nums):
            set_value(p + q, v)
        return
    for k, v in region.items():
        if k in cols:
            XYZ = CCs[k]
        elif k.upper() in rows:
            XYZ = RRs[k.upper()]
        elif k.lower() in areas:
            XYZ = AAs[k.lower()]
        else:
            return
    for k, v in single.items():
        if k in PP.keys():
            XYZ.append(k)
    if len(complete) > 0:
        v = ""
        for e in complete:
            v += str(e)
        for r in sorted(RRs.keys()):
            XYZ.extend(RRs.get(r))
    #
    i = 0
    for zz in XYZ:
        if (v[i] != " "):
            set_value(zz, int(v[i]))
        i += 1


def load_file(f=''):
    if f == '':
        return
    if not f.endswith(sudoku):
        f += sudoku
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
    if not f.endswith(sudoku):
        f += sudoku
    print('saving data to file:', f)
    try:
        with open(f, "x") as fp:
            JS.dump(XX, fp)
    except FileExistsError:
        print('take another name!', f)


def tell_help():
    print()
    print('fill r/c/a:  i:[A|n=]{0-9}9[,{0-9}9 ...]     solve grid:   S')
    print('enter value: e:An=0                          step by step: s')
    print('load a set:  l:filename                      clear/reset:  c')
    print('write file:  w:filename                      exit/leave:   x')


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
    if ww == 's':
        solve_grid(1)
    if ww == 'S':
        solve_grid(0)
    ww = ww[0].lower()
    if ww == 'x':
        break
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
