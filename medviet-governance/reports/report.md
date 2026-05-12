# Báo Cáo Thực Hành: Data Governance cho Nền Tảng Y Tế MedViet

**Người thực hiện:** Đỗ Thị Thùy Trang  
**Mã số học viên:** 2A202600041

---

## 1. Giới thiệu

Thực hành này tập trung vào xây dựng một hệ thống quản trị dữ liệu toàn diện cho MedViet, với các thành phần chính:

| Thành phần | Mô tả |
|-----------|-------|
| Khởi tạo dữ liệu | Tạo tập dữ liệu bệnh nhân mô phỏng |
| Bảo vệ PII | Phát hiện và xóa danh sách thông tin cá nhân |
| Kiểm soát quyền hạn | Triển khai RBAC cho các role khác nhau |
| Bảo mật dữ liệu | Sử dụng envelope encryption (AES-256-GCM) |
| Đảm bảo chất lượng | Xác nhận tính toàn vẹn và đúng định dạng |
| Tuân thủ quy định | Quét bảo mật và checklist compliance

## 2. Phát sinh và xử lý dữ liệu thô

Để phục vụ quá trình test, script `scripts/generate_data.py` đã được thực thi nhằm tạo tập dữ liệu bệnh nhân ban đầu trong tệp `data/raw/patients_raw.csv`.

**Thông tin tập dữ liệu:**

- **Số lượng bản ghi:** 200 hồ sơ bệnh nhân
- **Cấu trúc dữ liệu:** 11 trường dữ liệu
  - `patient_id` - Định danh bệnh nhân
  - `ho_ten` - Họ tên (PII)
  - `cccd` - Chứng chỉ căn cước (PII)
  - `ngay_sinh` - Ngày sinh (PII)
  - `so_dien_thoai` - Số điện thoại (PII)
  - `email` - Địa chỉ email (PII)
  - `dia_chi` - Địa chỉ cư trú (PII)
  - `benh` - Chẩn đoán bệnh lý
  - `ket_qua_xet_nghiem` - Kết quả xét nghiệm
  - `bac_si_phu_trach` - Tên bác sĩ (PII)
  - `ngay_kham` - Ngày khám

**Dữ liệu nhạy cảm được xác định:** 7 trường chứa thông tin cá nhân nhạy cảm (PII), bao gồm họ tên, CCCD, ngày sinh, số điện thoại, email, địa chỉ, và bác sĩ phụ trách.

**Kết quả:** Tập dữ liệu đã được xử lý và xuất sang dạng ẩn danh tại `data/processed/patients_anonymized.csv`.

## 3. Phát hiện và Ẩn danh Thông tin Cá nhân (PII)

### Thực hiện

Các mô-đun xử lý PII đã được triển khai hoàn chỉnh:

- `src/pii/detector.py` - Công cụ phát hiện PII
- `src/pii/anonymizer.py` - Công cụ ẩn danh hóa dữ liệu
- `tests/test_pii.py` - Test suite kiểm chứng

### Các loại dữ liệu được nhận diện

Hệ thống hỗ trợ các pattern nhận dạng sau:

| Loại PII | Mô tả |
|---------|-------|
| `VN_CCCD` | Chứng chỉ căn cước công dân Việt Nam |
| `VN_PHONE` | Số điện thoại Việt Nam |
| `EMAIL_ADDRESS` | Địa chỉ email |
| `PERSON` | Tên cá nhân |

### Các chiến lược xử lý dữ liệu

Bốn phương thức ẩn danh được áp dụng:

- `replace` - Thay thế bằng giá trị synthetic
- `mask` - Che phủ một phần giá trị
- `hash` - Hash mã hóa giá trị
- `generalize` - Khái quát hóa thành danh mục

### Kết quả kiểm thử

Tất cả 6 test case đều thành công:

| Test case | Trạng thái |
|-----------|-----------|
| Phát hiện CCCD | ✓ Pass |
| Phát hiện số điện thoại | ✓ Pass |
| Phát hiện email | ✓ Pass |
| Tỷ lệ phát hiện >= 95% | ✓ Pass |
| Không có PII trong output | ✓ Pass |
| Cột non-PII giữ nguyên | ✓ Pass |

**Tóm lại:** Quy trình phát hiện và xử lý PII hoạt động hiệu quả với tỷ lệ phát hiện đạt 95% và toàn bộ dữ liệu nhạy cảm đều được xử lý thành công.

## 4. Kiểm soát Truy cập theo Role (RBAC) và API

### Các thành phần đã triển khai

- `src/access/policy.csv` - Cấu hình policy RBAC
- `src/access/model.conf` - Định nghĩa mô hình phân quyền
- `src/access/rbac.py` - Công cụ kiểm soát truy cập
- `src/api/main.py` - API endpoints

### Các vai trò được cấu hình

Hệ thống xác định 4 vai trò chính:

| Role | Quyền hạn |
|------|-----------|
| `admin` | Toàn bộ quyền, kể cả xóa dữ liệu |
| `ml_engineer` | Truy cập dữ liệu huấn luyện (đã ẩn danh) |
| `data_analyst` | Chỉ xem các chỉ số tổng hợp |
| `intern` | Hạn chế, chỉ truy cập sandbox |

### Các endpoint được triển khai

- `GET /api/patients/raw` - Lấy dữ liệu thô (chỉ admin)
- `GET /api/patients/anonymized` - Lấy dữ liệu đã ẩn danh
- `GET /api/metrics/aggregated` - Lấy chỉ số tổng hợp
- `DELETE /api/patients/{patient_id}` - Xóa hồ sơ (admin only)
- `GET /health` - Kiểm tra trạng thái hệ thống

### Kết quả kiểm chứng

Các test truy cập được thực hiện cho 3 người dùng mẫu:

| Người dùng | Thao tác | Kết quả | Mô tả |
|-----------|---------|--------|-------|
| bob | Truy cập raw data | 403 | Từ chối (không phải admin) |
| alice | Truy cập raw data | 200 | Cho phép (admin) |
| bob | Truy cập anonymized data | 200 | Cho phép (ml_engineer) |
| carol | Truy cập aggregated metrics | 200 | Cho phép (data_analyst) |
| bob | Xóa patient | 403 | Từ chối (không phải admin) |
| alice | Xóa patient | 200 | Cho phép (admin) |

**Kết luận:** RBAC hoạt động chính xác theo thiết kế. Dữ liệu thô chỉ cho admin, dữ liệu huấn luyện cho ml_engineer, chỉ số tổng hợp cho data_analyst, đảm bảo nguyên tắc least privilege.

## 5. Mã hóa Dữ liệu (Envelope Encryption)

### Triển khai

Mô-đun `src/encryption/vault.py` cung cấp khả năng mã hóa toàn diện cho dữ liệu nhạy cảm.

### Kiến trúc Envelope Encryption

Hệ thống áp dụng mô hình 2-tầng:

```
Data plaintext
    ↓
   [DEK (Data Encryption Key)]
    ↓
Data ciphertext
    ↓
   [KEK (Key Encryption Key)]
    ↓
Encrypted DEK + Encrypted Data
```

- **DEK** (Data Encryption Key): Khóa cấp dữ liệu, sử dụng để mã hóa dữ liệu thực tế
- **KEK** (Key Encryption Key): Khóa cấp cao, sử dụng để mã hóa DEK
- **Thuật toán:** AES-256-GCM (Advanced Encryption Standard 256-bit, Galois/Counter Mode)

### Kiểm chứng Round-trip

Quá trình mã hóa-giải mã được xác nhận qua test:

**Input:** `Nguyen Van A - CCCD: 012345678901`

| Bước | Kết quả |
|-----|--------|
| Mã hóa | ✓ Thành công |
| Giải mã | ✓ Khôi phục chính xác |
| Dữ liệu match | ✓ Yes |

**Kết luận:** Envelope encryption hoạt động chính xác. Dữ liệu được bảo vệ bằng mã hóa mạnh và khóa được quản lý an toàn theo mô hình hai tầng.

## 6. Kiểm Chứng Chất Lượng Dữ liệu

### Thực hiện

Mô-đun `src/quality/validation.py` định nghĩa các tiêu chí kiểm chứng dữ liệu.

### Bộ Expectation được cấu hình

6 tiêu chí kiểm tra được định nghĩa và áp dụng:

| # | Tiêu chí | Mô tả |
|---|---------|-------|
| 1 | Not null | `patient_id` không được rỗng |
| 2 | Format CCCD | `cccd` phải đúng 12 ký tự |
| 3 | Range test | `ket_qua_xet_nghiem` nằm trong giới hạn cho phép |
| 4 | Domain values | `benh` phải thuộc tập giá trị được phép |
| 5 | Email regex | `email` phải khớp pattern email chuẩn |
| 6 | Uniqueness | `patient_id` không được trùng lặp |

### Kết quả Validation

Tập dữ liệu ẩn danh được kiểm chứng với kết quả:

| Chỉ số | Giá trị |
|-------|--------|
| Trạng thái | ✓ Thành công |
| Số lỗi | 0 |
| Tổng dòng dữ liệu | 200 |

**Kết luận:** Dữ liệu đã ẩn danh hoàn toàn đáp ứng các yêu cầu về chất lượng và định dạng.

## 7. Quét Bảo mật (Security Scanning)

### 7.1 Pre-commit Hooks

Tệp `.github/hooks/pre-commit` được cấu hình để chạy các công cụ kiểm tra bảo mật tự động trước mỗi commit:

- `git-secrets` - Phát hiện credentials trong code
- `bandit` - Phân tích mã Python tìm lỗ hổng bảo mật
- `pip-audit` - Kiểm tra dependencies có lỗ hổng đã biết

### 7.2 Kết quả Bandit

Lệnh thực thi: `bandit -r src/ -f json`

**Báo cáo:**

| Mức độ | Số lượng | Chi tiết |
|-------|---------|---------|
| LOW | 3 | Cảnh báo `B311` |
| MEDIUM | 0 | - |
| HIGH | 0 | - |

**Phân tích:** Cảnh báo liên quan đến việc sử dụng `random` module để tạo dữ liệu CCCD và số điện thoại giả trong quá trình ẩn danh. Đây không phải sử dụng cho cryptography mà chỉ để tạo dữ liệu test, không ảnh hưởng đến an toàn lôgic mã hóa thực tế trong `src/encryption/vault.py`.

### 7.3 Kết quả pip-audit

Lệnh thực thi: `pip-audit --desc on`

**Phát hiện:** Môi trường Python hiện tại chứa một số dependencies có vulnerability được biết đến.

**Đánh giá:** Đây là kết quả từ môi trường phát triển trên máy hiện tại. Để dùng trong production, cần cập nhật các dependency đến các phiên bản an toàn hơn. Đối với bài lab, report này đã ghi nhận đầy đủ trạng thái hiện tại.

### 7.4 git-secrets

**Trạng thái:** ⚠ Chưa thực thi  
**Nguyên nhân:** Công cụ `git-secrets` chưa được cài đặt trên máy

### 7.5 TruffleHog

**Trạng thái:** ⚠ Chưa thực thi  
**Nguyên nhân:** Công cụ `trufflehog` chưa được cài đặt trên máy

## 8. Policy as Code (OPA)

### Triển khai

Tệp `policies/opa_policy.rego` định nghĩa các policy phân quyền sử dụng Open Policy Agent.

### Các Policy được cấu hình

Policy được thiết kế cho các role khác nhau với quyền hạn chi tiết:

| Role | Quyền hạn |
|------|-----------|
| `admin` | Toàn bộ hành động được phép |
| `ml_engineer` | Đọc/ghi `training_data` và `model_artifacts`; không được xóa `production_data` |
| `data_analyst` | Đọc `aggregated_metrics`; ghi `reports` |
| `intern` | Chỉ truy cập `sandbox_data` |
| Tất cả | Dữ liệu `restricted` không được export ra ngoài Vietnam (VN) |

### Trạng thái Kiểm chứng

**Trạng thái:** ⚠ Chưa thực thi  
**Nguyên nhân:** CLI tool `opa` chưa được cài đặt trên máy  

**Ghi chú:** Policy Rego đã được viết hoàn chỉnh và sẵn sàng để kiểm chứng bằng lệnh `opa eval` khi công cụ được cài đặt.

## 9. Compliance Checklist

### Triển khai

Tệp `compliance_checklist.md` đã được cập nhật với các yêu cầu compliance và trạng thái triển khai.

### Nội dung Checklist

Các mục chính trong checklist:

- **Người phụ trách:** Liên hệ DPO (Data Protection Officer)
- **Audit Logging:** Giải pháp ghi nhật ký toàn diện hành động người dùng
- **Breach Detection:** Giải pháp phát hiện và cảnh báo vi phạm dữ liệu
- **Technical Controls:** Các biện pháp kỹ thuật để tuân thủ quy định bảo vệ dữ liệu

**Kết luận:** Checklist được hoàn thiện với đầy đủ các mục compliance, cung cấp hướng dẫn chi tiết cho từng vấn đề quản trị dữ liệu và bảo vệ thông tin cá nhân.

## 10. Bằng Chứng Kiểm Chứng

### Các kết quả đã được xác minh

Tất cả các thành phần chính đều được kiểm chứng trực tiếp trong môi trường hiện tại:

| Thành phần | Trạng thái | Ghi chú |
|-----------|-----------|--------|
| Phát sinh raw dataset | ✓ Thành công | 200 bản ghi được tạo |
| Tạo anonymized dataset | ✓ Thành công | Dữ liệu PII được xử lý |
| Unit tests (PII) | ✓ 6/6 pass | pytest tests/ -v --tb=short |
| RBAC/API smoke test | ✓ Đúng | Phân quyền hoạt động chính xác |
| Encryption round-trip | ✓ Thành công | Mã hóa/giải mã khôi phục chính xác |
| Data validation | ✓ Thành công | Tất cả 6 expectation pass |
| Bandit scan | ✓ Thực thi được | 3 cảnh báo LOW (không critical) |
| pip-audit scan | ✓ Thực thi được | Report được ghi nhận |

## 11. Giới Hạn Môi Trường

### Các Công Cụ Chưa Có Sẵn

Một số công cụ bảo mật ngoài systtme chưa được cài đặt:

| Công cụ | Mục đích | Trạng thái |
|---------|---------|-----------|
| `git-secrets` | Phát hiện credentials trong git history | ⚠ Chưa cài |
| `trufflehog` | Tìm secret keys trong code | ⚠ Chưa cài |
| `opa` CLI | Kiểm chứng OPA policy | ⚠ Chưa cài |
| `vi_core_news_lg` | Mô hình NER tiếng Việt cho spaCy | ⚠ Incompatible |

### Giải Pháp Áp Dụng

Để đảm bảo pipeline hoạt động ổn định trên môi trường hiện tại:

- **PII Detection:** Sử dụng mô hình local blank của spaCy kết hợp với pattern recognizers. Cách này vẫn đạt tỷ lệ phát hiện >= 95%
- **Security Report:** Ghi rõ trạng thái các công cụ chưa cài thay vì để trống hoặc bỏ qua
- **Documentation:** Mô tả cách lắp đặt thêm các công cụ để người khác có thể hoàn thiện khi cần

**Kết luận:** Mặc dù có một số giới hạn công cụ, các tính năng chính của lab vẫn hoạt động đầy đủ và có thể xác minh được.

## 12. Tổng Kết

### Các Hạng Mục Hoàn Thành

Những thành phần chính của bài lab đã được triển khai đầy đủ:

- ✓ **Phát hiện PII (PII Detection)** - Đạt >= 95% tỷ lệ phát hiện
- ✓ **Ẩn danh hóa dữ liệu (Anonymization)** - 4 chiến lược xử lý được triển khai
- ✓ **RBAC API** - 4 role, 5 endpoint, kiểm soát quyền hạn chính xác
- ✓ **Mã hóa toàn diện (Envelope Encryption)** - AES-256-GCM round-trip thành công
- ✓ **Kiểm chứng chất lượng (Data Quality Validation)** - 6 expectation, 0 lỗi
- ✓ **Tài liệu Compliance** - Checklist đầy đủ với hướng dẫn
- ✓ **Security Scanning** - Bandit & pip-audit đã chạy, report được ghi nhận

### Các Hạng Mục Phụ Thuộc Công Cụ Ngoài

Các thành phần sau phụ thuộc vào cài đặt thêm:

- `git-secrets` - Để quét credentials đầy đủ
- `trufflehog` - Để tìm secret keys nâng cao
- `opa` CLI - Để kiểm chứng OPA policy với lệnh `opa eval`

### Cách Tiếp Tục

Nếu cần hoàn thiện thêm, thực hiện:

1. Cài đặt các công cụ bổ sung từ package manager
2. Chạy các lệnh trong README để sinh thêm bằng chứng runtime
3. Cập nhật report với kết quả mới

**Đánh giá chung:** Bài lab đã hoàn thành thành công tất cả các hạng mục chính. Hệ thống quản trị dữ liệu y tế đã được xây dựng với các layer bảo vệ toàn diện: phát hiện/xử lý PII, kiểm soát quyền hạn, mã hóa, validation, và tuân thủ quy định.
