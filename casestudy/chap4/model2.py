import pulp
import pandas as pd
import time

cust_df = pd.read_csv("data/customers.csv")
prob_df = pd.read_csv("data/visit_probability.csv")

problem = pulp.LpProblem(name="DisCountCouponProblem2", sense=pulp.LpMaximize)

# (1)
I = cust_df["customer_id"].to_list()
S = prob_df["segment_id"].to_list()
M = [1, 2, 3]
xsm = {}
for s in S:
    for m in M:
        xsm[s,m] = pulp.LpVariable(name=f"xsm({s}, {m})", cat="Continuous")

# (2)
for s in S:
    problem += pulp.lpSum([xsm[s,m] for m in M]) == 1

# (3)
keys = ["age_cat", "freq_cat"]
cust_prob_df = pd.merge(cust_df, prob_df, on=keys)
Ns = cust_prob_df.groupby("segment_id")["customer_id"].count().to_dict()
prob_ver_df = prob_df.rename(columns={"prob_dm1":1, "prob_dm2":2, "prob_dm3":3})
prob_ver_df = prob_ver_df.melt(id_vars=["segment_id"], value_vars=[1,2,3], var_name="dm", value_name="prob")
Psm = prob_ver_df.set_index(["segment_id", "dm"])["prob"].to_dict()

problem += pulp.lpSum(Ns[s] * (Psm[s,m] - Psm[s,1]) * xsm[s,m] for s in S for m in [2, 3])

# (4)
Cm = {1:0, 2:1000, 3:2000}
problem += pulp.lpSum(Cm[m] * Ns[s] * Psm[s,m] * xsm[s,m] for s in S for m in [2,3]) <= 1000000

# (5)
for s in S:
    for m in M:
        problem += xsm[s,m] >= 0.1

# solve
time_start = time.time()
status = problem.solve()
time_stop = time.time()
print(pulp.LpStatus[status])
print(f"objective: {pulp.value(problem.objective):.4}")
print(f"{time_stop-time_start:.3} s")

send_dm_df = pd.DataFrame([[xsm[s,m].value() for m in M] for s in S], columns=["send_dm1", "send_dm2", "send_dm3"])
send_dm_df.to_csv("send_dm2.csv")