import pulp
import pandas as pd

s_df = pd.read_csv("data/students.csv")
s_pair_df = pd.read_csv("data/student_pairs.csv")
prob = pulp.LpProblem("ClassAsignment", pulp.LpMaximize)

# 生徒リスト
S = s_df["student_id"].tolist()
S_male = s_df["student_id"][s_df["gender"]==1].tolist()
S_female = s_df["student_id"][s_df["gender"]==0].tolist()
S_leader = s_df["student_id"][s_df["leader_flag"]==1].tolist()
S_support = s_df["student_id"][s_df["support_flag"]==1].tolist()
SS = [(row.student_id1, row.student_id2) for row in s_pair_df.itertuples()]

# クラスリスト（ハードコーディングxxx）
C = ["A", "B", "C", "D", "E", "F", "G", "H"]
class_dic = {0:"A", 1:"B", 2:"C", 3:"D", 4:"E", 5:"F", 6:"G", 7:"H"}

# 生徒とクラスのペアのリスト（変数）
SC = [(s, c) for s in S for c in C]
x = pulp.LpVariable.dicts("x", SC, cat="Binary")

# 学力順位を付与 & 初期クラス編成
s_df["score_rank"] = s_df["score"].rank(ascending=False, method="first")
s_df["init_assigned_class"] = s_df["score_rank"].map(lambda x:x % 8).map(class_dic)
init_flag = {(s,c):0 for s in S for c in C}
for row in s_df.itertuples():
    init_flag[row.student_id, row.init_assigned_class] = 1


""" 要件実装 """
# (1) 各生徒は1つのクラスに割り当てる
for s in S:
    prob += pulp.lpSum([x[s, c] for c in C]) == 1

# (2) 各クラスの生徒の人数は39人以上、40人以下とする
for c in C:
    prob += pulp.lpSum([x[s, c] for s in S]) >= 39
    prob += pulp.lpSum([x[s, c] for s in S]) <= 40

# (3) 各クラスの男子生徒、女子生徒の人数は20人以下とする
for c in C:
    prob += pulp.lpSum([x[s, c] for s in S_male]) <= 20
    prob += pulp.lpSum([x[s, c] for s in S_female]) <= 20

# (4) 各クラスの平均点が学年平均点+-10点とする
score = {row.student_id:row.score for row in s_df.itertuples()}
score_mean = s_df["score"].mean()
for c in C:
    prob += pulp.lpSum([x[s, c]*score[s] for s in S]) <= (score_mean + 10) * pulp.lpSum([x[s, c] for s in S])
    prob += pulp.lpSum([x[s, c]*score[s] for s in S]) >= (score_mean - 10) * pulp.lpSum([x[s, c] for s in S])

# (5) 各クラスにリーダー気質の生徒を2人以上割り当てる
for c in C:
    prob += pulp.lpSum([x[s, c] for s in S_leader]) >= 2

# (6) 特別な支援が必要な生徒は各クラスに1人以下とする
for c in C:
    prob += pulp.lpSum([x[s, c] for s in S_support]) <= 1

# (7) 特定ペアの生徒は同一クラスに割り当てない
for s1, s2 in SS:
    for c in C:
        prob += x[s1, c] + x[s2, c] <= 1

# 目的関数：初期クラス編成とできるだけ一致させる
prob += pulp.lpSum(x[s, c] * init_flag[s, c] for s, c in SC)

""" solve """
status = prob.solve()
print(status)
print(pulp.LpStatus[status])

""" 最適化結果の表示 """
C2Ss = {}
for c in C:
    C2Ss[c] = [s for s in S if x[s, c].value()==1]

for c, Ss in C2Ss.items():
    print("Class:", c)
    print("Num:", len(Ss))
    print("Student: ", Ss)
    print()

result_df = s_df.copy()
S2C = {s:c for s in S for c in C if x[s, c].value()==1}
result_df["assigned_class"] = result_df["student_id"].map(S2C)

result_df.to_csv("data/sc2.csv")