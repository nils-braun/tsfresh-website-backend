from unittest import TestCase
from io import BytesIO

import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app


class FeatureExtractionTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @staticmethod
    def _to_file(response):
        bio = BytesIO()
        bio.write(response.content)
        bio.seek(0)

        return bio

    def _check_features(self, df):
        self.assertIn("id", df.columns)
        self.assertEqual(len(df), 1)
        self.assertEqual(df["id"].iloc[0], 1)
        self.assertGreater(len(df.columns), 100)

    def test_wrong_input(self):
        # input file missing
        r = self.client.post("/extraction")
        self.assertEqual(r.status_code, 400)

        # input file missing
        r = self.client.post("/extraction?input_format=csv")
        self.assertEqual(r.status_code, 400)

        # input file invalid
        r = self.client.post("/extraction",  files={
            'data_file': BytesIO(b'1\n1,1'),
        })
        self.assertEqual(r.status_code, 400)

        # missing columns
        r = self.client.post("/extraction?column_id=id&column_sort=time",  files={
            'data_file': BytesIO(b'id,not_time\n1,1'),
        })
        self.assertEqual(r.status_code, 400)

    def test_extraction(self):
        # Send csv data and retrieve CSV data
        r = self.client.post("/extraction?column_id=id&column_value=value",  files={
            'data_file': BytesIO(b'id,value\n1,1'),
        })
        self.assertEqual(r.status_code, 200)

        # Check if result look reasonable
        bio = self._to_file(r)
        df = pd.read_csv(bio)
        self._check_features(df)


    def test_different_formats(self):
        # Input JSON
        r = self.client.post("/extraction?column_id=id&column_value=value&input_format=json", files={
            'data_file': BytesIO(b'[{"id": 1, "value": 2}]'),
        })
        self.assertEqual(r.status_code, 200)

        bio = self._to_file(r)
        df = pd.read_csv(bio)
        self._check_features(df)

        # Should not work with wrong format
        r = self.client.post("/extraction?column_id=id&column_value=value&input_format=csv",  files={
            'data_file': BytesIO(b'[{"id": 1, "value": 2}]'),
        })
        self.assertEqual(r.status_code, 400)

        # Output format json
        r = self.client.post("/extraction?column_id=id&column_value=value&output_format=json",  files={
            'data_file': BytesIO(b'id,value\n1,1'),
        })
        self.assertEqual(r.status_code, 200)

        bio = self._to_file(r)
        df = pd.read_json(bio, orient="records")
        self._check_features(df)

        # Output format csv, different delimiter
        r = self.client.post("/extraction?column_id=id&column_value=value&output_delimiter=|",  files={
            'data_file': BytesIO(b'id,value\n1,1'),
        })
        self.assertEqual(r.status_code, 200)

        bio = self._to_file(r)
        df = pd.read_csv(bio, sep="|")
        self._check_features(df)