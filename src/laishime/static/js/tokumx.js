db.tweets.aggregate([
    { '$match': {'topics': {'$ne': []}} },
    { '$group': {'_id': '$topics', 'val': {'$sum': 1}} },
    { '$match': {'val': {'$gt': 20}} },
    { '$sort': {'val': -1} },
]);

db.tweets.find({'topics': {'$ne': []}}, {'topics': 1}).sort({'timestamp': -1})

