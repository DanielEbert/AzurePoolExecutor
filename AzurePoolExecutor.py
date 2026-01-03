from azure.storage.queue import QueueClient
from azure.data.tables import TableClient
from typing import Callable, Iterable
import uuid
import cloudpickle
import time

from KVBlobStore import KVBlobStore


class AzurePoolExecutor:
    def __init__(self, max_workers: int, conn_str: str, queue_name: str, table_name: str):
        self.max_workers = max_workers
        self.queue = QueueClient.from_connection_string(conn_str, queue_name)
        self.table = TableClient.from_connection_string(conn_str, table_name)

        self.funcs_blob_store = KVBlobStore(conn_str, 'funcs')
        self.args_blob_store = KVBlobStore(conn_str, 'args')
        self.results_blob_store = KVBlobStore(conn_str, 'results')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # TODO: cleanup on return
    def map(self, func: Callable, iterable):
        job_id = str(uuid.uuid4())
        func_blob_key = f'func_{job_id}'
        self.funcs_blob_store.upload(func_blob_key, cloudpickle.dumps(func))

        for task_num, item in enumerate(iterable):
            args_blob_key = f'args_{job_id}_{task_num}'
            self.args_blob_store.upload(args_blob_key, cloudpickle.dumps(item))
            result_blob_key = f'result_{job_id}_{task_num}'
            self.queue.send_message(
                f'{{"job_id": "{job_id}", "task_num": "{task_num}", "func_blob_key": "{func_blob_key}", "args_blob_key": "{args_blob_key}", "result_blob_key": "{result_blob_key}"}}')

        # Loop until all table entries are created and get result_blob_key for each task
        result_blob_keys = []
        num_tasks = len(iterable)

        while len(result_blob_keys) < num_tasks or any(key is None for key in result_blob_keys):
            result_blob_keys = []
            for task_num in range(num_tasks):
                try:
                    entity = self.table.get_entity(
                        partition_key=job_id, row_key=str(task_num))
                    if entity and 'result_blob_key' in entity:
                        result_blob_keys.append(entity['result_blob_key'])
                    else:
                        result_blob_keys.append(None)
                except Exception:
                    # Entity doesn't exist yet
                    result_blob_keys.append(None)

            # If all results exist, break out of the loop
            if all(key is not None for key in result_blob_keys):
                break

            # Wait a bit before checking again
            time.sleep(0.1)

        # TODO: optionally just return link to result. the data might be too large to fit in memory
        return [cloudpickle.loads(self.results_blob_store.download(key)) for key in result_blob_keys]
