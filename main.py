from AzurePoolExecutor import AzurePoolExecutor
import os

conn_str = os.getenv('AZURE_BLOB_STORE_CONNECTION_STRING')


def square(x):
    print(f'square {x}')
    return x*x


with AzurePoolExecutor(4, conn_str, 'testqueue', 'testtable') as executor:
    results = executor.map(square, [1, 2, 3, 4, 5])
    print(results)
