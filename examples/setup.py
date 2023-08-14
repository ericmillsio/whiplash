from whiplash import Whiplash

whiplash = Whiplash("us-east-2", "dev")

# First time setup
whiplash.setup()

collection = whiplash.create_collection("example", n_features=256)

print("Project Info:", whiplash)
print("Collection Info:", collection)
print(
    "Tables in DynamoDB:",
    [
        "whiplash_metadata",
        collection.collection_id + "_vectors",
        collection.collection_id + "_buckets",
    ],
)

# Project Info: Whiplash(region=us-east-2, stage=dev, project_name=whiplash)
# Collection Info: Collection(collection_id=whiplash_dev_example, config=CollectionConfig(n_features=384, n_planes=6, bit_start=8, bit_scale_factor=2))
# Tables in DynamoDB: ['whiplash_metadata', 'whiplash_dev_example_vectors', 'whiplash_dev_example_buckets']
