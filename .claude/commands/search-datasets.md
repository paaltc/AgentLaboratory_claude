# Search Datasets

Search HuggingFace Hub for relevant datasets.

## Syntax
```bash
/search-datasets <query> [--count=N]
```

## Arguments
- `query`: Dataset search query (required)
- `--count`: Number of results (default: 10)

## Example
```bash
/search-datasets "sentiment analysis" --count=15
```

## Returns
- Dataset names
- Descriptions
- Repository links
- Number of downloads
- Tags and features

## Python API
```python
from tools import HFDataSearch

search = HFDataSearch()
results = search.retrieve_ds("sentiment analysis", N=10)
print(results)
```
