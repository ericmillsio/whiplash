# Performance Statistics

Stats are with default settings (6 hash keys, 384 dimensions). Keep in mind these stats are serially processing times, so they are not representative of the actual performance of the system. Parallel processing will depend on Lambda concurrency and DynamoDB read/write capacity.

## Direct Client (local, external to AWS)

Avg. Insert time: 0.3612s
Avg. Search time: 0.1324s

## Running API Client (local client, API running in AWS)

API Times:

- Avg. Insert time: 0.1299s
- Avg. Search time: 0.3460s

Client Times:

- Avg. Insert time: 0.1269s
- Avg. Search time: 0.5153s

### Rough Estimates

With 1000 concurrent requests and 1,000 WCUs per partition:

Write Throughput: 7.69 inserts/second/lambda \* 1000 concurrent requests = 7690 inserts/second
=> 130 seconds / 2.2 mins to insert 1 million items
This is comparable to Pinecone's indexing speed of 1.36 mins for 1 million items.

This is theoretical if you want to push concurrency to the max. In practice, you would want to limit concurrency on both Lambda and DynamoDB.

## ANN Benchmarks

TBD
