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