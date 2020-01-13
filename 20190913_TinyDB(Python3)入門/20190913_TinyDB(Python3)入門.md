[:contents]

Pythonで使える軽量なNoSQLデータベースないかなあと思って調べていたところ良さそうなものがあったので，忘れないようにとの意味も込めて書きます．

# はじめに
本エントリでは，TinyDBの活用方法について説明します．  
本エントリの内容は[TinyDBの公式ドキュメント](https://tinydb.readthedocs.io/en/latest/index.html)に基づいています．

# 環境
本エントリ内で記述してあるコードは，以下の環境において正しく動作することを確認しています．
```
$ python --version
Python 3.7.3

$ pip freeze | grep tinydb
tinydb==3.13.0
```

# 概要
[TinyDB](https://github.com/msiemens/tinydb/wiki)はpureなPythonで記述されたドキュメント志向型のNoSQLデータベースです．  
非常に軽量であり，別途データベース用のサーバ等も準備する必要がない一方で，データ操作のためのクエリを実行するためのAPIが豊富に用意されています．  
ただし，ACID特性に対する保証がないことやマルチスレッド環境への対応がなされていない等の欠点もあります．

# インストール
下記のコマンドでインストール可能です．
```
$ pip install tinydb
```

# 基本的なTinyDBの操作
## TL;DR
|コード|概要|
|:-:|:-|
|`db = TinyDB(filename)`|データを格納するファイルを選択した上でTinyDBのインスタンスを生成|
|`query = Query()`|`Query`インスタンスを生成|
|`db.insert(document)`|ドキュメントを追加|
|`db.all()`|ドキュメントを全件取得|
|`db.search(query)`|`query`の条件に一致するドキュメントを全件取得|
|`db.contains(query)`|`query`の条件に一致するドキュメントが存在するかを検査|
|`db.count(query)`|`query`の条件に一致するドキュメントの件数を調査|
|`db.update(fields, query)`|`query`の条件に一致するドキュメントを`fields`の内容で更新(`query`を省略すると全件更新)|
|`db.purge()`|ドキュメントを全件削除|
|`db.remove(query)`|`query`の条件に一致するドキュメントを全件削除|

## 解説
### 下準備
必要なモジュールをインポートします．
```python
from tinydb import TinyDB, Query
```

### インスタンス生成
データを格納するファイル名を指定した上でTinyDBのインスタンスを生成します．
```python
db = TinyDB("db.json")
```

### 追加
ドキュメントを追加します．
```python
db.insert({"name": "foo", "age": 20})
db.insert({"name": "bar", "age": 30})
```

### 全件取得
データを全件取得するには`TinyDB.all()`を使います．
```python
db.all()

# [{'name': 'foo', 'age': 20}, {'name': 'bar', 'age': 30}
```

### iter
イテレータとして用いることも可能です．
```python
for document in db:
    print(document)

# {'name': 'foo', 'age': 20}
# {'name': 'bar', 'age': 30}
```

### クエリ
クエリを指定してデータを抽出するときは，`Query`インスタンスを生成した上で条件を指定します．
```python
query = Query()
db.search(query.name == "foo")

# [{'name': 'foo', 'age': 20}]
```

### 演算子
`==`以外の演算子も利用可能です．
```python
db.search(query.age > 25)

# [{'name': 'bar', 'age': 30}]
```

### 存在可否と件数
`contains`を使うことで，クエリの条件に一致するドキュメントが存在するかを調べることができます．
また，`count`を使うことで，クエリの条件に一致するドキュメントが何件存在するかを調べることができます．
```python
db.contains(query.age > 40)

# False
```

```python
db.count(query.age < 40)

# 2
```

### 更新と削除
クエリの条件に一致するドキュメントのデータを更新したり削除したりすることもできます．
```python
db.update({"age": 40}, query.name == "bar")
db.search(query.name == "bar")

# [{'name': 'bar', 'age': 40}]
```

```python
db.remove(query.name == "foo")
db.all()

# [{'name': 'bar', 'age': 40}]
```

### 全件削除
`purge()`を呼び出すとドキュメントを全削除できます．
```python
db.purge()
db.all()

# []
```

## まとめ
```python
# 必要なライブラリのインポート
from tinydb import TinyDB, Query

# TinyDBインスタンスの生成
db = TinyDB("db.json")

# ドキュメントの追加
db.insert({"name": "foo", "age": 20})
db.insert({"name": "bar", "age": 30})

# 全件取得
print(db.all())

# イテレータとして取得
for document in db:
    print(document)

# クエリの活用
query = Query()
db.search(query.name == "foo")
db.search(query.age > 25)

# 存在可否と件数
db.contains(query.age > 40)
db.count(query.age < 40)

# ドキュメントの更新
db.update({"age": 40}, query.name == "bar")
db.search(query.name == "bar")

# ドキュメントの削除
db.remove(query.name == "foo")
db.all()

# ドキュメント全削除
db.purge()
db.all()
```

## Appendix
### テーブル
TinyDBでは，`TinyDB.table`を用いて複数のテーブルを同時に管理することができます． 
ただし，何も指定しない場合は`_default`という名前のテーブルがデフォルトで指定されます． 
操作方法は以下の通りです．

|コード|概要|
|:-:|:-|
|`table = TinyDB.table(name)`|指定した名前でテーブルを新規に生成|
|`db.tables()`|テーブル一覧を取得|
|`db.purge_table(name)`|指定したテーブルを削除|
|`db.purge_tables()`|テーブルを全件削除|

`table`インスタンスに対する操作は`TinyDB`インスタンスに対する操作と同様であるため説明は省略します．

### MemoryStorage
`TinyDB`インスタンス生成時に，インメモリのストレージを指定することができます．
```python
db = TinyDB(memory=MemoryStorage)
```

# 応用的なTinyDBの操作
## TL;DR
|コード|概要|
|:-:|:-|
|`db.search(where(field) == foo)`|`tinydb.where`を用いたクエリ|
|`db.search(query.field.exists())`|`field`が存在するドキュメントを抽出|
|`db.search(query.field.test(func, args, ...))`|クエリに独自の関数を利用して抽出|
|`db.search(query.field.any(list))`|`field`が`list`の要素を1つでも含んでいるドキュメントを抽出|
|`db.search(query.field.all(list))`|`field`が`list`の要素を全て含んでいるドキュメントを抽出
|`db.search(query.field.any(cond))`|`field`が`cond`の条件と部分的にでも一致しているドキュメントを抽出|
|`db.search(query.field.all(cond))`|`field`が`cond`の条件と完全に一致しているドキュメントを抽出|
|`db.search(~ query)`|否定(クエリに一致しないドキュメントを抽出)|
|`db.search(query1 & query2)`|論理積(両方のクエリに一致するドキュメントを抽出)|
|`db.search(query1 \| query2)`|論理和(少なくとも片方のクエリに一致するドキュメントを抽出)|
|`db.write_back(docs)`|指定した`docs`でデータベースを更新|

## 説明
### 下準備
```python
from tinydb import TinyDB, Query, where

db = TinyDB("db.json")

db.insert({
    "name": "foo",
    "birthday": {
        "year": 2000,
        "month": 1,
        "day": 10
    },
    "leader": "yes",
    "hobbies": ["sport", "movie", "walking"]
})

db.insert({
    "name": "bar",
    "birthday": {
        "year": 1990,
        "month": 2,
        "day": 20
    },
    "hobbies": ["movie", "walking", "programming"]
})

db.insert({
    "name": "baz",
    "birthday": {
        "year": 1980,
        "month": 3,
        "day": 30
    },
    "hobbies": ["swimming"]
})
```

### where
`where`を用いてクエリを構成できます．
```python
db.search(where("name") == "foo")

# [{'name': 'foo', 'birthday': {'year': 2000, 'month': 1, 'day': 10}, 'leader': 'yes', 'hobbies': ['sport', 'movie', 'walking']}]
```

### exists
`exists()`を使うと，その`field`が存在するドキュメントのみを抽出できます．
```python
db.search(query.leader.exists())

# [{'name': 'foo', 'birthday': {'year': 2000, 'month': 1, 'day': 10}, 'leader': 'yes', 'hobbies': ['sport', 'movie', 'walking']}]
```

### 独自関数
クエリに独自関数を用いることもできます．
```python
f = lambda v, l, r: l <= v <= r
db.search(query.birthday.year.test(f, 1975, 1995))

# [
#     {'name': 'bar', 'birthday': {'year': 1990, 'month': 2, 'day': 20}, 'hobbies': ['movie', 'walking', 'programming']}, 
#     {'name': 'baz', 'birthday': {'year': 1980, 'month': 3, 'day': 30}, 'hobbies': ['swimming']}
# ]
```

### any
`any`を用いることで，ドキュメントの特定のfieldの要素に，指定されたリストの要素が1つでも含まれている場合に，そのドキュメントを抽出することができます．
```python
db.search(query.hobbies.any(["sport", "movie", "programming"]))

# [
#     {'name': 'foo', 'birthday': {'year': 2000, 'month': 1, 'day': 10}, 'leader': 'yes', 'hobbies': ['sport', 'movie', 'walking']}, 
#     {'name': 'bar', 'birthday': {'year': 1990, 'month': 2, 'day': 20}, 'hobbies': ['movie', 'walking', 'programming']}
# ]
```

### all
`all`を用いることで，ドキュメントの特定のfieldの要素に，指定されたリストの要素が全て含まれている場合に，そのドキュメントを抽出することができます．
```python
db.search(query.hobbies.all(["sport", "movie", "walking"]))

# [{'name': 'foo', 'birthday': {'year': 2000, 'month': 1, 'day': 10}, 'leader': 'yes', 'hobbies': ['sport', 'movie', 'walking']}]
```

### 論理演算子
クエリに論理演算子を用いることもできます．
```python
db.search(~ query.leader.exists())

# [
#     {'name': 'bar', 'birthday': {'year': 1990, 'month': 2, 'day': 20}, 'hobbies': ['movie', 'walking', 'programming']}, 
#     {'name': 'baz', 'birthday': {'year': 1980, 'month': 3, 'day': 30}, 'hobbies': ['swimming']}
# ]
```

```python
db.search((query.birthday.year == 2000) | query.hobbies.any(["movie"]))

# [
#     {'name': 'foo', 'birthday': {'year': 2000, 'month': 1, 'day': 10}, 'leader': 'yes', 'hobbies': ['sport', 'movie', 'walking']}, 
#     {'name': 'bar', 'birthday': {'year': 1990, 'month': 2, 'day': 20}, 'hobbies': ['movie', 'walking', 'programming']}
# ]
```

```python
db.search((query.birthday.year == 2000) & query.hobbies.any(["movie"]))

# [{'name': 'foo', 'birthday': {'year': 2000, 'month': 1, 'day': 10}, 'leader': 'yes', 'hobbies': ['sport', 'movie', 'walking']}]
```

### write_back
`write_back`を用いることで，操作したデータの置換を容易に行うことができます．
```python
documents = db.search(query.hobbies.any("walking"))
for document in documents:
    document["hobbies"].append("running")
db.write_back(documents)

db.search(query.hobbies.any("running"))

# [
#     {'name': 'foo', 'birthday': {'year': 2000, 'month': 1, 'day': 10}, 'leader': 'yes', 'hobbies': ['sport', 'movie', 'walking', 'running']}, 
#     {'name': 'bar', 'birthday': {'year': 1990, 'month': 2, 'day': 20}, 'hobbies': ['movie', 'walking', 'programming', 'running']}
# ]
```

## まとめ
```python
# 必要なライブラリのインポート
from tinydb import TinyDB, Query, where

# TinyDB, Queryインスタンスの生成
db = TinyDB("db.json")
query = Query()

# データの下準備
db.insert({
    "name": "foo",
    "birthday": {
        "year": 2000,
        "month": 1,
        "day": 10
    },
    "leader": "yes",
    "hobbies": ["sport", "movie", "walking"]
})

db.insert({
    "name": "bar",
    "birthday": {
        "year": 1990,
        "month": 2,
        "day": 20
    },
    "hobbies": ["movie", "walking", "programming"]
})

db.insert({
    "name": "baz",
    "birthday": {
        "year": 1980,
        "month": 3,
        "day": 30
    },
    "hobbies": ["swimming"]
})

# whereを用いたクエリ
print(db.search(where("name") == "foo"))

# 特定のフィールドを持つドキュメントの抽出
print(db.search(query.leader.exists()))

# クエリへの独自関数の利用
f = lambda v, l, r: l <= v <= r
print(db.search(query.birthday.year.test(f, 1975, 1995)))

# anyとall
print(db.search(query.hobbies.any(["sport", "movie", "walking"])))
print(db.search(query.hobbies.all(["sport", "movie", "walking"])))

# 論理演算子
print(db.search(~ query.leader.exists()))
print(db.search((query.birthday.year == 2000) | query.hobbies.any(["movie"])))
print(db.search((query.birthday.year == 2000)))

# write_backを用いたデータの操作
documents = db.search(query.hobbies.any("walking"))
for document in documents:
    document["hobbies"].append("running")
db.write_back(documents)
print(db.search(query.hobbies.any("running")))
```

## おわりに
TinyDBの基本的な操作方法について解説しました．  
ここで説明したこと以外にも，データを操作するための様々なAPIや，MiddlewareやStorageあたりをいい感じに拡張するための仕様が準備されているので，興味があれば調べてみてください．