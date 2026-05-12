# src/api/main.py
import pandas as pd
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()
RAW_DATA_PATH = "data/raw/patients_raw.csv"


def load_raw_dataframe() -> pd.DataFrame:
    return pd.read_csv(
        RAW_DATA_PATH,
        dtype={"cccd": str, "so_dien_thoai": str},
    )


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(current_user: dict = Depends(get_current_user)):
    """
    Trả về raw patient data. Chỉ admin được phép đọc.
    """
    df = load_raw_dataframe().head(10)
    return JSONResponse(content=df.to_dict(orient="records"))


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(current_user: dict = Depends(get_current_user)):
    """
    Trả về anonymized data cho admin và ml_engineer.
    """
    df = load_raw_dataframe().head(10)
    df_anon = anonymizer.anonymize_dataframe(df)
    return JSONResponse(content=df_anon.to_dict(orient="records"))


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(current_user: dict = Depends(get_current_user)):
    """
    Trả về aggregated metrics không chứa PII.
    """
    df = load_raw_dataframe()
    metrics = (
        df.groupby("benh")
        .size()
        .reset_index(name="patient_count")
        .sort_values("patient_count", ascending=False)
    )
    return JSONResponse(content=metrics.to_dict(orient="records"))


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Chỉ admin được xóa. Ở lab này trả về phản hồi giả lập.
    """
    return {
        "deleted": True,
        "patient_id": patient_id,
        "deleted_by": current_user["username"],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
