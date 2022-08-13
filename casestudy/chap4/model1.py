import pulp
import pandas as pd
import time

cust_df = pd.read_csv("data/customers.csv")
prob_df = pd.read_csv("data/visit_probability.csv")

problem = pulp.LpProblem(name="DisCountCouponProblem1", sense=pulp.LpMaximize)

# (1)
I = cust_df["customer_id"].to_list()
M = [1, 2, 3]
xim = {}
for i in I:
    for m in M:
        xim[i,m] = pulp.LpVariable(name=f"xim({i}, {m})", cat="Binary")

# (2)
for i in I:
    problem += pulp.lpSum([xim[i,m] for m in M]) == 1

# (3)
keys = ["age_cat", "freq_cat"]
cust_prob_df = pd.merge(cust_df, prob_df, on=keys)
cust_prob_ver_df = cust_prob_df.rename(columns={"prob_dm1":1, "prob_dm2":2, "prob_dm3":3})
cust_prob_ver_df = cust_prob_ver_df.melt(id_vars=["customer_id"], value_vars=[1,2,3], var_name="dm", value_name="prob")
Pim = cust_prob_ver_df.set_index(["customer_id", "dm"])["prob"].to_dict()

problem += pulp.lpSum((Pim[i,m] - Pim[i,1]) * xim[i,m] for i in I for m in [2, 3])

# (4)
Cm = {1:0, 2:1000, 3:2000}
problem += pulp.lpSum(Cm[m] * Pim[i,m] * xim[i,m] for i in I for m in [2,3]) <= 1000000

# (5)
S = prob_df["segment_id"].to_list()
Ns = cust_prob_df.groupby("segment_id")["customer_id"].count().to_dict()
Si = cust_prob_df.set_index("customer_id")["segment_id"].to_dict()
for s in S:
    for m in M:
        problem += pulp.lpSum(xim[i,m] for i in I if Si[i] == s) >= 0.1 * Ns[s]

# solve
time_start = time.time()
status = problem.solve()
time_stop = time.time()
print(pulp.LpStatus[status])
print(f"ovjective: {pulp.value(problem.objective):.4}")
print(f"{time_stop-time_start:.3} s")

send_dm_df = pd.DataFrame([[xim[i,m].value() for m in M] for i in I], columns=["send_dm1", "send_dm2", "send_dm3"])
send_dm_df.to_csv("send_dm1.csv")