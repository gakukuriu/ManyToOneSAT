from math import factorial
from itertools import permutations
from itertools import chain,combinations
from collections import defaultdict
import pickle

#
# Tools
#

def powerset(iterable):  # takes an iterable object and returns an iterable object consisting of the power set of that element
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


#
# Market Dimension
#

# the default value for dimensions (n:total number of hospitals, m:total number of interns)
n = 2
m = 2

# change the value of dimensions
def setDimension(k, l):   
    global n, m
    n = k
    m = l

# return the current value of dimensions
def getDimension():
    return (n, m)


#
# Indices, Preferences, Profiles of Hospiutals/Interns
#

def allHospitalsIndices():
    return range(n)

def allHospitalsCapacityIndices():
    return range(1, m+1)

def allInternsIndices():
    return range(m) 

def allInternGroupsIndices():
    return range(2**m)

def allHospitalsPreferences():
    return range(factorial(2 ** m))

def allInternsPreferences():
    return range(factorial(n+1))

def allHospitalsProfiles():
    return range((factorial(2 ** m)) ** n)

def allInternsProfiles():
    return range((factorial(n+1)) ** m)

def allHospitalsCapacities():
    return range(m ** n)
    

#
# Reasoning about preferences/profiles
#

def internsPrefId(i, p):  # extract the preference of intern i from the intern's profile p in index format
    base = factorial(n+1)
    return ( p % (base ** (i+1)) ) // (base ** i)

def hospitalsPrefId(i, p):  # extract the preference of hospital i from the hospital's profile p in index format
    base = factorial(2**m)
    return ( p % (base ** (i+1)) ) // (base ** i)

def hospitalsCapa(i, q):  # extract the capacity of hospital i from the hospital's capacity profile q in index format
    base = m
    return (( q % (base ** (i+1)) ) // (base ** i)) + 1

def internsPrefList(i, p):   # extract the preference of intern i from the intern's profile p in list format
    preflists = list(permutations(range(n+1)))
    return preflists[internsPrefId(i, p)]

def hospitalsPrefList(i, p):  # extract the preference of hospital i from the hospital's profile p in list format
    preflists = list(permutations(range(2**m)))
    pw = list(powerset(allInternsIndices()))
    return [pw[i] for i in preflists[hospitalsPrefId(i, p)]]

def internsPrefers(i, h1, h2, p):  # check whether intern i prefers hospital h1 to h2 in profile p
    mylist = internsPrefList(i, p)
    return mylist.index(h1+1) < mylist.index(h2+1)

def hospitalsPrefers(h, g1, g2, p):  # check whether hospital h prefers intern's group g1 to g2 in profile p
    mylist = hospitalsPrefList(h, p)
    return mylist.index(g1) < mylist.index(g2)

def responsiveCondition(J_index, prList):  # check whether the preference relation prList satisfies the responsible condition for a subset J of the set of all interns.
    powerI_index = 2**m - 1
    powerI = list(powerset(range(m)))
    J = powerI[J_index]
    IminusJ = powerI[powerI_index-J_index]
    for i in IminusJ:
        Jplusi = tuple(sorted(J + (i,)))
        if (prList.index(Jplusi) < prList.index(J)):
            if prList.index(()) < prList.index((i,)):
                return False
        if prList.index((i,)) < prList.index(()):
            if prList.index(J) < prList.index(Jplusi):
                return False
        for j in IminusJ:
            if i != j:
                Jplusj = tuple(sorted(J + (j,)))
                if prList.index(Jplusi) < prList.index(Jplusj):
                    if prList.index((j,)) < prList.index((i,)):
                        return False
                if prList.index((i,)) < prList.index((j,)):
                    if prList.index(Jplusj) < prList.index(Jplusi):
                        return False
    return True

def responsivePref(prList):  # check whether preference list prList is responsive
    allJ = 2 ** m
    for j in range(allJ):
        if not(responsiveCondition(j, prList)):
            return False
    return True

def allHospitalsResponsivePreferences():  # return all responsive preferences of hospitals
    ans = []
    preflists = list(permutations(range(2**m)))
    pw = list(powerset(allInternsIndices()))
    for p in allHospitalsPreferences():
        prefList = [pw[i] for i in preflists[p]]
        if responsivePref(prefList):
            ans.append(p)
    return (range(len(ans)), ans)

def allHospitalsResponsiveProfiles(): # return all responsive profiles of hospitals
    _, y = allHospitalsResponsivePreferences()
    return (range(len(y) ** n), y)

def hospitalsPrefId_R(i, p):  # extract the preference of hospital i from the hospital's responsive profile p in index format
    _, y = allHospitalsResponsivePreferences()
    base = len(y)
    y_ind = ( p % (base ** (i+1)) ) // (base ** i)
    return y_ind

def hospitalsPrefList_R(i, p):  # extract the preference of hospital i from the hospital's responsive profile p in list format
    _, y = allHospitalsResponsivePreferences()
    preflists = list(permutations(range(2**m)))
    pw = list(powerset(allInternsIndices()))
    return [pw[i] for i in preflists[y[hospitalsPrefId_R(i, p)]]]

def hospitalsPrefers_R(h, g1, g2, p):  # check whether hospital h prefers intern's group g1 to g2 in hospital's responsive profile p
    mylist = hospitalsPrefList_R(h, p)
    return mylist.index(g1) < mylist.index(g2)


def visualize_HospitalPreference(p):  # visualize a hospital's preference
    preflists = list(permutations(range(2**m)))
    pw = list(powerset(allInternsIndices()))
    prefList = [pw[i] for i in preflists[p]]
    return prefList


def inGroup(i, g):  # check whether intern i belongs to group g
    allG = list(powerset(range(m)))
    return (i in allG[g])

def toGroup(i):  # returns the index of a group consisting of only intern i
    allG = list(powerset(range(m)))
    return allG.index((i,))

def indexToGroup(g):  # takes an index of a group and returns the actual group
    allG = list(powerset(range(m)))
    return allG[g]

def groupSize(g, q):  # check whether the group g is size q
    allG = list(powerset(range(m)))
    return(len(allG[g]) == q)


#
# Operations of profiles
#

def internsIndices(condition):  # return interns that satisfies the condition
    return [x for x in allInternsIndices() if condition(x)]

def internGroupsIndices(condition):  # return groups of interns that satisfy the condition
    return [x for x in allInternGroupsIndices() if condition(x)]

def hospitalsIndices(condition):  # return hospitals that satisfy the condition
    return [x for x in allHospitalsIndices() if condition(x)]

def internsPreferences(condition):  # return intern's prefeerences that satisfy the condition
    return [x for x in allInternsPreferences() if condition(x)]

def hospitalsPreferences(condition):  # return hospital's preferences that satisfy the condition
    return [x for x in allHospitalsPreferences() if condition(x)]

def hospitalsPreferences_R(condition):
    allHPrange, _ = allHospitalsResponsivePreferences()
    return [x for x in allHPrange if condition(x)]

def hospitalsCapacities(condition):  # return hospital's capacities that satisfy the condition
    return [c for c in range(m) if condition(c)]

def internsProfiles(condition):  # return profiles of interns that satisfy the condition
    return [x for x in allInternsProfiles() if condition(x)]

def hospitalsProfiles(condition):  # return profiles of hospitals that satisfy the condition
    return [x for x in allHospitalsProfiles() if condition(x)]
    
def hospitalsProfiles_R(condition):
    allRPs, _ = allHospitalsResponsiveProfiles()
    return [x for x in allRPs if condition(x)]

def iVariantsForInterns(i, p):  # return i-variants of the intern's profile p
    currpref = internsPrefId(i, p)
    factor = factorial(n+1) ** i
    rest = p - currpref * factor
    variants = []
    for newpref in internsPreferences(lambda newpref: newpref != currpref):
        variants.append(rest + newpref * factor)
    return variants

def iVariantsForHospitals(i, p):  # return i-variants of the hosputal's profile p
    currpref = hospitalsPrefId(i, p)
    factor = factorial(2**m) ** i
    rest = p - currpref * factor
    variants = []
    for newpref in hospitalsPreferences(lambda newpref: newpref != currpref):
        variants.append(rest + newpref * factor)
    return variants

def iVariantsForCapacities(i, q):  # return i-variants of the hospital's capacity vector q
    currcapa = hospitalsCapa(i, q) - 1
    factor = m ** i
    rest = q - currcapa * factor
    variants = []
    for newcapa in hospitalsCapacities(lambda newcapa: newcapa < currcapa):
        variants.append(rest + newcapa * factor)
    return variants

def iVariantsForHospitals_R(i, p):  # return i-variants of the hosputal's responsive profile p
    _, y = allHospitalsResponsiveProfiles()
    currpref = hospitalsPrefId_R(i, p)
    factor = len(y) ** i
    rest = p - currpref * factor
    variants = []
    for newpref in hospitalsPreferences_R(lambda newpref: newpref != currpref):
        variants.append(rest + newpref * factor)
    return variants


#
# Creating and Editing CNF
#

def posLiteral(p_H, p_I, p_q, h, g, allPH, allPI, allPQ):  # return a positive literal which represents that hospital h matches group of interns g in profile (p_H, p_I, p_q)
    p = (p_H * (allPH * allPI * allPQ)) + (p_I * (allPH * allPQ)) + p_q + 1
    return p * (n * (2**m)) + (h * (2**m)) + g + 1

def negLiteral(p_H, p_I, p_q, h, g, allPH, allPI, allPQ):  # return a negative literal which represents that hospital h doesn't match  group of interns g in profile (p_H, p_I, p_q)
    return (-1) * posLiteral(p_H, p_I, p_q, h, g, allPH, allPI, allPQ)

def interpretVariable(x, hospRespDict):  # interpret the literal and present it in a readable form
    g = (x-1) % (2**m)
    h = ((x - g - 1) % (n * (2**m))) // (2**m)
    p = ((x - h * (2**m) - g - 1)) // (n * (2**m))

    _, allRPrefH = allHospitalsResponsiveProfiles()
    allPH = (len(allRPrefH)) ** n
    allPI = (factorial(n+1)) ** m
    allPQ = m ** n
    p_q = (p-1) % allPQ
    p_I = ((p - p_q - 1) % (allPH * allPI * allPQ)) // (allPH * allPQ)
    p_H = (p - p_I * (allPH * allPQ) - p_q - 1) // (allPH * allPI * allPQ)

    pw = list(powerset(allInternsIndices()))
    print ('-> in profile number' + str(p_H) + ' , ' + str(p_I) + ' , ' + str(p_q) + ' match ' + str(h) + '/' + str(pw[g]))
    s_h = '( '
    s_q = ''
    for i in allHospitalsIndices():
        s_h = s_h + '>'.join([str(x) for x in hospitalsPrefList_R(i, p_H)]) + ' '
        s_q = s_q + str(hospitalsCapa(i, p_q)) + ' '
    s_h = s_h + ')'
    s_i = '( '
    for i in allInternsIndices():
        s_i = s_i + '>'.join([str(x) for x in internsPrefList(i, p_I)]) + ' '
    s_i = s_i + ')'
    print('-> where hospital profile ' + str(p_H) + ' = ' + s_h)
    print('-> where hospital capacity ' + str(p_q) + ' = ' + s_q)
    print('-> where intern profile ' + str(p_I) + ' = ' + s_i)

def printMechanism(mec):  # takes a Matching Mechanism and displays how Mechanism outputs to the profile 
    allRPH_range, allRPrefH = allHospitalsResponsiveProfiles()
    allPH = (len(allRPrefH)) ** n
    allPI = (factorial(n+1)) ** m
    allPQ = m ** n
    for h in allRPH_range:
        for q in allHospitalsCapacities():
            for i in allInternsProfiles():
                s = '( '
                for k in allHospitalsIndices():
                    s = s + '>'.join([str(x) for x in hospitalsPrefList_R(k, h)]) + '/Capacity:' + str(hospitalsCapa(k, q)) + ' '
                s = s + '| '
                for l in allInternsIndices():
                    s = s = '>'.join([str(x) for x in internsPrefList(l, i)]) + ' '
                s = s + ') --> { '
                for k in allHospitalsIndices():
                    for l in internsIndices(lambda o : posLiteral(h, i, q, k, l, allPH, allPI, allPQ) in mec):
                        s = s + str(k) + str(l) + ' '
                s = s + '}'
                print(s)

def subsetsOfInternGroupsIndices(g):  # return groups that are proper subsets of group g
    ans = []
    pw = list(powerset(allInternsIndices()))
    gPW = pw[g]
    for p in pw:
        if (p != gPW) and (p != ()):
            if set(p).issubset(gPW):
                ans.append(pw.index(p))
    return ans

def intersectionOfInternGroupsIndices(g):
    ans = []
    pw = list(powerset(allInternsIndices()))
    gPW = pw[g]
    for p in pw:
        if (p != gPW) and (p != ()):
            if set(p) & set(gPW):
                ans.append(pw.index(p))
    return ans

def cnfMechanism():  # a CNF to ensure that the Mechanism receives the Profile and returns Matching
    cnf = []
    pw = list(powerset(allInternsIndices()))
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H in allRPH_range:
        for p_q in allHospitalsCapacities():
            for p_I in allInternsProfiles():
                for h in allHospitalsIndices():
                    cnf.append([posLiteral(p_H, p_I, p_q, h, g, allPH, allPI, allPQ) for g in internGroupsIndices(lambda g : len(pw[g]) <= hospitalsCapa(h, p_q))])
                    for g1 in allInternGroupsIndices():
                        for g2 in internGroupsIndices(lambda g2 : g1 < g2):
                            cnf.append([negLiteral(p_H, p_I, p_q, h, g1, allPH, allPI, allPQ), negLiteral(p_H, p_I, p_q, h, g2, allPH, allPI, allPQ)])
                for g in allInternGroupsIndices():
                    if g:
                        for h1 in allHospitalsIndices():
                            for h2 in hospitalsIndices(lambda h2 : h1 < h2):
                                cnf.append([negLiteral(p_H, p_I, p_q, h1, g, allPH, allPI, allPQ), negLiteral(p_H, p_I, p_q, h2, g, allPH, allPI, allPQ)])
                        for g3 in intersectionOfInternGroupsIndices(g):
                            for h1 in allHospitalsIndices():
                                for h2 in hospitalsIndices(lambda h2 : h1 < h2):
                                    cnf.append([negLiteral(p_H, p_I, p_q, h1, g, allPH, allPI, allPQ), negLiteral(p_H, p_I, p_q, h2, g3, allPH, allPI, allPQ)])
                                    cnf.append([negLiteral(p_H, p_I, p_q, h2, g, allPH, allPI, allPQ), negLiteral(p_H, p_I, p_q, h1, g3, allPH, allPI, allPQ)])

    return cnf

def toNewLiteral(literal, dict):  # rename a literal according to dictionary "dict"
    if literal < 0:
        return  -1 *  dict[abs(literal)]
    else:
        return dict[literal]

def saveCNF(cnf, filename, dictfile):  # Save the CNF as file "filename" in DIMACS format. And save a dictionary of literal renaming to file "dict".
#    allPH = (factorial(2 ** m)) ** n
#    allPI = (factorial(n+1)) ** m
#    allPQ = m ** n
#    p = ((allPH-1) * (allPH * allPI * allPQ)) + ((allPI-1) * (allPH * allPQ)) + (allPQ-1) + 1
#    nvars = p * (n * (2**m)) + ((n-1) * (2**m)) + ((2**m)-1) + 1
#    nvars = (((factorial(2 ** m)) ** n) * (m ** n) * ((factorial(n+1)) ** m)) * n * (2 ** m)
    with open(filename, 'w') as file:
        with open(dictfile, 'wb') as dictF:
            mydict = defaultdict(lambda: len(mydict)+1)
            for c in cnf:
                for literal in c:
                    dum = mydict[abs(literal)]
            pickle.dump(dict(mydict), dictF)
            nvars = len(mydict)
            nclauses = len(cnf)
            file.write('p cnf ' + str(nvars) + ' ' + str(nclauses) + '\n')
            for c in cnf:
                file.write(' '.join([str(toNewLiteral(literal, mydict)) for literal in c]) + ' 0\n')


#
# Axioms
#

def cnfNotBlockedByInterns():  # CNF stating that the matching mechanism is not blocked by interns
    cnf = []
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H in allRPH_range:
        for p_q in allHospitalsCapacities():
            for p_I in allInternsProfiles():
                for h in allHospitalsIndices():
                    for i in internsIndices(lambda i : internsPrefers(i, -1, h, p_I)):
                        for g in internGroupsIndices(lambda g : inGroup(i, g)):
                            cnf.append([negLiteral(p_H, p_I, p_q, h, g, allPH, allPI, allPQ)])
    return cnf

def cnfNotBlockedByHospitals():  # CNF stating that the matching mechanism is not blocked by hospitals
    cnf = []
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H in allRPH_range:
        for p_q in allHospitalsCapacities():
            for p_I in allInternsProfiles():
                for h in allHospitalsIndices():
                    for i in internsIndices(lambda i : hospitalsPrefers_R(h, (), (i,), p_H)):
                        for g in internGroupsIndices(lambda g : inGroup(i, g)):
                            cnf.append([negLiteral(p_H, p_I, p_q, h, g, allPH, allPI, allPQ)])
    return cnf

def cnfIndividuallyRational():  # CNF stating that the matching mechanism is individually rational
    return cnfNotBlockedByInterns() + cnfNotBlockedByHospitals()

def cnfNotBlockedByHospitalInternPair_p():  # CNF stating that the matching mechanism is not blocked by hospital-intern pairs for hospuital's preferences
    cnf = []
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H in allRPH_range:
        for p_q in allHospitalsCapacities():
            for p_I in allInternsProfiles():
                for h1 in allHospitalsIndices():
                    for i1 in allInternsIndices():
                        for h2 in hospitalsIndices(lambda h2 : internsPrefers(i1, h1, h2, p_I)):
                            for i2 in internsIndices(lambda i2 : hospitalsPrefers_R(h1, (i1,), (i2,), p_H)):
                                for g1 in internGroupsIndices(lambda g1 : inGroup(i1, g1)):
                                    for g2 in internGroupsIndices(lambda g2 : inGroup(i2, g2)):
                                        cnf.append([negLiteral(p_H, p_I, p_q, h1, g2, allPH, allPI, allPQ), negLiteral(p_H, p_I, p_q, h2, g1, allPH, allPI, allPQ)])
    return cnf

def cnfNotBlockedByHospitalInternPair_c():  # CNF stating that the matching mechanism is not blocked by hospital-intern pairs for hospital's capacities
    cnf = []
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H in allRPH_range:
        for p_q in allHospitalsCapacities():
            for p_I in allInternsProfiles():
                for h1 in allHospitalsIndices():
                    for i in internsIndices(lambda i : hospitalsPrefers_R(h1, (i,), (), p_H)):
                        for h2 in hospitalsIndices(lambda h2 : internsPrefers(i, h1, h2, p_I)):
                            for g1 in internGroupsIndices(lambda g1 : groupSize(g1, hospitalsCapa(h1, p_q))):
                                for g2 in internGroupsIndices(lambda g2 : inGroup(i, g2)):
                                    cnf.append([posLiteral(p_H, p_I, p_q, h1, g1, allPH, allPI, allPQ), negLiteral(p_H, p_I, p_q, h2, g2, allPH, allPI, allPQ)])
    return cnf

def cnfNotBlockedByHospitalInternPair():  # CNF stating that the matching mechanism is not blocked by hospital-intern pairs
    return cnfNotBlockedByHospitalInternPair_p() + cnfNotBlockedByHospitalInternPair_c()

def cnfStable(): # CNF stating that the matching mechanism is stable
    return cnfIndividuallyRational() + cnfNotBlockedByHospitalInternPair()


def cnfStrategyProofForInterns():  # CNF stating that the matching mechanism is strategy-proof for interns
    cnf = []
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H in allRPH_range:
        for p_q in allHospitalsCapacities():
            for p_I_1 in allInternsProfiles():
                for h1 in allHospitalsIndices():
                    for i in allInternsIndices():
                        for p_I_2 in iVariantsForInterns(i, p_I_1):
                            for h2 in hospitalsIndices(lambda h2 : internsPrefers(i, h1, h2, p_I_1)):
                                for g in internGroupsIndices(lambda g : inGroup(i, g)):
                                    cnf.append([negLiteral(p_H, p_I_1, p_q, h2, g, allPH, allPI, allPQ), negLiteral(p_H, p_I_2, p_q, h1, g, allPH, allPI, allPQ)])
    return cnf

def cnfStrategyProofForHospitals():  # CNF stating that the matching mechanism is strategy-proof for hospitals
    cnf = []
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H_1 in allRPH_range:
        for p_q in allHospitalsCapacities():
            for p_I in allInternsProfiles():
                for h in allHospitalsIndices():
                    for g1 in allInternGroupsIndices():
                        for g2 in internGroupsIndices(lambda g2 : hospitalsPrefers_R(h, indexToGroup(g1), indexToGroup(g2), p_H_1)):
                            for p_H_2 in iVariantsForHospitals_R(h, p_H_1):
                                cnf.append([negLiteral(p_H_1, p_I, p_q, h, g2, allPH, allPI, allPQ), negLiteral(p_H_2, p_I, p_q, h, g1, allPH, allPI, allPQ)])
    return cnf

def cnfStrategyProofForCapacities():  # CNF stating that the matching mechanism is strategy-proof for capacities
    cnf = []
    allRPH_range, _ = allHospitalsResponsiveProfiles()
    allPH = len(allRPH_range)
    allPI = len(allInternsProfiles())
    allPQ = len(allHospitalsCapacities())
    for p_H in allRPH_range:
        for p_q_1 in allHospitalsCapacities():
            for p_I in allInternsProfiles():
                for h in allHospitalsIndices():
                    for p_q_2 in iVariantsForCapacities(h, p_q_1):
                        for g1 in allInternGroupsIndices():
                            for g2 in internGroupsIndices(lambda g2 : hospitalsPrefers_R(h, indexToGroup(g1), indexToGroup(g2), p_H)):
                                cnf.append([negLiteral(p_H, p_I, p_q_1, h, g2, allPH, allPI, allPQ), negLiteral(p_H, p_I, p_q_2, h, g1, allPH, allPI, allPQ)])
    return cnf

