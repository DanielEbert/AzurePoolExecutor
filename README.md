# Azure Blob Store Distributed Task Executor

A distributed task execution system built on Azure Blob Storage, Queue, and Table services. This system allows you to distribute Python function execution across multiple worker nodes.

## Overview

This project implements a distributed executor pattern where:
- **Host/Client** (`main.py`): Submits tasks to be executed
- **Worker Nodes** (`worker.py`): Process tasks from the queue and return results

Tasks are serialized using `cloudpickle` and stored in Azure Blob Storage, while task coordination happens through Azure Queue and Table services.

## Prerequisites

- Python 3.10 or higher
- Azure Storage Account with:
  - Blob Storage
  - Queue Storage
  - Table Storage
- Azure Storage connection string

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd azure_blob_store_test
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variable:**
   ```bash
   export AZURE_BLOB_STORE_CONNECTION_STRING="your_azure_connection_string_here"
   ```

   To make this persistent, add it to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   echo 'export AZURE_BLOB_STORE_CONNECTION_STRING="your_azure_connection_string_here"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

### Step 1: Start Worker Nodes

On **each worker node**, run the worker script:

```bash
python worker.py
```

The worker will continuously poll the Azure Queue for tasks and execute them. You can run multiple workers on different machines or multiple instances on the same machine for parallel processing.

**Note:** Each worker node must have:
- The same Python environment with dependencies installed
- The `AZURE_BLOB_STORE_CONNECTION_STRING` environment variable set
- Access to all project files (`worker.py`, `KVBlobStore.py`)

### Step 2: Run the Main Script

On the **host/client machine**, run the main script to submit tasks:

```bash
python main.py
```

The main script will:
1. Create tasks and upload them to Azure Blob Storage
2. Send task messages to the Azure Queue
3. Wait for workers to process the tasks
4. Retrieve and return the results

## Project Structure

- `main.py` - Host/client script that submits tasks using `AzurePoolExecutor`
- `worker.py` - Worker script that processes tasks from the queue
- `AzurePoolExecutor.py` - Executor class that manages task distribution
- `KVBlobStore.py` - Key-value store wrapper around Azure Blob Storage

## Example

The included `main.py` demonstrates a simple example:

```python
def square(x):
    print(f'square {x}')
    return x*x

with AzurePoolExecutor(4, conn_str, 'testqueue', 'testtable') as executor:
    results = executor.map(square, [1, 2, 3, 4, 5])
    print(results)
```

This will distribute the `square` function across worker nodes with the arguments `[1, 2, 3, 4, 5]`.

## Configuration

The system uses the following Azure resources:
- **Blob Containers**: `funcs`, `args`, `results` (created automatically)
- **Queue**: `testqueue` (must exist or be created)
- **Table**: `testtable` (must exist or be created)

Make sure these resources exist in your Azure Storage Account or modify the names in the code to match your setup.

## Troubleshooting

- **Connection errors**: Verify your `AZURE_BLOB_STORE_CONNECTION_STRING` is correct and has proper permissions
- **Queue/Table not found**: Ensure the queue and table names exist in your Azure Storage Account
- **Workers not processing**: Check that workers are running and can access the Azure services
- **Import errors**: Ensure all dependencies are installed in the Python environment
