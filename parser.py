from typing import Iterator
from langchain.document_loaders.base import BaseBlobParser
from langchain.document_loaders.blob_loaders import Blob
from langchain.schema import Document
import pandas as pd
import json

class DataSetParser(BaseBlobParser):
    """Parser for dataset blobs."""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Lazily parse the blob."""

        content = ""

        with blob.as_bytes_io() as file:
            if blob.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                content = pd.read_excel(file, index_col=0)
            elif blob.mimetype == "text/csv":
                content = pd.read_csv(file)
        
        content = content.to_dict()

        yield Document(page_content=json.dumps(content), metadata={"source": "analytibot", "name": blob.path.rsplit('.', 1)[0]})