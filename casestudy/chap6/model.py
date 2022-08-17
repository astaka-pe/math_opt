import pandas as pd
from pulp import *

students_df = pd.read_csv("data/resource/students.csv")
cars_df = pd.read_csv("data/resource/cars.csv")

prob = LpProblem("ClubCarProblem", LpMinimize)

S = students_df["student_id"].to_list()
C = cars_df["car_id"].to_list()
G = [1, 2, 3, 4]
SC = [(s,c) for s in S for c in C]
S_license = students_df[students_df["license"]==1]["student_id"]
S_g = {g: students_df[students_df["grade"]==g]["student_id"] for g in G}
S_male = students_df[students_df["gender"]==0]["student_id"]
S_female = students_df[students_df["gender"]==1]["student_id"]
U = cars_df["capacity"].to_list()

x = LpVariable.dicts("x", SC, cat="Binary")

for s in S:
    prob += lpSum(x[s,c] for c in C) == 1

for c in C:
    prob += lpSum(x[s,c] for s in S) <= U[c]

for c in C:
    prob += lpSum(x[s,c] for s in S_license) >= 1

for c in C:
    for g in G:
        prob += lpSum(x[s,c] for s in S_g[g]) >= 1

for c in C:
    prob += lpSum(x[s,c] for s in S_male) >= 1
    prob += lpSum(x[s,c] for s in S_female) >= 1

status = prob.solve()
print(LpStatus[status])

c2s = {c: [s for s in S if x[s,c].value()==1] for c in C}
max_people = dict(zip(cars_df["car_id"], cars_df["capacity"]))

for c, ss in c2s.items():
    print("CarID:", c)
    print("NumS:", len(ss), "maxP:", max_people[c])
    print("S:", ss)