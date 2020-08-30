from typing import Optional

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from .utils import read_in_data, extract_features, output_data

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.post("/extraction")
def extraction(
    input_format: Optional[str] = "csv",
    data_file: UploadFile = File(default=None),
    column_id: Optional[str] = None,
    column_kind: Optional[str] = None,
    column_sort: Optional[str] = None,
    column_value: Optional[str] = None,
    settings: Optional[str] = "comprehensive",
    output_format: Optional[str] = "csv",
    output_delimiter: Optional[str] = ",",
) -> StreamingResponse:
    df = read_in_data(input_format, data_file)
    features = extract_features(
        df,
        column_id=column_id,
        column_kind=column_kind,
        column_sort=column_sort,
        column_value=column_value,
        settings=settings,
    )

    return output_data(
        features, output_format=output_format, output_delimiter=output_delimiter
    )
