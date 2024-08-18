import random
import string
import pandas as pd
from connection import RedisConnection


def load_data():
    conn = RedisConnection().get_connection()
    data = pd.read_csv("data.csv")
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
        conn.json().set(f"product:{pid}", "$", product)

    conn.close()

