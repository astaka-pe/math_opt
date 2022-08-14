import pulp
import pandas as pd
import time

MAX_LOWERBOUND = 0.1313

cust_df = pd.read_csv("data/customers.csv")
prob_df = pd.read_csv("data/visit_probability.csv")

cost_list = []              # キャンペーン費用
cpa_list = []               # 来店数1人当たりの獲得費用
inc_action_list = []        # 来客増加数

print("status, cost, 来客増加数, CPA")

for cost in range(761850, 3000000, 100000):
    problem = pulp.LpProblem(name="DisCountCouponProblem2", sense=pulp.LpMaximize)
    # (1)
    I = cust_df["customer_id"].to_list()
    S = prob_df["segment_id"].to_list()
    M = [1, 2, 3]
    xsm = {}
    for s in S:
        for m in M:
            xsm[s,m] = pulp.LpVariable(name=f"xsm({s}, {m})", lowBound=0, upBound=1, cat="Continuous")

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
    problem += pulp.lpSum(Cm[m] * Ns[s] * Psm[s,m] * xsm[s,m] for s in S for m in [2,3]) <= cost

    # (5)
    for s in S:
        for m in M:
            problem += xsm[s,m] >= 0.1

    # solve
    status = problem.solve(pulp.PULP_CBC_CMD(msg=0))
    cpa = cost / pulp.value(problem.objective)
    inc_action = pulp.value(problem.objective)
    cost_list.append(cost)
    cpa_list.append(cpa)
    inc_action_list.append(inc_action)
    print("{}, {}, {:.4}, {:.5}".format(pulp.LpStatus[status], cost, inc_action, cpa))
    
    # send_dm_df = pd.DataFrame([[xsm[s,m].value() for m in M] for s in S], columns=["send_dm1", "send_dm2", "send_dm3"])
    # send_dm_df.to_csv("send_dm2.csv")

import json
result = {"cost_list":cost_list, "cpa_list":cpa_list, "inc_action_list":inc_action_list}
with open("model4.json", mode="w") as f:
    json.dump(result, f)