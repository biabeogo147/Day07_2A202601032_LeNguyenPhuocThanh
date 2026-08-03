# Ngày 7 — Bài tập
## Nền tảng Dữ liệu: Embedding & Vector Store | Bài tập thực hành

> Đây là template cá nhân. Kết quả phải do Trần Chí Hiển tự chạy và đối chiếu trước khi điền.

---

## Phần 1 — Khởi động (Cá nhân)

### Bài tập 1.1 — Cosine Similarity bằng ngôn ngữ đời thường

- Điều gì xảy ra khi hai đoạn văn bản có cosine similarity cao?
- Đưa ra một cặp câu có similarity cao và một cặp có similarity thấp.
- Tại sao cosine similarity thường được ưu tiên hơn Euclidean distance cho text embeddings?

> **Ghi kết quả vào:** `REPORT_CANHAN.md` — Phần 1.

---

### Bài tập 1.2 — Bài toán tính toán Chunking

- Tài liệu dài 10.000 ký tự, `chunk_size=500`, `overlap=50`: dự kiến bao nhiêu chunks?
- Công thức: `ceil((document_length - overlap) / (chunk_size - overlap))`.
- Nếu overlap tăng lên 100, số chunks thay đổi thế nào? Tại sao muốn tăng overlap?

> **Ghi kết quả vào:** `REPORT_CANHAN.md` — Phần 1.

---

## Phần 2 — Lập trình cốt lõi (Cá nhân)

Hoàn thành các TODO trong `src/chunking.py`, `src/store.py`, `src/agent.py` và chạy `pytest ../tests/ -v`.

### Danh sách cần làm (Checklist)

- [ ] Đọc và hiểu `Document` dataclass.
- [ ] Đọc và hiểu `FixedSizeChunker`.
- [ ] Kiểm tra/triển khai `SentenceChunker`.
- [ ] Kiểm tra/triển khai `RecursiveChunker`.
- [ ] Kiểm tra/triển khai `compute_similarity`.
- [ ] Kiểm tra/triển khai `ChunkingStrategyComparator`.
- [ ] Kiểm tra/triển khai `EmbeddingStore.__init__`.
- [ ] Kiểm tra/triển khai `EmbeddingStore.add_documents`.
- [ ] Kiểm tra/triển khai `EmbeddingStore.search`.
- [ ] Kiểm tra/triển khai `EmbeddingStore.get_collection_size`.
- [ ] Kiểm tra/triển khai `EmbeddingStore.search_with_filter`.
- [ ] Kiểm tra/triển khai `EmbeddingStore.delete_document`.
- [ ] Kiểm tra/triển khai `KnowledgeBaseAgent.answer`.
- [ ] Chạy đủ 42 tests bằng môi trường được chỉ định.

> **Nộp code:** thư mục `src/`. Ghi cách tiếp cận vào `REPORT_CANHAN.md`, Phần 2–3.

---

## Phần 3 — So Sánh Chiến Lược Truy Xuất

### Bài tập 3.0 — Chuẩn bị tài liệu

Chủ đề K4: chính sách TMĐT/hỗ trợ khách hàng. Đọc [hướng dẫn dữ liệu](../docs/DATA_COLLECTION.md) và dùng corpus chung tại `../data/shopee_customer_support`.

| # | Tên tài liệu | Source URL | Ngày lấy / Phiên bản | Số ký tự | Metadata |
|---|---|---|---|---:|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Metadata schema cần kiểm tra:** `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `customer_role`, `category`, `language`; khi ingest bổ sung `chunk_index`.

> **Ghi phần nhóm vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md), Phần 1.

---

### Bài tập 3.1 — Thiết kế chiến lược truy xuất

1. Chạy `ChunkingStrategyComparator().compare()` trên 2–3 tài liệu.
2. Ghi số chunks và độ dài trung bình của Fixed Size, Sentence và Recursive.
3. Chọn hoặc tự thiết kế một chiến lược riêng; không mặc nhiên xem baseline sao chép là kết quả cá nhân.
4. Dùng embedder thật, không dùng mock để kết luận chất lượng semantic retrieval.

```python
class CustomChunker:
    """Hiển tự mô tả chiến lược và lý do lựa chọn."""

    def chunk(self, text: str) -> list[str]:
        raise NotImplementedError
```

**Kết quả baseline:**

| Tài liệu | Chiến lược | Số chunks | Độ dài TB | Nhận xét |
|---|---|---:|---:|---|
| | Fixed Size | | | |
| | Sentence | | | |
| | Recursive | | | |

> **Ghi phần nhóm vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md), Phần 2.

---

### Bài tập 3.2 — Chuẩn bị câu hỏi đánh giá

Dùng đúng 5 benchmark queries và gold answers đã thống nhất trong báo cáo nhóm.

| # | Query | Gold Answer | Chunk chứa thông tin |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

- [ ] Các câu hỏi đa dạng và kiểm chứng được.
- [ ] Có ít nhất một câu yêu cầu metadata filter.
- [ ] Năm câu trùng với các thành viên còn lại.

> **Nguồn chuẩn:** [REPORT_NHOM.md](../report/REPORT_NHOM.md), Phần 3.

---

### Bài tập 3.3 — Dự đoán Cosine Similarity

Trước khi chạy, dự đoán mức tương tự của 5 cặp câu; sau đó nhúng bằng embedder thật và gọi `compute_similarity()`.

| Cặp | Câu A | Câu B | Dự đoán trước | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

> **Ghi kết quả vào:** `REPORT_CANHAN.md`, Phần 4.

---

### Bài tập 3.4 — Chạy đánh giá và so sánh

Chạy đúng 5 queries bằng chiến lược cá nhân, ghi top-3, similarity score và Agent answer. Chấm theo [rubric](../docs/SCORING.md): 2 điểm nếu top-3 có chunk liên quan và Agent đúng; 1 điểm nếu thiếu; 0 điểm nếu không retrieve được.

| # | Top-1 Chunk | Similarity Score | Relevant trong top-3? | Agent / điểm rubric |
|---|---|---:|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Số câu có chunk liên quan trong top-3:** __ / 5
**Điểm retrieval tự đánh giá:** __ / 10

> **Ghi kết quả vào:** `REPORT_CANHAN.md`, Phần 5, và phần tương ứng của [REPORT_NHOM.md](../report/REPORT_NHOM.md).

---

### Bài tập 3.5 — Phân tích lỗi

Mô tả ít nhất một failure case:

- Query thất bại:
- Kết quả sai/thiếu:
- Nguyên nhân:
- Ảnh hưởng đến precision, recall hoặc grounding:
- Đề xuất cải thiện:

---

## Danh Sách Kiểm Tra Nộp Bài

- [ ] `42/42` tests pass trên package cá nhân.
- [ ] Đã kiểm tra và cập nhật `src/` bằng công việc của chính mình.
- [ ] Đã điền phần chiến lược cá nhân trong `../report/REPORT_NHOM.md`.
- [ ] Đã hoàn thành `REPORT_CANHAN.md`.
- [ ] Không chứa token, API key hoặc credential trong file/commit.
