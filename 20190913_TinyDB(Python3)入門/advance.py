from tinydb import TinyDB, Query, where

db = TinyDB("db.json")
query = Query()

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

print(db.search(where("name") == "foo"))

print(db.search(query.leader.exists()))

f = lambda v, l, r: l <= v <= r
print(db.search(query.birthday.year.test(f, 1975, 1995)))

print(db.search(query.hobbies.any(["sport", "movie", "walking"])))
print(db.search(query.hobbies.all(["sport", "movie", "walking"])))

print(db.search(~ query.leader.exists()))
print(db.search((query.birthday.year == 2000) | query.hobbies.any(["movie"])))
print(db.search((query.birthday.year == 2000)))

documents = db.search(query.hobbies.any("walking"))
for document in documents:
    document["hobbies"].append("running")
db.write_back(documents)
print(db.search(query.hobbies.any("running")))