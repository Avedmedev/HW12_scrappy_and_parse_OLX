import logging

from bson import ObjectId


async def insert_data(collection, data_list):
    flats = []

    for data in data_list:
        flats.append({
            '_id': ObjectId(),
            'title': data[0].text,
            'price': data[1].text,
            'location': data[2].text,
            'square': data[3].text[len(data[2].text):]
        })

    values = await collection.insert_many(flats)
    return values


async def get_all_flats(mongo):
    cursor = mongo.flats.find({})
    flats = [flat for flat in await cursor.to_list(length=100)]

    return flats


