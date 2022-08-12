# 2. Python数理最適化チュートリアル

## 2.1 連立一次方程式をPuLPで解く

$$
\begin{align}
120x + 150y &= 1440\\
x + y &= 10
\end{align}
$$

```
import pulp
problem = pulp.LpProblem("SLE", pulp.LpMaximize)
```

- "SLE"は任意の名前で良い（Simultaneous Linear Equation）
- `pulp.LpMaximize`: 最大化問題を解くという指定（今回は特に意味はない）
- 連立一次方程式は、**線形計画問題の目的関数が定数の場合**に含まれるので、線形計画問題として解ける（後述）

```
x = pulp.LpVariable("x", cat="Continuous")
y = pulp.LpVariable("y", cat="Continuous")
```

- 変数x, yを定義（第1引数は任意の名前）
- 第2引数 `Continuous`: 変数が連続変数であることを指定
    - 整数計画問題の場合には `Integer` を指定
```
problem += 120 * x + 150 * y == 1440
# problem.addConstraint(120 * x + 150 * y == 1440) でも良い
problem += x + y == 10
```

- 数理モデル `problem` に制約式を加える

```
status = problem.solve()
print(pulp.LpStatus[status])
```

解けたか解けなかったかがstatusに返る（最適解を得られていれば`Optimal`）

```
print(x.value(), y.value())
```

## 2.2 線形計画問題をPuLPで解く

線形計画問題：領域の最大・最小

$$
\begin{align}
x + 3y \leq 30\\
2x + y \leq 40\\
x \geq 0, y \geq 0\\
\max (x+2y)
\end{align}
$$

```
problem += x + 3 * y <= 30
problem += 2 * x + y <= 40
problem += x >= 0
problem += y >= 0
problem += x + 2 * y
# problem.setObjective(x + 2 * y) でも良い
```

右辺が制約式であれば**制約**を追加し、関数であれば**目的関数**を定義する

```
status = problem.solve()
print(x.value(), y.value(), problem.objective.value())
```

### 数理最適化モデルの分類

- 線形計画問題：変数が実数値をとる問題（生産量）
- 整数計画問題：変数が整数値をとる問題（個数）
- 混合整数計画問題：整数計画問題の一部の変数が実数値をとる問題（生産量と個数）
- 0-1整数計画問題：変数が0か1をとる問題（割り当て）
- 凸二次計画問題：目的関数に凸な二次関数が現れる問題（二乗誤差の最小化）

## 2.3 規模の大きな数理最適化問題をPuLPで解く

変数や制約式の定義を1つずつ定義するのではなく、まとめて定義する

**リスト・定数・変数**を準備した上で、**制約式**と**目的関数**を定める

- リスト（入力）
  - 製品、原料のリスト
- 定数（入力）
  - 原料の在庫量
  - 製品を生産するのに必要な原料の量
  - 製品を生産したときの利得
- 変数（出力）
  - 製品の生産量
- 制約式（関数定義）
  - 製品の生産量は0以上
  - 使用する減量は在庫の範囲で
- 目的関数（関数定義）

```
# P = ["p1", "p2", "p3", "p4"]
# M = ["m1", "m2", "m3"]
```
データの前処理にはデータフレームを利用し、数理モデルの定義には辞書を利用する

```
# 変数の定義
x = pulp.LpVariable.dicts("x", P, cat="Continuous)

# 制約式の定義
for p in P:
    problem += x[p] >= 0

for m in M:
    # pulp.lpSumはsumと同じだがより高速に計算できる
    problem += pulp.lpSum([require[p, m] * x[p] for p in P]) <= stock[m]

# 目的関数
problem += pulp.lpSum([gain[p] * x[p] for p in P])
```

線形計画問題よりも整数計画問題の方が難しい。
線形計画問題で解いて解を丸める方法（連続緩和）は実務において有効な方法。