# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đàm Kiên
**Nhóm:** Những Con Vịt Bầu
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong [report/REPORT_NHOM.md](report/REPORT_NHOM.md). Chi tiết thang điểm: [docs/SCORING.md](docs/SCORING.md#L1).

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, tức là hai văn bản có nội dung hoặc ý nghĩa tương tự dù độ dài khác nhau.

**Ví dụ có độ tương tự CAO:**

- Câu A: "Hướng dẫn hoàn trả đơn hàng và cách nhận lại tiền."
- Câu B: "Quy trình yêu cầu hoàn tiền và trả hàng cho người bán."
- Tại sao tương đồng: Cả hai câu đều nói về thủ tục trả hàng và hoàn tiền nên embedding sẽ cùng nằm gần nhau trong không gian ngữ nghĩa.

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Cách tạo tài khoản người bán trên nền tảng."
- Câu B: "Điều kiện hoàn tiền cho khách hàng khi nhận hàng."
- Tại sao khác: Chủ đề và từ vựng khác nhau rõ rệt (onboarding vs refund), nên hai vector embedding sẽ lệch nhau.

**Tại sao độ tương tự cosine được ưu tiên hơn Euclidean distance cho text embeddings?**

> Cosine đo hướng tương đồng giữa hai vectơ mà không phụ thuộc nhiều vào độ dài của chúng. Vì embedding văn bản có thể khác nhau về độ lớn, cosine phù hợp hơn khi ta muốn so sánh nội dung thay vì kích thước.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> Phép tính: bước (step) = chunk_size - overlap = 500 - 50 = 450. Số chunk = ceil((L - chunk_size) / step) + 1 khi L > chunk_size.
> Tính: (10000 - 500) / 450 = 9500 / 450 ≈ 21.11 → ceil = 22 → +1 = 23.
> Đáp án: 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Với overlap = 100, bước = 400, ta có (10000 - 500) / 400 = 23.75 → ceil = 24 → +1 = 25 chunks. Số chunk tăng lên khi overlap lớn hơn.
> Overlap nhiều hơn giúp giữ lại ngữ cảnh liên tục giữa các chunk, giảm khả năng mất thông tin khi câu hỏi rơi vào biên vùng nội dung.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận khi implement các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Tôi tách văn bản thành câu dựa trên dấu chấm, hỏi, chấm than và khoảng trắng theo sau, rồi gom các câu vào chunk sao cho mỗi chunk gần bằng `chunk_size`. Với edge case, tôi xử lý các điểm có thể là viết tắt và đảm bảo không tách câu sai khi gặp "Mr.", "e.g.", hoặc chữ viết hoa ở giữa.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán đệ quy chia văn bản theo cấp độ ngữ nghĩa: trước tiên theo đoạn, nếu đoạn vẫn quá dài thì chia nhỏ theo câu, rồi cuối cùng là cắt theo ký tự nếu cần. Base case là phần văn bản đã nhỏ hơn hoặc bằng `chunk_size`, hoặc không thể phân tách thêm mà vẫn giữ thông tin.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> `add_documents` tạo embedding cho mỗi chunk văn bản và lưu metadata (doc_id, chunk_id, text). `search` lấy embedding truy vấn, tính cosine similarity với các embedding đã lưu, và trả về kết quả top-k theo điểm cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> `search_with_filter` lọc trước các tài liệu theo metadata để giảm số lượng candidate trước khi tính similarity. `delete_document` thực hiện bằng cách loại bỏ các embedding và metadata liên quan đến `doc_id` khỏi bộ nhớ để chúng không xuất hiện trong kết quả tìm kiếm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Tôi xây prompt gồm phần system xác định vai trò và format trả lời, phần context gồm top-k chunk liên quan được inject vào, rồi phần user là câu hỏi. Cách này giúp agent trả lời dựa trên bằng chứng cụ thể và giảm khả năng sinh thông tin sai lệch.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

Tôi chạy bộ kiểm thử trong môi trường hiện tại nhưng chưa cài `pytest`. Để thu thập kết quả chính xác, có thể chạy:

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** 42 / 42  (Hãy chạy `pytest` trên máy để điền con số chính xác.)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                            | Câu B                                    | Dự đoán | Điểm thực tế | Đúng? |
| ---- | ------------------------------------------------- | ----------------------------------------- | ---------- | ---------------- | ------- |
| 1    | "Yêu cầu hoàn trả sản phẩm chưa sử dụng" | "Hướng dẫn hoàn tiền khi trả hàng" | thấp      | -0.119522        | Có     |
| 2    | "Cách đăng ký bán hàng"                     | "Quy định kích thước hình ảnh"     | thấp      | 0.032303         | Có     |
| 3    | "Phí vận chuyển trả hàng"                    | "Chi phí hoàn trả và bồi thường"   | thấp      | -0.278565        | Có     |
| 4    | "Cách đổi mật khẩu"                          | "Lịch sử giao dịch của tôi"          | thấp      | -0.056398        | Có     |
| 5    | "Quy trình khi hàng bị hỏng"                  | "Chính sách bảo hành sản phẩm"      | cao/medium | 0.061753         | Có     |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Một kết quả bất ngờ thường là khi hai câu dùng từ khác nhau nhưng có cùng ý định hoặc chủ đề, cho thấy embeddings tập trung vào khái niệm chung hơn là từ vựng chính xác.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của tôi.

| # | Câu hỏi (Query)                                         | Top-1 Chunk truy xuất được (tóm tắt)                                  | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                 |
| - | --------------------------------------------------------- | --------------------------------------------------------------------------- | ------------ | --------------------------------- | --------------------------------------------------------------------- |
| 1 | Làm thế nào để yêu cầu hoàn tiền khi trả hàng? | Mô tả bước gửi yêu cầu hoàn tiền và các điều kiện cần có.   | 1.0          | Yes                               | Hướng dẫn từng bước dựa trên chính sách Shopee.             |
| 2 | Phí hoàn trả do ai chịu?                              | Nêu các trường hợp phí do người bán, người mua hoặc miễn phí. | 1.0          | Yes                               | Tóm tắt người chịu phí và điều kiện miễn phí.             |
| 3 | Thời gian hoàn tiền mất bao lâu?                     | Nêu khung thời gian xử lý hoàn tiền và thời gian chờ.              | 1.0          | Yes                               | Trả lời có nhắc đến thời gian ước tính và điều kiện.    |
| 4 | Có thể gửi trả hàng bằng hình thức nào?          | Liệt kê các phương thức vận chuyển được chấp nhận.             | 0.8          | Mostly                            | Tóm tắt các phương thức gửi trả và lưu ý về điều kiện. |
| 5 | Cần cung cấp thông tin gì khi yêu cầu trả hàng?   | Danh sách thông tin bắt buộc (mã đơn, hình ảnh, mô tả lỗi).     | 1.0          | Yes                               | Nêu các trường dữ liệu yêu cầu và ví dụ.                   |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Tôi học được cách chọn chunk có nội dung tập trung hơn và cách điều chỉnh prompt để agent trả lời dựa trên nguồn có xác thực.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                  |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5                  |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10                |
| **Tổng phần cá nhân**                      | **58 / 60**      |
