from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareAdjustmentFactorsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceAdapter, SourceRequest, fetch_source_result


class _FakeDataFrame:
    def __init__(self, records):
        self._records = list(records)

    def to_dict(self, orient="records"):
        if orient != "records":
            raise ValueError("Only orient='records' is supported in test fixture.")
        return list(self._records)


class AkshareAShareAdjustmentFactorsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareAShareAdjustmentFactorsAdapter(fetch_daily_factor=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_multi_symbol_batches(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2024, 7, 20, 9, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        rows_by_request = {
            ("sh600000", "qfq-factor"): [
                {"date": "2024-07-18", "qfq_factor": "1.0303254437870000"},
                {"date": "2024-07-18", "qfq_factor": "1.0303254437870000"},
                {"date": "1900-01-01", "qfq_factor": "16.6070491973801000"},
            ],
            ("sh600000", "hfq-factor"): [
                {"date": "2024-07-18", "hfq_factor": "16.1182559331356000"},
                {"date": "1900-01-01", "hfq_factor": "1.0000000000000000"},
            ],
            ("sz000001", "qfq-factor"): [
                {"date": date(2024, 6, 14), "qfq_factor": "1.0756444209161000"},
            ],
            ("sz000001", "hfq-factor"): [
                {"date": datetime(2024, 6, 14, 0, 0, 0), "hfq_factor": "138.6749600000000000"},
            ],
        }

        def fake_fetch_daily_factor(**kwargs):
            calls.append(kwargs)
            return _FakeDataFrame(rows_by_request[(kwargs["symbol"], kwargs["adjust"])])

        adapter = AkshareAShareAdjustmentFactorsAdapter(
            fetch_daily_factor=fake_fetch_daily_factor,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.ADJUSTMENT_FACTORS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH", "000001", "600000"),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "sh600000",
                    "start_date": "20240101",
                    "end_date": "20241231",
                    "adjust": "qfq-factor",
                },
                {
                    "symbol": "sh600000",
                    "start_date": "20240101",
                    "end_date": "20241231",
                    "adjust": "hfq-factor",
                },
                {
                    "symbol": "sz000001",
                    "start_date": "20240101",
                    "end_date": "20241231",
                    "adjust": "qfq-factor",
                },
                {
                    "symbol": "sz000001",
                    "start_date": "20240101",
                    "end_date": "20241231",
                    "adjust": "hfq-factor",
                },
            ],
        )
        self.assertEqual(result.record_count, 4)
        self.assertEqual(
            [
                (
                    record["symbol"],
                    record["factor_date"],
                    record["adjustment_basis"],
                )
                for record in result.normalized_records
            ],
            [
                ("000001.SZ", "2024-06-14", "hfq"),
                ("000001.SZ", "2024-06-14", "qfq"),
                ("600000.SH", "2024-07-18", "hfq"),
                ("600000.SH", "2024-07-18", "qfq"),
            ],
        )

        first_record = result.normalized_records[0]
        self.assertEqual(first_record["market"], "CN")
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["schema_version"], "v1")
        self.assertEqual(first_record["ingested_at"], now.isoformat())
        self.assertTrue(
            str(result.normalized_records[-1]["raw_payload_ref"]).startswith(
                "AKAF|600000.SH|qfq|2024-07-18|"
            )
        )
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.ADJUSTMENT_FACTORS, record),
                (),
            )

    def test_adapter_requires_bounded_dates_and_symbols(self) -> None:
        adapter = AkshareAShareAdjustmentFactorsAdapter(fetch_daily_factor=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.ADJUSTMENT_FACTORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "requires at least one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.ADJUSTMENT_FACTORS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31),
                ),
            )
        with self.assertRaisesRegex(ValueError, "Invalid SourceRequest date range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.ADJUSTMENT_FACTORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 12, 31),
                    end_date=date(2024, 1, 1),
                ),
            )

    def test_adapter_rejects_invalid_hk_etf_and_index_like_symbols(self) -> None:
        adapter = AkshareAShareAdjustmentFactorsAdapter(fetch_daily_factor=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Invalid symbol filter market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.ADJUSTMENT_FACTORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.HK",),
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31),
                ),
            )

        with self.assertRaisesRegex(ValueError, "code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.ADJUSTMENT_FACTORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.ADJUSTMENT_FACTORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.ADJUSTMENT_FACTORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SZ",),
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31),
                ),
            )

    def test_raw_payload_ref_is_deterministic_for_equivalent_rows(self) -> None:
        row = {"date": "2024-07-18", "qfq_factor": "1.0303254437870000"}
        adapter = AkshareAShareAdjustmentFactorsAdapter(
            fetch_daily_factor=lambda **kwargs: [dict(row)],
            adjustment_bases=("qfq",),
        )

        result_a = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.ADJUSTMENT_FACTORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
            ),
        )
        result_b = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.ADJUSTMENT_FACTORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
            ),
        )

        self.assertEqual(
            result_a.normalized_records[0]["raw_payload_ref"],
            result_b.normalized_records[0]["raw_payload_ref"],
        )


if __name__ == "__main__":
    unittest.main()
