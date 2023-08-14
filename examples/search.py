import time

import numpy as np

from whiplash import Whiplash

whiplash = Whiplash("us-east-2", "dev")
collection = whiplash.get_collection("example")

assert collection is not None

# Search for the inserted vector
vectors = [np.random.rand(256).astype(np.float32) for i in range(100)]
start = time.time()
for vector in vectors:
    result = collection.search(vector, k=5)
    print("Search results:", result)

search_time = (time.time() - start) / 100
print(f"Average Search time: {search_time}")

# Search results: [id_39: 0.8007, id_3: 0.7801, id_19: 0.772, id_86: 0.7669, id_35: 0.7611]
# Search results: [id_90: 0.7845, id_54: 0.7762, id_16: 0.768, id_34: 0.7662, id_52: 0.7661]
# Search results: [id_9: 0.7722, id_67: 0.7718, id_29: 0.7664, id_99: 0.7658, id_20: 0.7546]
# Search results: [id_56: 0.791, id_17: 0.7791, id_88: 0.7737, id_72: 0.7707, id_95: 0.7657]
# ...
# Average Search time: 0.0792296814918518
