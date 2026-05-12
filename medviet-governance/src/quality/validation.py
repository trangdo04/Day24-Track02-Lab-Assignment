# src/quality/validation.py
import pandas as pd

try:
    import great_expectations as gx
    from great_expectations.core.expectation_suite import ExpectationSuite
    from great_expectations.expectations.expectation_configuration import (
        ExpectationConfiguration,
    )
except ImportError:  # pragma: no cover - dependency may be missing locally
    gx = None
    ExpectationSuite = object
    ExpectationConfiguration = object


def build_patient_expectation_suite() -> ExpectationSuite:
    """
    Tạo expectation suite cho patient data.
    """
    if gx is None:
        raise ImportError("great_expectations is not installed")

    context = gx.get_context()
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]

    suite = ExpectationSuite(name="patient_data_suite")
    suite.add_expectation_configuration(
        ExpectationConfiguration(
            type="expect_column_values_to_not_be_null",
            kwargs={"column": "patient_id"},
        )
    )
    suite.add_expectation_configuration(
        ExpectationConfiguration(
            type="expect_column_value_lengths_to_equal",
            kwargs={"column": "cccd", "value": 12},
        )
    )
    suite.add_expectation_configuration(
        ExpectationConfiguration(
            type="expect_column_values_to_be_between",
            kwargs={
                "column": "ket_qua_xet_nghiem",
                "min_value": 0,
                "max_value": 50,
            },
        )
    )
    suite.add_expectation_configuration(
        ExpectationConfiguration(
            type="expect_column_values_to_be_in_set",
            kwargs={"column": "benh", "value_set": valid_conditions},
        )
    )
    suite.add_expectation_configuration(
        ExpectationConfiguration(
            type="expect_column_values_to_match_regex",
            kwargs={
                "column": "email",
                "regex": r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            },
        )
    )
    suite.add_expectation_configuration(
        ExpectationConfiguration(
            type="expect_column_values_to_be_unique",
            kwargs={"column": "patient_id"},
        )
    )

    context.suites.add_or_update(suite)
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath, dtype={"cccd": str, "so_dien_thoai": str})
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        },
    }

    if "cccd" in df.columns:
        original_cccd_values = set(
            pd.read_csv(
                "data/raw/patients_raw.csv",
                dtype={"cccd": str, "so_dien_thoai": str},
            )["cccd"].astype(str).tolist()
        )
        leaked_cccd = df["cccd"].astype(str).isin(original_cccd_values).any()
        if leaked_cccd:
            results["success"] = False
            results["failed_checks"].append("Found original CCCD values in anonymized data")

    critical_columns = ["patient_id", "ho_ten", "cccd", "benh", "ket_qua_xet_nghiem"]
    null_issues = [column for column in critical_columns if column in df.columns and df[column].isnull().any()]
    if null_issues:
        results["success"] = False
        results["failed_checks"].append(
            f"Null values found in columns: {', '.join(null_issues)}"
        )

    original_df = pd.read_csv(
        "data/raw/patients_raw.csv",
        dtype={"cccd": str, "so_dien_thoai": str},
    )
    if len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append("Row count does not match original dataset")

    return results
