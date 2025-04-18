# fed-court-decisions-db

[![PyPI - Version](https://img.shields.io/pypi/v/fed-court-decisions-db.svg)](https://pypi.org/project/fed-court-decisions-db)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fed-court-decisions-db.svg)](https://pypi.org/project/fed-court-decisions-db)

-----

## Table of Contents

- [Process](#process)
- [License](#license)

## Process

1. Getting Fed Court decisions from https://zenodo.org/records/14867950
Those documents are at the core of the system and form the knowledge base used to answer to user's questions. They are provided as a single _.parquet_ file (several GB).

2. Embedding the decisions Parquet file locally
Using the _"embed-decisions"_ notebook, the decision texts are extracted from the _zenodo_ parquet file. Chunks are created so as to be able to embed larger decisions and are all gathered in a _.jsonl_ file along with the generated vector and certain other properties, such as chunk number, language, date ...

3. Splitting the _.jsonl_ file locally
The _.jsonl_ file from previous step is then split locally and each part is uploaded to a dedicated bucket on S3.

4. Feeding the OpenSearch Serverless vector db
Each part of the original _.jsonl_ file is itself a _.jsonl_ file and is processed by calling a lambda with the corresponding S3 reference as input. The vector is extracted from each item of the _.jsonl_ part and inserted into the OpenSearch Serverless DB. A unicity check is performed using the doc id and chunk number.

## License

`fed-court-decisions-db` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
