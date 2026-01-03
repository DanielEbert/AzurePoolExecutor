from KVBlobStore import KVBlobStore
from azure.storage.queue import QueueClient
from azure.data.tables import TableClient
import json
import cloudpickle
import os

conn_str = os.getenv('AZURE_BLOB_STORE_CONNECTION_STRING')

funcs_blob_store = KVBlobStore(conn_str, 'funcs')
args_blob_store = KVBlobStore(conn_str, 'args')
results_blob_store = KVBlobStore(conn_str, 'results')

table = TableClient.from_connection_string(conn_str, 'testtable')
queue = QueueClient.from_connection_string(conn_str, 'testqueue')

while True:
    message = queue.receive_message()
    if message:
        queue.delete_message(message)
        content = json.loads(message['content'])

        job_id = content['job_id']
        task_num = content['task_num']
        func_blob_key = content['func_blob_key']
        args_blob_key = content['args_blob_key']
        result_blob_key = content['result_blob_key']
        func = cloudpickle.loads(funcs_blob_store.download(func_blob_key))
        args = cloudpickle.loads(args_blob_store.download(args_blob_key))
        result = func(args)
        results_blob_store.upload(result_blob_key, cloudpickle.dumps(result))

        table.create_entity(entity={
            'PartitionKey': job_id,
            'RowKey': task_num,
            'result_blob_key': result_blob_key
        })
