from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKMinuteBarsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


class _FakeDataFrame:
    def __init__(self, records):
        self._records = list(records)

    def to_dict(self, orient="records"):
        if orient != "records":
            raise ValueError("Only orient='records' is supported in test fixture.")
        return list(self._records)


def _build_adapter(
    *,
    fetch_hk_hist_min=None,
    fetch_hk_security_profile=None,
    now_fn=None,
    minute_period="5",
    price_adjustment="raw",
) -> AkshareHKMinuteBarsAdapter:
    return AkshareHKMinuteBarsAdapter(
        fetch_hk_hist_min=fetch_hk_hist_min,
        fetch_hk_security_profile=fetch_hk_security_profile,
        now_fn=now_fn,
        minute_period=minute_period,
        price_adjustment=price_adjustment,
    )


class AkshareHKMinuteBarsAdapterTests(unittest.TestCase):
    def test_fetch_source_result_normalizes_and_validates_multi_symbol_batch(self) -> None:
        minute_calls: list[dict[str, object]] = []
        profile_calls: list[dict[str, object]] = []
        now = datetime(2024, 2, 1, 9, 30, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_hk_security_profile(**kwargs):
            profile_calls.append(kwargs)
            symbol = kwargs["symbol"]
            return [
                {
                    "证券代码": f"{symbol}.HK",
                    "证券简称": f"名称-{symbol}",
                    "上市日期": "2004-06-16",
                    "证券类型": "非H股",
                    "交易所": "香港交易所",
                }
            ]

        def fake_fetch_hk_hist_min(**kwargs):
            minute_calls.append(kwargs)
            symbol = kwargs["symbol"]
            if symbol == "00700":
                return _FakeDataFrame(
                    [
                        {
                            "代码": "00700.HK",
                            "时间": "2024-01-03 09:35:00",
                            "开盘": 300.5,
                            "收盘": 301.0,
                            "最高": 301.2,
                            "最低": 300.1,
                            "成交量": 120000.0,
                            "成交额": 36120000.0,
                        },
                        {
                            "代码": "00700.HK",
                            "时间": "2024-01-03 09:40:00",
                            "开盘": 301.0,
                            "收盘": 302.0,
                            "最高": 302.1,
                            "最低": 300.8,
                            "成交量": 90000.0,
                            "成交额": 27180000.0,
                        },
                    ]
                )
            return _FakeDataFrame(
                [
                    {
                        "代码": "00005.HK",
                        "时间": "2024-01-03 09:35:00",
                        "开盘": 62.1,
                        "收盘": 62.4,
                        "最高": 62.5,
                        "最低": 62.0,
                        "成交量": 50000.0,
                        "成交额": 3115000.0,
                    }
                ]
            )

        adapter = _build_adapter(
            fetch_hk_hist_min=fake_fetch_hk_hist_min,
            fetch_hk_security_profile=fake_fetch_hk_security_profile,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 3),
                    end_date=date(2024, 1, 3),
                    symbols=("00700.HK", "00005"),
                ),
                fetched_at=datetime(2024, 2, 1, 9, 35, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(
            profile_calls,
            [{"symbol": "00700"}, {"symbol": "00005"}],
        )
        self.assertEqual(
            minute_calls,
            [
                {
                    "symbol": "00700",
                    "period": "5",
                    "start_date": "2024-01-03 09:30:00",
                    "end_date": "2024-01-03 16:10:00",
                    "adjust": "",
                },
                {
                    "symbol": "00005",
                    "period": "5",
                    "start_date": "2024-01-03 09:30:00",
                    "end_date": "2024-01-03 16:10:00",
                    "adjust": "",
                },
            ],
        )
        self.assertEqual(result.record_count, 3)
        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            ["00005.HK", "00700.HK", "00700.HK"],
        )
        first_record = result.normalized_records[0]
        self.assertEqual(first_record["market"], "HK")
        self.assertEqual(first_record["trade_date"], "2024-01-03")
        self.assertEqual(first_record["bar_time"], "2024-01-03T09:35:00")
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["ingested_at"], now.isoformat())
        self.assertEqual(first_record["schema_version"], "v1")
        self.assertIn("amount", first_record)
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.MINUTE_BARS, record),
                (),
            )

    def test_adapter_accepts_raw_numeric_symbol_and_deduplicates_requested_symbols(self) -> None:
        profile_calls: list[str] = []

        def fake_fetch_hk_security_profile(**kwargs):
            profile_calls.append(kwargs["symbol"])
            return [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "非H股",
                    "交易所": "香港交易所",
                }
            ]

        adapter = _build_adapter(
            fetch_hk_security_profile=fake_fetch_hk_security_profile,
            fetch_hk_hist_min=lambda **kwargs: [
                {
                    "代码": "00700.HK",
                    "时间": "2024-01-03 09:35:00",
                    "开盘": 300.5,
                    "收盘": 301.0,
                    "最高": 301.2,
                    "最低": 300.1,
                    "成交量": 120000.0,
                }
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MINUTE_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 3),
                end_date=date(2024, 1, 3),
                symbols=("00700", "00700.HK"),
            ),
        )
        self.assertEqual(profile_calls, ["00700"])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 3),
                    end_date=date(2024, 1, 3),
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_requires_bounded_dates(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "requires bounded date window"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_old_one_minute_window(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [],
            fetch_hk_hist_min=lambda **kwargs: [],
            now_fn=lambda: datetime(2026, 6, 12, 9, 0, 0, tzinfo=timezone.utc),
            minute_period="1",
        )
        with self.assertRaisesRegex(ValueError, "recent trailing window"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 1),
                    end_date=date(2026, 5, 1),
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_non_stock_symbol_via_profile_validation(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: (_ for _ in ()).throw(
                TypeError("'NoneType' object is not subscriptable")
            ),
            fetch_hk_hist_min=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "stock-only minute-bars adapter"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 3),
                    end_date=date(2024, 1, 3),
                    symbols=("02800.HK",),
                ),
            )

    def test_adapter_rejects_route_signature_incompatibility(self) -> None:
        def incompatible_fetch(symbol):
            return []

        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "非H股",
                    "交易所": "香港交易所",
                }
            ],
            fetch_hk_hist_min=incompatible_fetch,
        )
        with self.assertRaisesRegex(RuntimeError, "does not accept required argument"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 3),
                    end_date=date(2024, 1, 3),
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "非H股",
                    "交易所": "香港交易所",
                }
            ],
            fetch_hk_hist_min=lambda **kwargs: [
                {
                    "代码": "00700.HK",
                    "时间": "2024-01-03 09:35:00",
                    "开盘": 300.5,
                    "收盘": 301.0,
                    "最高": 301.2,
                    "最低": 300.1,
                    "成交量": 120000.0,
                },
                {
                    "代码": "00700.HK",
                    "时间": "2024-01-03 09:35:00",
                    "开盘": 300.5,
                    "收盘": 302.0,
                    "最高": 301.2,
                    "最低": 300.1,
                    "成交量": 120000.0,
                },
            ],
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate HK minute-bars row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 3),
                    end_date=date(2024, 1, 3),
                    symbols=("00700.HK",),
                ),
            )
