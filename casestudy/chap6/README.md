# 6. 数理最適化APIとWebアプリの開発

## 6.1 導入

### Application Programming Interface, API

- 汎用性の高い機能を誰でも手軽に利用できるように提供される仕組み
- 利用者は公開されたAPIを通じて、欲しい機能を一から開発することなく使える
（利用者がAPIに対してリクエストを送ると何らかの処理を行なった上でレスポンスを返す）

- 基本的に利用者とのインタラクションは発生せず、データを送信したらデータが返却される

### Webアプリケーション

- ユーザー操作によるリクエストに応じて何らかのレスポンスを返す
- APIとの違いは、**Webブラウザの画面を介して**利用者が機能を操作する点
（人間とのインタラクションが必要になる）
- APIはWebアプリケーションの裏側で使用されることが多い

**フロントエンド**: Webアプリケーションにおいて目に見える部分
**バックエンド**: 画面の後側で動く機能（最適化サーバー等）

数理最適化エンジニアやDS（≠ソフトウェアエンジニア）がAPIやWebアプリを実装できるメリット

- スピード感を持って**概念実証（Proof of Concept, PoC）** を推進できる場面が増える
  - 検討→数理モデリング→アプリケーション を一気痛感して開発できる

- カウンターパート（数理モデル開発の依頼社）にプロトタイプを見せながら提案できる
- エンジニアと議論できるようになり、作業が効率化する
  - 開発フローを理解していると、モデリング側で何を決める必要があるかを議論できる

- プロダクトを俯瞰的に理解できるようになる

Webアプリケーションを利用するメリット

- 利用者は好きなタイミングで最適化結果を取得できる
- 開発者は手動で最適化する作業が不要になる

### 扱う問題

サークルにおける学生の乗車グループ分け問題

## 6.2 数理モデリングと実装

**0-1整数計画問題**: 学生をどの車に割り当てるか決定する

### 課題整理

1. 学生をどの車に割り当てるかを決定する
2. 乗車人数は定員を超えてはいけない
3. 運転免許証を持つ学生を1人以上車に割り当てる
4. 各学年の学生を1人以上車に割り当てる
5. 男女それぞれ1人以上を車に割り当てる

### データ確認

[EDA](eda.ipynb)

### モデルの実装

[実装例](model.py)

最適解が複数存在することに注意

## 6.3 最適化APIを作る

### 要件と仕様の定義

- 要件：APIに学生データと車データを投げると、学生の乗車グループ分け問題を解いた結果が得られる

- 使用
  - HTTPプロトコルによるAPIとの通信
    - リクエスト（入力）：学生データ、車データのcsv
    - レスポンス（出力）：最適化結果のcsv
  - 最適化を実行

### FlaskによるAPIの基礎

#### デコレータ

```
@foo
def bar():
    ...
```
は、`bar=foo(bar)` を意味する

```
@app.route("/api", methods=["POST"])    # ルーティング
def solve():
    ...
```
URL `/api` に対するPOSTリクエストを受け付けた際に、`solve()` 関数を実行する
`solve()` を `@app.route(...)` でラップしている

- ルーティング：処理とURL等のパスを紐づける機能
- HTTPメソッド `methods=["POST"]`：APIに対して何をして欲しいか
  - GET：画面に表示したいページを取得
    - URLの末尾にリクエストで送信するデータが付与される
  - POST：情報の送信
    - URLに含めずにデータを送信できる

## 6.4 Webアプリケーションを作る

