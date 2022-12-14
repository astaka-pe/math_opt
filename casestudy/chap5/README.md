# 5. コストを最小化する輸送車両の配送計画

## 5.1 導入

利益率の高くないビジネスでは、売上の最大化だけでなくコスト削減も重要

**配送計画問題（vehicle routing problem, VRP）**：車両を用いて複数の荷物を配送する際の経路最適化

考慮する内容

- 利用できる車両台数
- 積載量などの物理的な制約
- 荷物ごとの輸送車両の指定
- 受け取り時間の指定
- 混載不可の商品ペア
- 運転手の連続運転時間などの労働・交通関係の法規則

VRPのほとんどは**NP困難**

- 大規模問題に対して厳密解の算出が厳しい
- 単一拠点・単一車両で移動時間を最小化する**巡回セールスマン問題(TSP)** ですらNP困難
  - [部分巡回路除去制約付きTSPの実装](../../theory/chap4/note/TSP_check.ipynb)
- **ヒューリスティック解法**の検討も必要

**混合整数計画問題**によるモデリング

- 現実的な時間での最適化が可能になる場合があること
- 補助変数の用い方
- 巡回セールスマン問題のMTZ定式化

## 5.2 課題整理

顧客：自社倉庫から車で2~3時間圏内に点在する工場
自社のトラック1台を使って顧客に荷物を届けている

- 最適化対象期間：1ヶ月
- 注文関連の要件：指定された期間内に配達
- 配送関連の要件：
  - 最大積載量
  - 残業代
  - 残業時間の制約
  - 外部委託費用
- 最小化指標：配送コスト（外注費、残業代）

## 5.3 数理モデリング

### 5.3.1 パラメータの整理

1. 最適化対象期間：D=20程度
2. 地理：
    - 地点の集合：K
    - 自社拠点を表す地点：o
    - 移動時間：t[k][l]

3. 注文
    - 注文集合：R
      - 届け先地点：k[r]
      - 配送指定期間：d[r]
      - 重量：w[r]
      - 外注したときの費用：f[r]

4. トラックの運用
    - 所定労働時間：H0
    - 最大積載重量：W
    - 1時間当たりの残業代：c
    - 最大残業時間：H1

### 5.3.2 混合整数計画問題による素朴なモデリング

**混合整数計画問題（Mixed Integer Programming, MIP）**：線形計画問題の一部の変数が整数値をとる

- 決定変数：トラックの移動を表現する変数
- 補助変数：移動の順序を表現する変数
- 決定変数：自社トラックによる配送の有無を表現する変数
- 補助変数：日別の残業時間を表現する変数

**決定変数**：独立した変数として定義する必要のあるもの
**補助変数**：決定変数から算出可能である変数

#### 要件

1. 1日の移動経路の整合性

    - 移動経路は0個以上のサイクルからなる
      - 地点lに向かう移動は、高々1つしか許されない
      - 地点lに向かう移動の有無は、地点lを出る移動の有無と一致する
    - 配送拠点oを通らないサイクルの除去（MTZ定式化）

2. 同一注文の複数回配送の禁止
3. 移動経路上以外での配送禁止
4. 積載上限を超えない
5. 最大残業時間を超えない
6. 注文は配送指定期間内に届ける
7. 配送費用の最小化

### 5.3.3 補助変数の役割

### 5.3.4 数理モデルの検証と改善

素朴な方法では、現実時間で最適解を得ることはできない
実行可能解も明らかに無駄のある経路を出力する

対応：

1. ビジネス課題レベルでのモデリングを見直す
2. **数理最適化問題としてのモデリング（数式の書き方）を見直す**
3. より高性能なソルバーを導入する
4. CPUを増強する
5. 実行時間を長くする

複数日で相互に関連する難しい問題となっていたのが計算時間増大の一因
→ 日毎にスケジュールを事前に列挙しておく

## 5.4 実装と数値実験

### 移動経路の列挙

どのような移動経路を通り、どの荷物を配送するか
日付を問わず共通となる移動経路を列挙する

- 全ての考えられる配送先集合に対して、配送先集合だけを通る移動経路で移動時間が上限に満たないものを全て列挙する
- 1つの配送先集合に対して、最短の移動経路だけを残す

`K_minus_o` **の全ての部分集合について、それらを訪問する最短経路を算出する**

- 巡回セールスマン問題をMTZ定式化でモデリングする

訪問先の工場が9地点ある

- 移動経路の数は $2^9=512$ 通り
- 残業時間の制約により実行不可能となる経路を除去

### 日毎のスケジュールを列挙

**移動経路上で配送可能な荷物の部分集合**であって**重量制限を守れるもの**を列挙する

配送可能な荷物の部分集合

- 再帰的列挙：**ある荷物の集合が重量制約に違反するならば、その集合に別の荷物を追加したものも重量制約に違反する**

