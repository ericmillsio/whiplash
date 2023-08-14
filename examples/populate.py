import time

import numpy as np

from whiplash import Vector, Whiplash

whiplash = Whiplash("us-east-2", "dev")

collection = whiplash.get_collection("example")

assert collection is not None

# Insert a vector
start = time.time()
vectors = []
for i in range(100):
    vector = Vector(f"id_{i}", np.random.rand(256).astype(np.float32))
    vectors.append(vector)
    collection.insert(vector)
insert_time = (time.time() - start) / 100

print(f"Inserted {len(vectors)} vectors")
print(f"Average Insert time: {insert_time}")

# Inserted 100 vectors
# Average Insert time: 0.40521308183670046
