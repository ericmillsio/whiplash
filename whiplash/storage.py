# -*- coding: utf-8 -*-

from typing import Optional

import boto3

from whiplash.dynamo_util import clean_item


class DynamoStorage:
    def __init__(self, region_name=None):
        self.region_name = region_name
        if self.region_name:
            self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
        else:
            self.dynamodb = boto3.resource("dynamodb")

    def get_table(self, table_name):
        """
        Get a DynamoTable instance for the specified table name.
        :param table_name: Name of the DynamoDB table to create the DynamoTable for.
        :return: A DynamoTable instance for the specified table.
        """
        return DynamoTable(table_name, self.dynamodb)


class DynamoTable:
    def __init__(self, table_name, dynamodb):
        self.table_name = table_name
        self.table = dynamodb.Table(self.table_name)
        self.dynamodb = dynamodb
        self.pk = "id"

    def exists(self):
        """
        Check if the DynamoDB table exists.
        :return: True if the table exists, False otherwise.
        """
        try:
            self.dynamodb.meta.client.describe_table(TableName=self.table_name)
            return True
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            return False

    def create_table(self):
        """
        Create the DynamoDB table.
        """
        self.table = self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[{"AttributeName": self.pk, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": self.pk, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

    def describe_table(self):
        """
        Describe the DynamoDB table.
        :return: Dictionary containing the table description.
        """
        return self.dynamodb.meta.client.describe_table(TableName=self.table_name)

    def put(self, item):
        """
        Store an item in the DynamoDB table.
        :param item: Dictionary representing the item to be stored.
        """
        self.table.put_item(Item=item)

    def update_column(self, item_id, column_name, new_val):
        """
        Update a column of an item in the DynamoDB table.
        :param item_id: The unique ID of the item to update.
        :param column_name: The name of the column to update.
        :param new_val: The new value to set for the column.
        """
        try:
            self.table.update_item(
                Key={self.pk: item_id},
                UpdateExpression=f"ADD {column_name} :val",
                ExpressionAttributeValues={":val": set([new_val])},
                ConditionExpression=f"attribute_exists({self.pk})",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            # If the item does not exist, create it
            self.put({self.pk: item_id, column_name: set([new_val])})

    def upsert_items_set_bulk(self, item_ids, column_name, new_val):
        with self.table.batch_writer() as batch:
            # Update the item or create a new item with the primary key and set the new IDs
            for item_id in item_ids:
                batch.put_item(
                    Item={self.pk: item_id, column_name: set([new_val])},
                    ConditionExpression=f"attribute_exists({self.pk})",
                    UpdateExpression=f"ADD {column_name} :id",
                    ExpressionAttributeValues={":id": set([new_val])},
                )

    def get(self, item_id) -> Optional[dict]:
        """
        Retrieve an item from the DynamoDB table by its ID.
        :param item_id: The unique ID of the item to retrieve.
        :return: Dictionary representing the retrieved item, or None if not found.
        """
        response = self.table.get_item(Key={"id": item_id})
        if "Item" not in response or not response["Item"]:
            return None
        return clean_item(response.get("Item"))

    def get_batch(self, item_ids: list[str]) -> list[dict]:
        """
        Retrieve multiple items from the DynamoDB table by their IDs.
        :param item_ids: A list of unique IDs of the items to retrieve.
        :return: A list of dictionaries representing the retrieved items.
        """
        response = self.dynamodb.batch_get_item(
            RequestItems={
                self.table_name: {
                    "Keys": [{"id": item_id} for item_id in set(item_ids)],
                }
            }
        )
        items = response.get("Responses", {}).get(self.table_name, [])
        return [clean_item(item) for item in items]

    def get_bulk(self, item_ids: list[str]) -> list[dict]:
        """
        Retrieve multiple items from the DynamoDB table by their IDs.
        Chunk the item IDs into batches of 100 to avoid exceeding the 100-item limit.
        :param item_ids: A list of unique IDs of the items to retrieve.
        :return: A list of dictionaries representing the retrieved items.
        """
        results = []
        for i in range(0, len(item_ids), 100):
            batch = item_ids[i : i + 100]
            results.extend(self.get_batch(batch))
        return [clean_item(item) for item in results]

    def delete(self, item_id):
        """
        Delete an item from the DynamoDB table by its ID.
        :param item_id: The unique ID of the item to delete.
        """
        self.table.delete_item(Key={"id": item_id})

    def update(self, item_id, update_expression, expression_attribute_values):
        """
        Update an existing item in the DynamoDB table.
        :param item_id: The unique ID of the item to update.
        :param update_expression: The update expression for the update operation.
        :param expression_attribute_values: A dictionary of attribute values used in the update expression.
        """
        self.table.update_item(
            Key={"id": item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )

    def query(self, key_condition_expression, expression_attribute_values=None):
        """
        Perform a query on the DynamoDB table.
        :param key_condition_expression: The key condition expression for the query.
        :param expression_attribute_values: A dictionary of attribute values used in the query.
        :return: A list of items matching the query condition.
        """
        if not expression_attribute_values:
            expression_attribute_values = {}

        response = self.table.query(
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )

        items = response.get("Items", [])

        return [clean_item(item) for item in items]

    def dump(self):
        """
        Perform a scan on the DynamoDB table.
        :return: A list of all items in the table.
        """

        response = self.table.scan()

        items = response.get("Items", [])

        return [clean_item(item) for item in items]
