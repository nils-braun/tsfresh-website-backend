from io import StringIO
from typing import Optional

from fastapi import UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import tsfresh
from tsfresh.feature_extraction import settings as tsfresh_settings

import pandas as pd


def read_in_data(
    input_format: Optional[str] = "csv", data_file: UploadFile = File(default=None)
) -> pd.DataFrame:
    if not data_file or not data_file.filename:
        raise HTTPException(400, "Need to supply a valid data file.")

    try:
        if input_format == "csv":
            df = pd.read_csv(data_file.file)
        elif input_format == "json":
            df = pd.read_json(data_file.file, orient="records")
        elif input_format == "parquet":
            df = pd.read_parquet(data_file.file)
        else:
            raise HTTPException(400, f"Do not understand input format: {input_format}")
    except Exception as e:
        raise HTTPException(400, f"Can not read input file: {e}")

    if len(df) >= 100 or len(df.columns) > 6:
        raise HTTPException(400, "Only files with less than 100 data points and less than 7 columns are allowed.")

    return df


def extract_features(
    df: pd.DataFrame,
    column_id: Optional[str] = None,
    column_kind: Optional[str] = None,
    column_sort: Optional[str] = None,
    column_value: Optional[str] = None,
    settings: Optional[str] = "comprehensive",
) -> pd.DataFrame:

    if settings == "comprehensive":
        default_fc_parameters = tsfresh_settings.ComprehensiveFCParameters()
    elif settings == "minimal":
        default_fc_parameters = tsfresh_settings.MinimalFCParameters()
    elif settings == "efficient":
        default_fc_parameters = tsfresh_settings.EfficientFCParameters()
    else:
        raise HTTPException(400, f"Do not understand extraction setting: {setting}")

    kwargs = dict(
        column_id=column_id,
        column_kind=column_kind,
        column_sort=column_sort,
        column_value=column_value,
        default_fc_parameters=default_fc_parameters,
        disable_progressbar=True,
        n_jobs=0,
    )

    try:
        extracted_features = tsfresh.extract_features(df, **kwargs)
    except Exception as e:
        raise HTTPException(400, f"Could not extract features: {e}")

    return extracted_features


def output_data(
    df: pd.DataFrame,
    output_format: Optional[str] = "csv",
    output_delimiter: Optional[str] = ",",
) -> StreamingResponse:
    sio = StringIO()

    if output_format == "csv":
        df.to_csv(sio, sep=output_delimiter)
    elif output_format == "json":
        # Make sure that the index (= ids) is included
        df = df.reset_index()
        df.to_json(sio, orient="records")
    elif output_format == "parquet":
        df.to_parquet(sio)
    else:
        raise HTTPException(400, f"Do not understand output format {output_format}")

    sio.seek(0)

    return StreamingResponse(
        sio,
        headers={
            "Content-Disposition": f"attachment;filename=features.{output_format}"
        },
    )
