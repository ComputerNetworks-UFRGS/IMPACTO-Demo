import math

alpha = 0.001
def EBIS(v, l, z):
    return (v-v/(1+z/(l*alpha)))*l

def ENBIS(v, l, z):
    return EBIS(v, l, z) - z

def gordon_loeb_perfect(v, l):
    return l*(math.sqrt(v*alpha) - alpha)

def EBIS_BPF(v, l, z):
    return (v-v/(0.5+z/(l*alpha)))*l

def ENBIS_BPF(v, l, z):
    return EBIS_BPF(v, l, z) - z

def gordon_loeb_perfect_BPF(v, l):
    return l*(math.sqrt(v*alpha) - alpha/2)

"""
v = 0.21
l = 2000000

perfect_z = gordon_loeb_perfect(v, l)
print("S(Slides)")
for i in range(11):
    if i == 5:
        print("EBIS = ", EBIS(v, l, perfect_z - 500 + 100*i),"\tENBIS = " , ENBIS(v, l, perfect_z - 500 + 100*i), "\tz = ", perfect_z,  "\t<- Perfect")
    else:
        print("EBIS = ", EBIS(v, l, perfect_z - 500 + 100*i),"\tENBIS = " , ENBIS(v, l, perfect_z - 500 + 100*i), "\tz = ", perfect_z - 500 + 100*i)
        
perfect_z = gordon_loeb_perfect_BPF(v, l)
print("S(SECAdvisor)")
for i in range(11):
    if i == 5:
        print("EBIS = ", EBIS_BPF(v, l, perfect_z - 500 + 100*i),"\tENBIS = " , ENBIS_BPF(v, l, perfect_z - 500 + 100*i), "\tz = ", perfect_z,  "\t<- Perfect")
    else:
        print("EBIS = ", EBIS_BPF(v, l, perfect_z - 500 + 100*i),"\tENBIS = " , ENBIS_BPF(v, l, perfect_z - 500 + 100*i), "\tz = ", perfect_z - 500 + 100*i)
"""