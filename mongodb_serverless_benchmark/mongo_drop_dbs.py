import asyncio

import motor.motor_asyncio

CONN_STR = os.getenv("CONN_STR", None)
if CONN_STR is None:
    raise ValueError("CONN_STR env variable is required")


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(CONN_STR)

    database_names = await client.list_database_names()
    for db_name in database_names:
        if len(db_name) == 8:
            # await client.drop_database(db_name)  # UNCOMMENT WHEN ACTUALLY PERFORMING!
            print(f"Dropped database: {db_name}")

    database_names = await client.list_database_names()
    for db_name in database_names:
        print(f"Remaining database: {db_name}")


asyncio.run(main())
