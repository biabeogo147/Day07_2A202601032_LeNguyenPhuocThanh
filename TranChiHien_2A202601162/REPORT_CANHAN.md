# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Chí Hiển
**Mã học viên:** 2A202601162
**Nhóm:** Những con vịt bầu
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm nộp chung trong `../report/REPORT_NHOM.md`. Chi tiết thang điểm: `../docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:*

**Ví dụ có độ tương tự CAO:**
- Câu A:
- Câu B:
- Tại sao tương đồng:

**Ví dụ có độ tương tự THẤP:**
- Câu A:
- Câu B:
- Tại sao khác:

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận khi triển khai các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: regex phát hiện câu và các edge case đã xử lý.*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán, thứ tự separator và base case.*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: cách lưu trữ, embedding và tính similarity.*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: thứ tự filter/search và cách xóa theo doc_id.*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt và cách inject context.*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
# Dán output của: pytest tests/ -v
```

**Số lượng bài test vượt qua:** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---|---|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy đúng 5 câu hỏi đánh giá của nhóm trên mã nguồn cá nhân trong `src`; xem `../report/REPORT_NHOM.md`.

| # | Câu hỏi | Top-1 Chunk truy xuất được | Điểm Score | Relevant? | Câu trả lời Agent |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk liên quan trong top-3?** __ / 5

**Điều hay nhất học được từ thành viên khác / nhóm khác:**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | / 5 |
| Hướng tiếp cận | / 10 |
| Hoàn thiện code | / 30 |
| Dự đoán độ tương tự | / 5 |
| Kết quả truy xuất | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
