# `unfolded.data-sdk`

Python package for interfacing with Unfolded's Data SDK.

## Installation

Install via pip:

```
pip install -U unfolded.data-sdk
```

## Authentication

Before using the Data SDK, you must authenticate. Authentication with a refresh
token only needs to be done once, and can be done either through the CLI or
Python module. First go to
[studio.unfolded.ai/tokens.html](https://studio.unfolded.ai/tokens.html) to sign
in. Then copy the **Refresh Token** for use in the next step.

### CLI

To authenticate via the CLI, use the `store-refresh-token` method:

```
> uf-data-sdk store-refresh-token
```

The CLI will then prompt for your refresh token, and print a message when it has
successfully stored it.

### Python module

To authenticate via the Python module, pass the refresh token to the `DataSDK`
class. **This only needs to happen once.** For future uses of the `DataSDK`
class, do not pass a `refresh_token` argument.

```py
from unfolded.data_sdk import DataSDK
DataSDK(refresh_token='v1.ABC...')
```

## Usage

### CLI

The CLI is available through `uf-data-sdk` on the command line. Running that
without any other arguments gives you a list of available commands:

```
> uf-data-sdk
Usage: uf-data-sdk [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  delete-dataset       Delete dataset from Unfolded Studio Warning: This...
  download-dataset     Download data for existing dataset to disk
  list-datasets        List datasets for a given user
  store-refresh-token  Store refresh token to enable seamless future...
  update-dataset       Update data for existing Unfolded Studio dataset
  upload-file          Upload new dataset to Unfolded Studio
```

Then to see how to use a command, pass `--help` to a subcommand:

```
> uf-data-sdk download-dataset --help

Usage: uf-data-sdk download-dataset [OPTIONS]

  Download data for existing dataset to disk

Options:
  --dataset-id TEXT       Dataset id.  [required]
  -o, --output-file PATH  Output file for dataset.  [required]
  --help                  Show this message and exit.
```

### Python Package

The Python package can be imported via `unfolded.data_sdk`:

```py
from unfolded.data_sdk import DataSDK, MediaType

data_sdk = DataSDK()
```

#### List Datasets

List datasets for given user

```py
datasets = data_sdk.list_datasets()
```

#### Get Dataset by ID

Get dataset given its id

```py
dataset = datasets[0]
data_sdk.get_dataset_by_id(dataset)
```

#### Download dataset data

Download data for dataset given its id

```py
dataset = datasets[0]
data_sdk.download_dataset(dataset, output_file='output.csv')
```

#### Upload new dataset

Upload new dataset to Unfolded Studio

```py
data_sdk.upload_file(
    file='new_file.csv',
    name='Dataset name',
    media_type=MediaType.CSV,
    description='Dataset description')
```

#### Update existing dataset

Update data for existing Unfolded Studio dataset

```py
dataset = datasets[0]
data_sdk.update_dataset(
    file='new_file.csv',
    dataset=dataset,
    media_type=MediaType.CSV)
```

#### Delete dataset

Delete dataset from Unfolded Studio

**Warning: This operation cannot be undone.** If you delete a dataset
currently used in one or more maps, the dataset will be removed from
those maps, possibly causing them to render incorrectly.

```py
dataset = datasets[0]
data_sdk.delete_dataset(dataset)
```

### DataFrame support

The Python package makes it simple to upload pandas `DataFrames` and geopandas
`GeoDataFrames` to Unfolded Studio. Pass either a `DataFrame` or a
`GeoDataFrame` to `upload_dataframe`:

```py
import pandas as pd

df = pd.DataFrame({'column1': [1, 2, 3, 4]})
data_sdk.upload_dataframe(df, 'Dataset Name')
```

```py
import geopandas as gpd

gdf = gpd.read_file('path/to/data.geojson')
data_sdk.upload_dataframe(gdf, 'Dataset Name')
```
