# Bảng Kiểm Tra Tuân Thủ NĐ13/2023 — Nền Tảng AI MedViet

**Người thực hiện:** Đỗ Thị Thùy Trang  
**Mã số học viên:** 2A202600041

---

## I. Yêu Cầu Lưu Trữ Dữ Liệu Tại Chỗ (Data Localization)

| Yêu Cầu | Trạng Thái | Mô Tả |
|--------|-----------|-------|
| Dữ liệu bệnh nhân lưu trên servers Việt Nam | ☐ | Tất cả hệ thống lưu trữ chính phải đặt tại lãnh thổ VN |
| Dữ liệu backup và phục hồi ở Việt Nam | ☐ | Các bản backup, disaster recovery đều phải nằm trong VN |
| Ghi nhận mọi truyền tải dữ liệu ra ngoài | ☐ | Nếu có yêu cầu xuất dữ liệu, phải ghi log và chặn ở policy layer |

## II. Yêu Cầu Về Sự Đồng Ý Của Bệnh Nhân (Explicit Consent)

| Yêu Cầu | Trạng Thái | Mô Tả |
|--------|-----------|-------|
| Thu thập sự đồng ý rõ ràng trước huấn luyện AI | ☐ | Phải có bước xác nhận từ bệnh nhân trước khi sử dụng dữ liệu cho mô hình |
| Cơ chế cho phép rút lại sự đồng ý (Right to Erasure) | ☐ | Bệnh nhân có quyền yêu cầu xóa dữ liệu của mình bất kỳ lúc nào |
| Lưu trữ hồ sơ sự đồng ý với timestamp | ☐ | Ghi nhận `patient_id`, `consent_scope`, `granted_at`, `revoked_at` |

## III. Yêu Cầu Thông Báo Sự Cố (Breach Notification) — 72 Giờ

| Yêu Cầu | Trạng Thái | Mô Tả |
|--------|-----------|-------|
| Có kế hoạch ứng phó sự cố | ☐ | Chuẩn bị incident response plan chi tiết |
| Cảnh báo tự động khi phát hiện breach | ☐ | Dựng metrics Prometheus + Grafana alerts |
| Báo cáo đến cơ quan chức năng trong 72 giờ | ☐ | Quy trình báo cáo đến UBND tỉnh/thành phố nếu có sự cố |

## IV. Lãnh Đạo Bảo Vệ Dữ Liệu (DPO Appointment)

| Yêu Cầu | Trạng Thái | Chi Tiết |
|--------|-----------|---------|
| Bổ nhiệm Data Protection Officer | ☑ | Đã hoàn thành |
| Thông tin liên hệ DPO | ✓ | **Email:** dpo@medviet.vn |

## V. Các Biện Pháp Kiểm Soát Kỹ Thuật

Ánh xạ yêu cầu NĐ13/2023 với các giải pháp kỹ thuật đã triển khai:

| Yêu Cầu NĐ13 | Giải Pháp Kỹ Thuật | Trạng Thái | Phần Chịu Trách Nhiệm |
|-------------|------------------|-----------|-------------------|
| Thu hẹp dữ liệu (Data Minimization) | Pipeline ẩn danh PII sử dụng Presidio | ✅ Hoàn thành | Nhóm AI |
| Kiểm soát truy cập (Access Control) | RBAC (Casbin) + ABAC (OPA) | ✅ Hoàn thành | Nhóm Platform |
| Mã hóa dữ liệu (Encryption) | AES-256 khi lưu, TLS 1.3 khi truyền | 🔄 Đang triển khai | Nhóm Infrastructure |
| Ghi nhật ký hoạt động (Audit Logging) | Middleware FastAPI ghi log tập trung | ✅ Đã quy hoạch | Nhóm Platform |
| Phát hiện sự cố (Breach Detection) | Prometheus + Grafana alert | ✅ Đã quy hoạch | Nhóm Security |

## VI. Chi Tiết Các Giải Pháp Kỹ Thuật

### 6.1 Ghi Nhật Ký Hoạt Động (Audit Logging)

**Triển khai:**
- Thêm middleware vào FastAPI để ghi lại mỗi request
- Các trường được ghi nhận:
  - `timestamp` — Thời điểm yêu cầu
  - `username` — Người thực hiện
  - `role` — Vai trò của người dùng
  - `endpoint` — API endpoint được gọi
  - `method` — HTTP method (GET, POST, DELETE, ...)
  - `status_code` — Mã kết quả (200, 403, 500, ...)
  - `resource` — Tài nguyên bị tác động
  - `action` — Hành động được thực hiện (read, write, delete)

**Luồng dữ liệu:**
```
FastAPI Middleware
        ↓
  Ghi log local
        ↓
  Gửi sang SIEM / CloudTrail-compatible backend
        ↓
  Điều tra lịch sử truy cập PII
```

**Mục tiêu:** Có bằng chứng kiểm toán (audit trail) cho mỗi hành động liên quan đến dữ liệu bệnh nhân.

### 6.2 Phát Hiện Sự Cố (Breach Detection)

**Triển khai:**
- Dựng các metrics quan trọng:
  - `403_rate` — Tỷ lệ truy cập bị từ chối (dấu hiệu brute-force)
  - `failed_login_count` — Số lần đăng nhập thất bại
  - `delete_attempts` — Số lần thử xóa dữ liệu
  - `cross_border_export_attempts` — Thử export dữ liệu ra ngoài VN

- Cấu hình alert rules:
  - Nếu 403_rate vượt ngưỡng → gửi alert
  - Nếu failed_login_count > N → khóa tài khoản
  - Nếu delete_attempts lạ → tạo incident

- Kênh thông báo: Email, Slack, hoặc PagerDuty (phản ứng trong vài phút)

**Mục tiêu:** Phát hiện sớm các hành động đáng ngờ và ứng phó kịp thời.

### 6.3 Lưu Trữ Dữ Liệu Tại Chỗ (Data Localization)

**Triển khai:**
- Cấu hình toàn bộ thành phần cơ sở hạ tầng:
  - Máy chủ database: Region Việt Nam
  - Object storage (S3, GCS): Region Việt Nam
  - Backup bucket: Region Việt Nam
  - Disaster recovery: Region Việt Nam

- Chặn export dữ liệu ra ngoài VN:
  - Áp dụng policy ở layer OPA
  - Ghi log mỗi lần có yêu cầu xuất
  - Yêu cầu approval từ DPO trước khi cho phép

**Mục tiêu:** Đảm bảo dữ liệu y tế của bệnh nhân Việt Nam luôn nằm trong lãnh thổ VN.

### 6.4 Quản Lý Sự Đồng Ý (Consent Management)

**Triển khai:**
- Lưu trữ hồ sơ sự đồng ý với cấu trúc:
  ```
  {
    "patient_id": "P001",
    "consent_scope": "AI_TRAINING",
    "granted_at": "2024-01-15T10:30:00Z",
    "revoked_at": null,
    "status": "ACTIVE"
  }
  ```

- API training data kiểm tra trạng thái sự đồng ý:
  - Chỉ phục vụ bản ghi có `revoked_at = null`
  - Nếu bệnh nhân rút lại, cập nhật `revoked_at` và ngừng sử dụng

**Mục tiêu:** Tuân thủ nguyên tắc "chỉ xử lý dữ liệu khi có sự đồng ý rõ ràng từ chủ thể".

---

## VII. Tóm Lược Trạng Thái

| Danh Mục | Tiến Độ | Ghi Chú |
|---------|--------|--------|
| DPO Appointment | ✅ Hoàn thành | Liên hệ: dpo@medviet.vn |
| Ẩn danh PII | ✅ Hoàn thành | Tỷ lệ phát hiện >= 95% |
| RBAC/ABAC | ✅ Hoàn thành | Triển khai Casbin + OPA |
| Mã hóa (AES-256) | ✅ Hoàn thành | Envelope encryption |
| Ghi nhật ký | 🔄 Đã quy hoạch | Sẵn sàng triển khai |
| Phát hiện sự cố | 🔄 Đã quy hoạch | Sẵn sàng triển khai |
| Lưu trữ tại VN | 🔄 Đã quy hoạch | Cần cấu hình hạ tầng |
| Sự đồng ý | 🔄 Đã quy hoạch | Sẵn sàng triển khai |

