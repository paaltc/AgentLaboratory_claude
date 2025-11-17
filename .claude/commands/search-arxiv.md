# Search ArXiv

Search arXiv for research papers matching a query.

## Syntax
```bash
/search-arxiv <query> [--count=N]
```

## Arguments
- `query`: Search query (required)
- `--count`: Number of results (default: 20)

## Example
```bash
/search-arxiv "transformer attention mechanisms" --count=30
```

## Returns
- Paper titles
- Abstracts
- Publication dates
- arXiv IDs
- PDF URLs

## Advanced Usage
Retrieve full paper text:
```bash
/search-arxiv <arxiv-id> --full-text
```

## Python API
```python
from tools import ArxivSearch

search = ArxivSearch()
results = search.find_papers_by_str("attention mechanisms", N=20)
print(results)

# Get full paper text
full_text = search.retrieve_full_paper_text("2304.12234")
print(full_text)
```
