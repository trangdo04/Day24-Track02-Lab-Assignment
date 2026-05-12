# src/pii/detector.py
from pathlib import Path

import spacy
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

EMAIL_REGEX = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
PHONE_REGEX = r"\b0[35789]\d{8}\b"
CCCD_REGEX = r"\b\d{12}\b"
PERSON_REGEX = r"\b[A-ZĐ][A-Za-zÀ-ỹà-ỹ]*(?:\s+[A-ZĐ][A-Za-zÀ-ỹà-ỹ]*){1,4}\b"


def get_local_vi_model_name() -> str:
    preferred_model = "vi_core_news_lg"
    if spacy.util.is_package(preferred_model):
        return preferred_model

    model_dir = Path(__file__).resolve().parents[2] / ".models" / "vi_blank_model"
    if not model_dir.exists():
        model_dir.parent.mkdir(parents=True, exist_ok=True)
        # Dùng multilingual blank pipeline để tránh phụ thuộc pyvi khi không có
        # model tiếng Việt cài sẵn trong môi trường local.
        spacy.blank("xx").to_disk(model_dir)
    return str(model_dir)


def build_vietnamese_analyzer() -> AnalyzerEngine:
    """
    Xây dựng AnalyzerEngine với recognizers cho dữ liệu tiếng Việt.

    Ưu tiên dùng spaCy Vietnamese model nếu có. Nếu model chưa được cài,
    analyzer vẫn chạy bằng pattern recognizers để phục vụ lab và test local.
    """
    registry = RecognizerRegistry(supported_languages=["vi"])

    recognizers = [
        PatternRecognizer(
            supported_entity="VN_CCCD",
            patterns=[Pattern(name="cccd_pattern", regex=CCCD_REGEX, score=0.9)],
            context=["cccd", "căn cước", "chứng minh", "cmnd"],
            supported_language="vi",
        ),
        PatternRecognizer(
            supported_entity="VN_PHONE",
            patterns=[Pattern(name="vn_phone", regex=PHONE_REGEX, score=0.85)],
            context=["điện thoại", "sdt", "phone", "liên hệ"],
            supported_language="vi",
        ),
        PatternRecognizer(
            supported_entity="EMAIL_ADDRESS",
            patterns=[Pattern(name="email_pattern", regex=EMAIL_REGEX, score=0.95)],
            context=["email", "mail", "liên hệ"],
            supported_language="vi",
        ),
        PatternRecognizer(
            supported_entity="PERSON",
            patterns=[Pattern(name="vn_person", regex=PERSON_REGEX, score=0.7)],
            context=["bệnh nhân", "họ tên", "bac si", "bác sĩ", "doctor", "bs"],
            supported_language="vi",
        ),
    ]

    for recognizer in recognizers:
        registry.add_recognizer(recognizer)

    model_name = get_local_vi_model_name()
    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "vi", "model_name": model_name}],
        }
    )
    nlp_engine = provider.create_engine()

    return AnalyzerEngine(
        registry=registry,
        nlp_engine=nlp_engine,
        supported_languages=["vi"],
    )


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """
    Detect PII trong text tiếng Việt.
    Trả về list các RecognizerResult.
    """
    return analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
    )
