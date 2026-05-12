# src/pii/anonymizer.py
import hashlib
import random

import pandas as pd
from faker import Faker
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")
random.seed(42)


def generate_fake_cccd() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def generate_fake_phone() -> str:
    prefix = f"0{random.choice([3, 5, 7, 8, 9])}"
    return prefix + "".join(str(random.randint(0, 9)) for _ in range(8))


def mask_value(value: str) -> str:
    if len(value) <= 1:
        return value
    if " " in value:
        masked_parts = []
        for part in value.split():
            if len(part) <= 1:
                masked_parts.append(part)
            else:
                masked_parts.append(part[0] + "*" * (len(part) - 1))
        return " ".join(masked_parts)
    return value[:2] + "*" * max(len(value) - 2, 0)


class MedVietAnonymizer:
    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        """
        Anonymize text với strategy được chọn.

        Strategies:
        - replace: thay bằng fake data
        - mask: giữ ký tự đầu rồi che phần còn lại
        - hash: SHA-256 one-way hash theo từng entity
        - generalize: fallback che bằng nhãn tổng quát
        """
        text = str(text)
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", {"new_value": generate_fake_cccd()}),
                "VN_PHONE": OperatorConfig("replace", {"new_value": generate_fake_phone()}),
            }
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=operators,
            )
            return anonymized.text

        replacements = []
        for result in results:
            original = text[result.start:result.end]
            if strategy == "mask":
                replacement = mask_value(original)
            elif strategy == "hash":
                replacement = hashlib.sha256(original.encode("utf-8")).hexdigest()
            else:
                replacement = f"[{result.entity_type}]"
            replacements.append((result.start, result.end, replacement))

        anonymized_text = text
        for start, end, replacement in sorted(replacements, reverse=True):
            anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
        return anonymized_text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Anonymize toàn bộ DataFrame.
        - Cột text dùng anonymize_text()
        - CCCD và số điện thoại được replace trực tiếp
        - Benh, ket_qua_xet_nghiem, patient_id được giữ nguyên
        """
        df_anon = df.copy()

        for column in ["ho_ten", "email", "dia_chi", "bac_si_phu_trach"]:
            if column in df_anon.columns:
                df_anon[column] = df_anon[column].astype(str).apply(self.anonymize_text)

        if "cccd" in df_anon.columns:
            df_anon["cccd"] = [generate_fake_cccd() for _ in range(len(df_anon))]

        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = [generate_fake_phone() for _ in range(len(df_anon))]

        if "ngay_sinh" in df_anon.columns:
            df_anon["ngay_sinh"] = df_anon["ngay_sinh"].astype(str).apply(
                lambda value: value[-4:] if len(value) >= 4 else value
            )

        return df_anon

    def calculate_detection_rate(
        self,
        original_df: pd.DataFrame,
        pii_columns: list,
    ) -> float:
        """
        Tính % PII được detect thành công.
        """
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].astype(str):
                total += 1
                results = detect_pii(value, self.analyzer)
                if results:
                    detected += 1

        return detected / total if total > 0 else 0.0
