# Whiplash

Serverless, lightweight, and fast vector store on top of DynamoDB

## Description

Whiplash is a lightweight vector store built on top of [AWS DynamoDB](https://aws.amazon.com/dynamodb/). It uses a variant of [locality-sensitive hashing (LSH)](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) to index vectors in a DynamoDB table. This is intended to be a mimimalist, scalable, and fast vector store and is intended to be extremely easy to use, maintain, and self-host.

There are several main components to Whiplash:

- **Whiplash Serverless API** - A fully functional API that can be deployed to AWS with a few commands.
- **Whiplash Client / SDK** - A Python library that can be used to interact directly with Whiplash internals (talks directly to DynamoDB) or via the API.
- **Whiplash CLI** - A CLI that can be used to interact with the Whiplash Serverless API. (TODO)

## Installation

### Library

```bash
pip install whiplash-client

# OR

poetry add whiplash-client
```

### Serverless API (AWS)

```bash
npm install -g serverless
# Go to project directory
npm install
```

Prepare for deployment:

1. Setup env

```bash
cp .env.example .env
# Change AWS_PROFILE within .env to your AWS profile
# Adjust other values if you want
```

2. Ensure you have Docker/Colima installed and running for building

Deploy to AWS:

```bash
serverless deploy --stage dev --region us-east-2
```

Expected output is below. Note the API key for access and endpoints to use.

```bash
Running "serverless" from node_modules

Deploying whiplash to stage dev (us-east-2)

✔ Service deployed to stack whiplash-dev (64s)

api keys:
  dev-api-key: <YOUR API KEY WILL BE HERE>
endpoints:
  GET - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}
  POST - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects
  GET - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects
  POST - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}/collections
  GET - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}/collections
  GET - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}/collections/{collectionId}
  POST - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}/collections/{collectionId}/items
  POST - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}/collections/{collectionId}/items/batch
  GET - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}/collections/{collectionId}/items/{itemId}
  GET - https://API_ID.execute-api.us-east-2.amazonaws.com/dev/projects/{projectId}/collections/{collectionId}/search
functions:
  getProject: whiplash-dev-getProject (12 kB)
  createProject: whiplash-dev-createProject (12 kB)
  listProjects: whiplash-dev-listProjects (12 kB)
  createCollection: whiplash-dev-createCollection (12 kB)
  listCollections: whiplash-dev-listCollections (12 kB)
  getCollection: whiplash-dev-getCollection (12 kB)
  createItem: whiplash-dev-createItem (12 kB)
  createItems: whiplash-dev-createItems (12 kB)
  getItem: whiplash-dev-getItem (12 kB)
  searchItems: whiplash-dev-searchItems (12 kB)
```

## Usage

There are three ways to use Whiplash: as a direct client, as a serverless API, or as a library proxying through the API.

### Direct Client

The library is the most flexible way to use Whiplash. It can be used in any Python project and can be used to build custom applications on top of Whiplash without deploying the API. It will manage the tables directly. It's recommended to be used inside of AWS to avoid network latency, but can be used outside for testing/evaluation.

```python
import numpy as np

from whiplash import Vector, Whiplash

# AWS_PROFILE must be set in environment variables for boto3
whiplash = Whiplash("us-east-2", "dev")

# First time only setup
whiplash.setup()

collection = whiplash.create_collection("test_collection", n_features=3)

# Insert a vector
item = Vector("some_id", np.ndarray([1, 2, 3]))
collection.insert(item)

# Search for the inserted vector
result = collection.search(item.vector, limit=1)
```

### Serverless API

The serverless API is fully functional microservice and can be deployed to AWS with a few commands. The API is built using [Serverless](https://www.serverless.com/) and [AWS Lambda](https://aws.amazon.com/lambda/).

API Endpoints:

- `/projects`
- `/projects/{projectId}`
- `/projects/{projectId}/collections`
- `/projects/{projectId}/collections/{collectionId}`
- `/projects/{projectId}/collections/{collectionId}/items`
- `/projects/{projectId}/collections/{collectionId}/items/{itemId}`
- `/projects/{projectId}/collections/{collectionId}/search`

Required Headers:

- `x-api-key: API_KEY`
- `Content-Type: application/json`

You can choose to interact with the API directly or use the Whiplash Client Library. An api.yaml file is included in the project for use with [Postman](https://www.postman.com/) or [Insomnia](https://insomnia.rest/).

### Library Proxying Through API

The library can be used to proxy through the API. This is recommended if you want to use a library but don't want to manage the tables directly. This is more stable and likely faster than the direct client library for bulk insert operations, but slower for single insert operations (assuming you are calling from outside the AWS region).

This can only be used if the API is deployed. It also avoids the numpy dependency, but I haven't broken out the packages yet.

```python
import time

from whiplash.api.client import Whiplash

query = [0.5472,...]
whiplash = Whiplash(
    "https://API-ID.execute-api.us-east-2.amazonaws.com/STAGE",
    "API_KEY",
)

collection = whiplash.get_collection("example")

assert collection is not None

start = time.time()
results = collection.search(query)

print("Search took", time.time() - start, "seconds")
print("Results:", results)
```

## How it works

Whiplash uses [locality-sensitive hashing (LSH)](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) to index vectors in a [DynamoDB](https://aws.amazon.com/dynamodb/) table. This is intended to be a mimimalist, scalable, and fast vector store built on top of AWS production-grade infrastructure.

Whiplash varies from traditional LSH in that it uses differing number of bits for each hash key. This allows for dynamic and automatic tuning of the number of buckets, which gives flexiblity to scaling the index over time. When buckets on the smallest hash key are close to the maximum size of a DynamoDB item, a new layer of hash function/keys is added.

### Dynamo Tables

Whiplash uses several Dynamo tables to store the vectors and buckets:

- `PROJECT_STAGE_COLLECTION_vectors` - stores the `{ vector_id: binary(vector) }`
- `PROJECT_STAGE_COLLECTION_buckets` - stores the `{ hash: set of vector_ids }`
- `whiplash_metadata` - stores metadata about each collection `{ collection_id: { n_features: 256, uniform_planes: {0: [binary]} ...} }`

### Hashing

Whiplash uses [random projection](https://en.wikipedia.org/wiki/Random_projection) to hash vectors into buckets. The vectors are projected onto a set of random planes, and the sign of the projection determines which side of the plane the vector is on. The planes are generated using the [Gaussian distribution](https://en.wikipedia.org/wiki/Normal_distribution) to ensure that the vectors are evenly distributed.

Hash keys are generated by converting the array of boolean results of random projection to a binary string, and then converted to base 36.

## Development

```bash
poetry install
poetry run pytest
```

## Pros and Cons

Whiplash (and LSH in general) for the purpose of approximate nearest neighbor (ANN) algorithmic search has tradeoffs compared to current vector stores:

Pros:

- Fast even for very large datasets
- Extremely simple infrastructure
- Serverless and scalable (built on top of DynamoDB and mostly KV lookups)
- Low cost (25GB of free storage free, ~200M requests per month)
- Self hosted and in control of your data, no vendor lock-in

Cons:

- Lower recall (less accurate) than other vector stores / algorithms (You can trade off recall for speed by increasing the number of hash keys / DEFAULT_N_PLANES)
- Less desirable for high-dimensional vectors (BUT I have found it works fine < 500 dimensions)
- Since we are using Lambda, there are cold starts, weaker compute, and limited memory. But this is a tradeoff for the cost and scalability.

I wanted to build this because I was frustrated with the high cost of managed vector stores, and the complexity of self-hosting other open-source vector stores. There is also no good serverless solution (even if AWS pushes "Serverless" ElasticSearch, ugh). Whiplash is so simple and built on production-ready infrastructure that will have very little maintenance.

Comparing storage cost alone to Pinecone:

- Pinecone:

  - 20 million vectors x 768 dimensions
  - 4xs1 pod = $0.3840/hour = $276.48/month

- Whiplash:
  - (Assume UUIDs for vector IDs, 6 hash keys per vector)
  - Vector Index: 20 million vectors x 768 dimensions x 4 bytes per float = 60GB
  - Bucket Index (assume UUIDs): 20 million vectors x 16 bytes x 6 hash keys = 1.92GB
  - 25GB free, 37GB = $0.25/GB-month = $9.25/month

## Roadmap

In no particular order:

- [x] Add serverless lambda microservice API with one-click deployment
- [x] Add SDK for API
- [ ] Add dynamic scaling of uniform planes
  - [ ] Handle DynamoDB item size limits (400KB)
- [ ] Add CLI tool with API
- [ ] Add support for attribute filtering
- [ ] Performance benchmarking
- [ ] Additional testing

## License

If you are Amazon and want to use this, please contact me and pay me a bunch of money beforehand. Otherwise, this is licensed under [Apache 2.0](https://choosealicense.com/licenses/apache-2.0/).
