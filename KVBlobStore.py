from azure.storage.blob import BlobServiceClient


class KVBlobStore:
    def __init__(self, conn_str, container_name):
        self.container_name = container_name
        self.client = BlobServiceClient.from_connection_string(
            conn_str,
            max_block_size=1024*1024*8,      # 8 MiB per chunk
            max_single_put_size=1024*1024*64,  # Single upload if < 64 MiB
            max_concurrency=4                # Number of parallel workers
        )

        container_client = self.client.get_container_client(
            self.container_name)
        if not container_client.exists():
            container_client.create_container()

    def upload(self, key, data):
        container_client = self.client.get_container_client(
            self.container_name)
        container_client.upload_blob(key, data)

    def download(self, key):
        container_client = self.client.get_container_client(
            self.container_name)
        return container_client.download_blob(key).readall()

    def delete(self, key):
        container_client = self.client.get_container_client(
            self.container_name)
        container_client.delete_blob(key)
