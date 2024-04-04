import asyncio
import logging
import os
import random
import time
import uuid

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient

CONN_STR = os.getenv("CONN_STR", None)
if CONN_STR is None:
    raise ValueError("CONN_STR env variable is required")

logging.basicConfig(level=logging.INFO)


class Timer:
    def __init__(self):
        self.key = None
        self.start_time = None
        self.durations = {}

    def __str__(self):
        return self.durations.to_json()

    def start(self, key):
        self.key = key
        logging.info(key)
        self.start_time = time.time()

    def end(self):
        if self.key is None:
            raise ValueError(f"Timer not started.")

        end_time = time.time()
        duration = end_time - self.start_time
        self.durations[self.key] = duration
        self.key = None


def clear(self):
    self.durations = pd.DataFrame(columns=["key", "duration"])


async def perform_database_operations() -> Timer:
    client = AsyncIOMotorClient(CONN_STR)
    timer = Timer()

    timer.start("0. Create a test database and collection")
    db_name = uuid.uuid4().hex[:8]
    collection_name = uuid.uuid4().hex[:8]
    db = client[db_name]
    collection = db[collection_name]
    timer.end()

    timer.start("1. Insert N items with random values")
    names = [uuid.uuid4().hex[:8] for _ in range(100)]
    items = []
    for _ in range(10000):
        item = {
            "id": str(uuid.uuid4()),
            "name": random.choice(names),
            "age": random.randint(18, 60),
        }
        items.append(item)
    await collection.insert_many(items)
    timer.end()

    timer.start("2. CreateIndexes")
    await collection.create_index("name")
    timer.end()

    timer.start("3. FindAndModify")
    for name in names:
        result = await collection.find_one_and_update(
            {"name": name}, {"$set": {"age": random.randint(18, 60)}}
        )
        logging.debug("Updated document:", result)
    timer.end()

    timer.start("4. Aggregate")
    pipeline = [{"$group": {"_id": None, "total_age": {"$sum": "$age"}}}]
    async for result in collection.aggregate(pipeline):
        logging.debug("Total age:", result["total_age"])
    timer.end()

    timer.start("5. Find")
    async for document in collection.find({"age": {"$gt": 30}}):
        logging.debug("Document:", document)
    timer.end()

    timer.start("6. Distinct")
    distinct_values = await collection.distinct("name")
    logging.debug("Distinct names:", distinct_values)
    timer.end()

    timer.start("7. Update")
    await collection.update_many({"age": {"$lt": 30}}, {"$set": {"status": "young"}})
    timer.end()

    timer.start("8. Delete")
    for name in names:
        await collection.delete_one({"name": name})
    timer.end()

    timer.start("9. DbStats")
    stats = await db.command("dbstats")
    logging.debug("Database stats:", stats)
    timer.end()

    # logging.debug("11. GetMore - Not applicable in MongoDB")

    timer.start("10. Delete collection and db")
    await collection.drop()
    await client.drop_database(db_name)
    timer.end()
    return timer


async def worker() -> [Timer]:
    timers = []
    for i in range(5):
        timer = await perform_database_operations()
        timers.append(timer)
    return timers


async def main():
    # There's limit of max 50 databases, so we'll stay under that
    tasks = [worker() for _ in range(30)]
    workers_timers: [[Timer]] = await asyncio.gather(*tasks)

    durations = [timer.durations for sublist in workers_timers for timer in sublist]
    df_durations = pd.DataFrame(durations)
    df_durations.to_json("output.json", orient="records", indent=4)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()

    print(f"Total execution time: {end_time - start_time} seconds")
