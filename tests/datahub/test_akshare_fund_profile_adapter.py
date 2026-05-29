from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareFundProfileAdapter,
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


def _vertical_profile_rows(**overrides):
    values = {
        "基金代码": "000001",
        "基金名称": "华夏成长混合",
        "基金全称": "华夏成长证券投资基金",
        "成立时间": "2001-12-18",
        "基金公司": "华夏基金管理有限公司",
        "基金经理": "刘睿聪 郑晓辉",
        "托管银行": "中国建设银行股份有限公司",
        "基金类型": "混合型-偏股",
        "业绩比较基准": "本基金暂不设业绩比较基准",
    }
    values.update(overrides)
    return [{"item": key, "value": value} for key, value in values.items()]


class AkshareFundProfileAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_vertical_profile(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 10, 9, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_fund_profile(**kwargs):
            calls.append(kwargs)
            return _vertical_profile_rows(source_ts="2024-01-09T18:00:00")

        adapter = AkshareFundProfileAdapter(
            fetch_fund_profile=fake_fetch_fund_profile,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.FUND_PROFILE,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("000001.FUND_CN",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 10, 9, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(calls, [{"symbol": "000001", "timeout": 10.0}])
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["fund_code"], "000001.FUND_CN")
        self.assertEqual(record["fund_name"], "华夏成长混合")
        self.assertEqual(record["market"], "CN")
        self.assertEqual(record["fund_type"], "混合型-偏股")
        self.assertEqual(record["management_company"], "华夏基金管理有限公司")
        self.assertEqual(record["inception_date"], "2001-12-18")
        self.assertEqual(record["currency"], "CNY")
        self.assertEqual(record["benchmark"], "本基金暂不设业绩比较基准")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["source_ts"], "2024-01-09T18:00:00")
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(registry.validate_record(DatasetName.FUND_PROFILE, record), ())

    def test_adapter_accepts_bare_fund_code_and_normalizes_output_code(self) -> None:
        adapter = AkshareFundProfileAdapter(
            fetch_fund_profile=lambda **kwargs: _vertical_profile_rows()
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PROFILE,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["fund_code"], "000001.FUND_CN")

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(_vertical_profile_rows())
        adapter = AkshareFundProfileAdapter(
            fetch_fund_profile=lambda **kwargs: payload,
            now_fn=lambda: datetime(2024, 1, 10, 9, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PROFILE,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.FUND_CN",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["fund_name"], "华夏成长混合")

    def test_adapter_handles_horizontal_list_payload(self) -> None:
        adapter = AkshareFundProfileAdapter(
            fetch_fund_profile=lambda **kwargs: [
                {
                    "fund_code": "000001.FUND_CN",
                    "fund_name": "华夏成长混合",
                    "inception_date": "20011218",
                    "management_company": "华夏基金管理有限公司",
                    "fund_type": "混合型-偏股",
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PROFILE,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["inception_date"], "2001-12-18")

    def test_adapter_deduplicates_exact_duplicate_horizontal_records(self) -> None:
        rows = [
            {
                "fund_code": "000001",
                "fund_name": "华夏成长混合",
                "inception_date": "2001-12-18",
                "management_company": "华夏基金管理有限公司",
                "fund_type": "混合型-偏股",
            },
            {
                "fund_code": "000001",
                "fund_name": "华夏成长混合",
                "inception_date": "2001-12-18",
                "management_company": "华夏基金管理有限公司",
                "fund_type": "混合型-偏股",
            },
        ]
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: rows)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PROFILE,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001",),
            ),
        )
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_conflicting_duplicate_horizontal_records(self) -> None:
        rows = [
            {
                "fund_code": "000001",
                "fund_name": "华夏成长混合",
                "inception_date": "2001-12-18",
                "management_company": "华夏基金管理有限公司",
                "fund_type": "混合型-偏股",
            },
            {
                "fund_code": "000001",
                "fund_name": "华夏成长混合A",
                "inception_date": "2001-12-18",
                "management_company": "华夏基金管理有限公司",
                "fund_type": "混合型-偏股",
            },
        ]
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: rows)
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PROFILE,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001",),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_vertical_items(self) -> None:
        rows = _vertical_profile_rows() + [{"item": "基金名称", "value": "另一个名称"}]
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: rows)
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate AKShare fund profile item"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PROFILE,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001",),
                ),
            )

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001",),
                ),
            )

    def test_adapter_rejects_invalid_symbol_inputs(self) -> None:
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: [])
        invalid_cases = (
            (None, "requires exactly one fund code"),
            ((), "requires exactly one fund code"),
            (("000001", "000002"), "exactly one fund code"),
            (("",), "non-empty string"),
            (("000001.SZ",), "Unsupported fund profile market suffix"),
            (("00700.HK",), "Unsupported fund profile market suffix"),
            (("600000",), "A-share stock-like code"),
            (("510300",), "ETF-like fund code"),
            (("399001",), "Index-like code"),
            (("ABCDEF",), "Unsupported fund profile code format"),
        )
        for symbols, message in invalid_cases:
            with self.subTest(symbols=symbols):
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_PROFILE,
                            source_name=AKSHARE_SOURCE_ID,
                            symbols=symbols,
                        ),
                    )

    def test_adapter_rejects_malformed_payload(self) -> None:
        bad_payloads = (
            {"item": "基金代码", "value": "000001"},
            [1],
        )
        for payload in bad_payloads:
            with self.subTest(payload=payload):
                adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: payload)
                with self.assertRaisesRegex(ValueError, "payload"):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_PROFILE,
                            source_name=AKSHARE_SOURCE_ID,
                            symbols=("000001",),
                        ),
                    )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        rows = _vertical_profile_rows()
        rows = [row for row in rows if row["item"] != "基金公司"]
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: rows)
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PROFILE,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001",),
                ),
            )

    def test_adapter_rejects_invalid_required_values(self) -> None:
        invalid_cases = (
            ({"基金名称": " "}, "Invalid fund_name value"),
            ({"基金类型": 123}, "Invalid fund_type value type"),
            ({"成立时间": "not-a-date"}, "Invalid inception_date value"),
            ({"业绩比较基准": object()}, "Invalid benchmark value type"),
        )
        for overrides, message in invalid_cases:
            with self.subTest(overrides=overrides):
                def fake_fetch_fund_profile(**kwargs):
                    return _vertical_profile_rows(**overrides)

                adapter = AkshareFundProfileAdapter(
                    fetch_fund_profile=fake_fetch_fund_profile
                )
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_PROFILE,
                            source_name=AKSHARE_SOURCE_ID,
                            symbols=("000001",),
                        ),
                    )

    def test_adapter_rejects_source_code_mismatch(self) -> None:
        adapter = AkshareFundProfileAdapter(
            fetch_fund_profile=lambda **kwargs: _vertical_profile_rows(基金代码="000002")
        )
        with self.assertRaisesRegex(ValueError, "does not match requested fund"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PROFILE,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001",),
                ),
            )

    def test_adapter_does_not_pass_timeout_when_signature_lacks_it(self) -> None:
        calls: list[dict] = []

        def fake_fetch_fund_profile(symbol):
            calls.append({"symbol": symbol})
            return _vertical_profile_rows()

        adapter = AkshareFundProfileAdapter(fetch_fund_profile=fake_fetch_fund_profile)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PROFILE,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001",),
            ),
        )
        self.assertEqual(calls, [{"symbol": "000001"}])
        self.assertEqual(result.record_count, 1)

    def test_live_classifier_marks_only_environment_failures(self) -> None:
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: [])
        self.assertTrue(
            adapter._is_fund_profile_network_unavailable(
                OSError(111, "connection refused to danjuanapp.com endpoint")
            )
        )
        self.assertFalse(
            adapter._is_fund_profile_network_unavailable(
                ValueError("Invalid inception_date value")
            )
        )


if __name__ == "__main__":
    unittest.main()
