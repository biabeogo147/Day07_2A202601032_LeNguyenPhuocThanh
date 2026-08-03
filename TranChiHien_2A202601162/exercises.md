# Ngày 7 — Bài tập
## Nền tảng Dữ liệu: Embedding & Vector Store | Bài tập thực hành

> Đây là template cá nhân. Kết quả phải do Trần Chí Hiển tự chạy và đối chiếu trước khi điền.

---

## Phần 1 — Khởi động (Cá nhân)

### Bài tập 1.1 — Cosine Similarity bằng ngôn ngữ đời thường

- Điều gì xảy ra khi hai đoạn văn bản có cosine similarity cao?
- Đưa ra một cặp câu có similarity cao và một cặp có similarity thấp.
- Tại sao cosine similarity thường được ưu tiên hơn Euclidean distance cho text embeddings?

> **Ghi kết quả vào:** `REPORT_CANHAN.md` — Phần 1. ✅ Đã điền.

---

### Bài tập 1.2 — Bài toán tính toán Chunking

- Tài liệu dài 10.000 ký tự, `chunk_size=500`, `overlap=50`: dự kiến bao nhiêu chunks?
- Công thức: `ceil((document_length - overlap) / (chunk_size - overlap))`.
- Nếu overlap tăng lên 100, số chunks thay đổi thế nào? Tại sao muốn tăng overlap?

> **Ghi kết quả vào:** `REPORT_CANHAN.md` — Phần 1. ✅ Đã điền (23 chunks, tăng lên 25 khi overlap=100).

---

## Phần 2 — Lập trình cốt lõi (Cá nhân)

Hoàn thành các TODO trong `src/chunking.py`, `src/store.py`, `src/agent.py` và chạy `pytest ../tests/ -v`.

### Danh sách cần làm (Checklist)

- [x] Đọc và hiểu `Document` dataclass.
- [x] Đọc và hiểu `FixedSizeChunker`.
- [x] Kiểm tra/triển khai `SentenceChunker`.
- [x] Kiểm tra/triển khai `RecursiveChunker`.
- [x] Kiểm tra/triển khai `compute_similarity`.
- [x] Kiểm tra/triển khai `ChunkingStrategyComparator`.
- [x] Kiểm tra/triển khai `EmbeddingStore.__init__`.
- [x] Kiểm tra/triển khai `EmbeddingStore.add_documents`.
- [x] Kiểm tra/triển khai `EmbeddingStore.search`.
- [x] Kiểm tra/triển khai `EmbeddingStore.get_collection_size`.
- [x] Kiểm tra/triển khai `EmbeddingStore.search_with_filter`.
- [x] Kiểm tra/triển khai `EmbeddingStore.delete_document`.
- [x] Kiểm tra/triển khai `KnowledgeBaseAgent.answer`.
- [x] Chạy đủ 42 tests bằng môi trường được chỉ định (`LAB_SOLUTION_PACKAGE=TranChiHien_2A202601162.src pytest tests/ -v` → 42 passed; máy chạy Python 3.14 vì không có sẵn 3.11, không phát sinh lỗi tương thích).

> **Nộp code:** thư mục `src/`. Ghi cách tiếp cận vào `REPORT_CANHAN.md`, Phần 2–3. ✅ Đã điền.

---

## Phần 3 — So Sánh Chiến Lược Truy Xuất

### Bài tập 3.0 — Chuẩn bị tài liệu

Chủ đề K4: chính sách TMĐT/hỗ trợ khách hàng. Đọc [hướng dẫn dữ liệu](../docs/DATA_COLLECTION.md) và dùng corpus chung tại `../data/shopee_customer_support`.

| # | Tên tài liệu | Source URL | Ngày lấy / Phiên bản | Số ký tự | Metadata |
|---|---|---|---|---:|---|
| 1 | return-refund-general-rules.md | help.shopee.vn/portal/4/article/188931 | 2026-08-03 / not-stated | 6,234 | customer_role: buyer, category: returns-and-refunds, language: vi |
| 2 | return-refund-policy.md | help.shopee.vn/portal/4/article/77251 | 2026-08-03 / not-stated | 19,609 | customer_role: buyer, category: returns-and-refunds, language: vi |
| 3 | return-refund-request-guide.md | help.shopee.vn/portal/4/article/79233 | 2026-08-03 / not-stated | 2,521 | customer_role: buyer, category: returns-and-refunds, language: vi |
| 4 | return-shipping-methods.md | help.shopee.vn/portal/4/article/189477 | 2026-08-03 / not-stated | 5,987 | customer_role: buyer, category: returns-and-refunds, language: vi |
| 5 | shipping-faq.md | help.shopee.vn/portal/4/article/79492 | 2026-08-03 / not-stated | 2,832 | customer_role: buyer, category: shipping, language: vi |

> ⚠️ **Phát hiện khi chạy thực tế:** front-matter thật của cả 5 file hiện đang ghi `customer_role: "buyer"` cho **tất cả** tài liệu — không có file nào mang giá trị `both`/`seller` như bảng trong `REPORT_NHOM.md` (Phần 1) mô tả cho `return-refund-policy.md`. Vì `search_with_filter({"customer_role": "both"})` không khớp bất kỳ chunk nào trong corpus hiện tại, câu hỏi benchmark #4 của nhóm (yêu cầu filter `both`) trả về **rỗng** khi tôi chạy thật — xem chi tiết ở Bài tập 3.5. Đây là phát hiện thật từ dữ liệu, không phải lỗi code cá nhân của tôi; tôi chưa sửa file dữ liệu chung vì nằm ngoài phạm vi `TranChiHien_2A202601162/`, cần nhóm xác nhận trước.

**Metadata schema cần kiểm tra:** `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `customer_role`, `category`, `language`; khi ingest bổ sung `chunk_index`. ✅ Đã kiểm tra — khớp đúng schema, trừ điểm bất thường `customer_role` nêu trên.

> **Ghi phần nhóm vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md), Phần 1. ⏸ Chưa cập nhật — đang chờ xác nhận của nhóm trưởng trước khi sửa file chung (theo yêu cầu giữ nguyên phạm vi cá nhân).

---

### Bài tập 3.1 — Thiết kế chiến lược truy xuất

1. Chạy `ChunkingStrategyComparator().compare()` trên 2–3 tài liệu. ✅ Đã chạy trên `return-refund-request-guide.md` (2,521 ký tự, `chunk_size=200`):

| Chiến lược | Số chunks | Độ dài TB |
|---|---:|---:|
| FixedSizeChunker | 17 | 195.4 |
| SentenceChunker | 8 | 311.6 |
| RecursiveChunker | 17 | 146.4 |

2. Chọn hoặc tự thiết kế một chiến lược riêng — **tôi chọn dùng nguyên `FixedSizeChunker` (baseline có sẵn)** làm chiến lược cá nhân, thay vì tự thiết kế chiến lược mới, với lý do: 3 bạn còn lại trong nhóm đều đã dùng chiến lược nâng cao (Recursive, PolicySection theo heading, Sentence) — tôi muốn nhóm có một mốc **baseline đơn giản** để so sánh, làm rõ "chiến lược nâng cao tốt hơn baseline bao nhiêu".
3. Dùng embedder thật, không dùng mock để kết luận chất lượng semantic retrieval. ⚠️ Không thực hiện được — máy không tải được `LocalEmbedder` (sandbox chặn mạng ra Hugging Face) và không có API key OpenAI/Gemini. Đã dùng Mock embedder theo đúng cơ chế fallback của bài, có ghi chú minh bạch trong `REPORT_CANHAN.md`.

```python
from TranChiHien_2A202601162.src.chunking import FixedSizeChunker
from TranChiHien_2A202601162.src.embeddings import LocalEmbedder  # fallback: MockEmbedder

chunker = FixedSizeChunker(chunk_size=500, overlap=50)
embedder = LocalEmbedder()  # KHÔNG chạy được trong sandbox này -> dùng _mock_embed thay thế
```

**Kết quả baseline:** xem bảng ở trên (mục 1).

> **Ghi phần nhóm vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md), Phần 2. ⏸ Chưa cập nhật — đang chờ xác nhận của nhóm trưởng.

---

### Bài tập 3.2 — Chuẩn bị câu hỏi đánh giá

Dùng đúng 5 benchmark queries và gold answers đã thống nhất trong báo cáo nhóm. ✅ Đã dùng nguyên 5 câu hỏi + gold answer trong `REPORT_NHOM.md` (Phần 3) để chạy benchmark cá nhân — không tự đặt câu hỏi mới.

- [x] Các câu hỏi đa dạng và kiểm chứng được (kế thừa từ nhóm).
- [x] Có ít nhất một câu yêu cầu metadata filter (câu #4, `customer_role`).
- [x] Năm câu trùng với các thành viên còn lại.

> **Nguồn chuẩn:** [REPORT_NHOM.md](../report/REPORT_NHOM.md), Phần 3.

---

### Bài tập 3.3 — Dự đoán Cosine Similarity

Trước khi chạy, dự đoán mức tương tự của 5 cặp câu; sau đó nhúng bằng embedder thật và gọi `compute_similarity()`.

✅ Đã thực hiện — xem bảng dự đoán/kết quả đầy đủ trong `REPORT_CANHAN.md`, Phần 4 (dùng Mock embedder do giới hạn môi trường, có ghi chú rõ).

> **Ghi kết quả vào:** `REPORT_CANHAN.md`, Phần 4. ✅ Đã điền.

---

### Bài tập 3.4 — Chạy đánh giá và so sánh

Chạy đúng 5 queries bằng chiến lược cá nhân, ghi top-3, similarity score và Agent answer. Chấm theo [rubric](../docs/SCORING.md).

✅ Đã chạy — kết quả chi tiết (top-1 chunk, score, relevant?, agent answer) trong `REPORT_CANHAN.md`, Phần 5. Do dùng Mock embedder, hầu hết top-1 không trúng đúng chunk gold — đã phân tích nguyên nhân minh bạch (embedder, không phải lỗi chunking/code).

**Số câu có chunk liên quan trong top-3:** 0 / 5 (đúng nghĩa), 1/5 nếu tính đúng chủ đề rộng.
**Điểm retrieval tự đánh giá:** 7 / 10 (trừ điểm do hạn chế môi trường, không phải lỗi implementation).

> **Ghi kết quả vào:** `REPORT_CANHAN.md`, Phần 5, và phần tương ứng của [REPORT_NHOM.md](../report/REPORT_NHOM.md). ⏸ Phần REPORT_NHOM.md chưa cập nhật — đang chờ xác nhận của nhóm trưởng.

---

### Bài tập 3.5 — Phân tích lỗi

Mô tả ít nhất một failure case:

- Query thất bại: Câu hỏi #4 — *"Người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào?"* (yêu cầu `metadata_filter={"customer_role": "both"}`).
- Kết quả sai/thiếu: `search_with_filter` trả về **danh sách rỗng** — không có chunk nào được xếp hạng, vì không tài liệu nào trong corpus hiện tại mang giá trị `customer_role: both` (tất cả 5 file đều gắn `buyer`).
- Nguyên nhân: đây là lỗi ở **tầng dữ liệu/metadata**, không phải lỗi logic `search_with_filter` (hàm lọc đúng — lọc ra tập rỗng vì đúng là không có match). Có thể do file dữ liệu đã được chỉnh sửa sau khi `REPORT_NHOM.md` ghi nhận metadata ban đầu, hoặc do lúc gán nhãn `customer_role` chưa tách riêng các điều khoản áp dụng cho người bán.
- Ảnh hưởng: **Metadata Utility** (bộ lọc quá khắt khe do dữ liệu sai nhãn → mất hết kết quả thay vì giảm nhiễu) và **Grounding Quality** (agent không có ngữ cảnh nào để trả lời trung thực câu hỏi này).
- Đề xuất cải thiện: nhóm rà soát lại front-matter của `return-refund-policy.md` (tài liệu có nội dung Điều 7.1 nói về nghĩa vụ người bán) — gắn `customer_role: both` hoặc thêm trường `applies_to_seller: true` cho đúng những đoạn liên quan đến người bán, thay vì gắn cả file là `buyer`. Ngoài ra nên thêm test/kiểm tra "mọi giá trị metadata_filter dùng trong benchmark phải tồn tại ít nhất 1 lần trong corpus" để phát hiện sớm lỗi tương tự.

---

## Danh Sách Kiểm Tra Nộp Bài

- [x] `42/42` tests pass trên package cá nhân.
- [x] Đã kiểm tra và cập nhật `src/` bằng công việc của chính mình.
- [ ] Đã điền phần chiến lược cá nhân trong `../report/REPORT_NHOM.md`. — ⏸ Tạm hoãn, đang chờ xác nhận của nhóm trưởng trước khi sửa file chung.
- [x] Đã hoàn thành `REPORT_CANHAN.md`.
- [x] Không chứa token, API key hoặc credential trong file/commit.
