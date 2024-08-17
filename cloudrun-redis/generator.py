import random
import string
import json
import redis
import os
import pandas as pd


def load_data(conn):
    data = pd.read_csv("data.csv")
    pipeline = conn.pipeline()
    for i, row in data.iterrows():
        pid = f"ID{i + 1:04d}"
        product = {
            "pid": pid,
            "sku": ''.join(random.choices(string.ascii_uppercase + string.digits, k=7)),
            "name": row['name'],
            "category": row['category'],
            "brand": row['brand'],
            "price": row['price'],
            "image": row['image'],
            "description": row['description']
        }
        pipeline.json().set(f"product:{pid}", "$", product)

    pipeline.execute()
    pipeline.close()
    conn.close()

