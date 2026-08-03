# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Nguyễn Phước Thành
**Nhóm:** Những con vịt bầu
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding hướng gần giống nhau, nên hai đoạn văn thường có nội dung hoặc ý nghĩa gần nhau. Giá trị càng gần 1 thì mức tương đồng theo hướng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày.
- Câu B: Người mua được phép hoàn hàng trong bảy ngày kể từ khi nhận.
- Tại sao tương đồng: Hai câu cùng diễn đạt quyền đổi trả của người mua trong thời hạn bảy ngày, dù dùng từ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Khách hàng có thể thanh toán bằng thẻ tín dụng.
- Câu B: Rừng nhiệt đới có đa dạng sinh học cao.
- Tại sao khác: Một câu nói về phương thức thanh toán, câu còn lại nói về hệ sinh thái nên gần như không có chủ đề chung.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào góc giữa hai vector, tức hướng biểu diễn ngữ nghĩa, và ít bị ảnh hưởng bởi độ lớn vector. Khoảng cách Euclid phụ thuộc cả hướng lẫn độ lớn nên hai embedding có cùng ý nghĩa nhưng khác norm vẫn có thể bị xem là cách xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.111...)`.
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100: `ceil((10,000 - 100) / (500 - 100)) = ceil(9,900 / 400) = 25`, nên số chunk tăng từ 23 lên **25**. Overlap lớn hơn giúp giữ lại ngữ cảnh nằm gần ranh giới chunk, đổi lại cần lưu trữ và xử lý nhiều dữ liệu trùng lặp hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])(?:[ \t]+|\n+)` để tách tại khoảng trắng hoặc xuống dòng sau dấu kết câu, nhờ vậy dấu câu vẫn thuộc về câu trước. Các phần rỗng và văn bản chỉ có khoảng trắng được loại bỏ; số câu mỗi chunk được chặn tối thiểu là 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử separator theo thứ tự đoạn văn, dòng, câu, từ rồi ký tự; các mảnh nhỏ được ghép tuần tự cho đến giới hạn `chunk_size`, còn mảnh quá lớn được xử lý bằng separator kế tiếp. Base case là văn bản đã đủ ngắn; nếu hết separator thì hard-split theo số ký tự để tránh đệ quy vô hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được nhúng, chuẩn hóa thành record có ID vật lý duy nhất, nội dung, metadata và embedding rồi lưu vào ChromaDB Ephemeral với HNSW inner-product; một bản mirror in-memory được giữ để fallback. `search` nhúng truy vấn, lấy kết quả theo inner product và chuyển Chroma distance thành `score = 1 - distance`; nhánh fallback tính dot product trực tiếp.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Metadata được lọc trước khi similarity search; nhiều điều kiện được kết hợp bằng `$and` và so khớp chính xác. `delete_document` tìm mọi record có `metadata["doc_id"]` tương ứng, xóa toàn bộ ID vật lý khỏi Chroma và bản mirror, sau đó trả `True` nếu thực sự có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent truy xuất top-k chunk, đánh số từng ngữ cảnh và thêm nguồn từ `source_url` hoặc `source` nếu có. Prompt gồm chỉ dẫn chỉ được dựa trên ngữ cảnh, phần `NGỮ CẢNH`, `CÂU HỎI` và `TRẢ LỜI`; khi không có chunk, prompt yêu cầu LLM nói rõ không đủ thông tin thay vì suy đoán.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
D:\AI-DS-Study\Lab\Day04_2A202601032_LeNguyenPhuocThanh\.venv\Scripts\python.exe -m pytest tests/ -v

============================= test session starts =============================
platform win32 -- Python 3.10.6, pytest-9.1.1
rootdir: D:\AI-DS-Study\Lab\Day07_2A202601032_LeNguyenPhuocThanh
collected 42 items

tests/test_solution.py ..........................................        [100%]

============================= 42 passed in 1.18s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày. | Người mua được phép hoàn hàng trong bảy ngày kể từ khi nhận. | Cao | 0.533952 | Có |
| 2 | Người bán phải cung cấp thông tin sản phẩm chính xác. | Nhà bán hàng cần mô tả sản phẩm trung thực và đầy đủ. | Cao | 0.650115 | Có |
| 3 | Đơn hàng sẽ được giao trong 3 đến 5 ngày làm việc. | Thời gian vận chuyển dự kiến là ba đến năm ngày làm việc. | Cao nhất | 0.667857 | Có |
| 4 | Khách hàng có thể thanh toán bằng thẻ tín dụng. | Rừng nhiệt đới có đa dạng sinh học cao. | Thấp nhất | 0.271100 | Có |
| 5 | Chính sách bảo mật giải thích cách dữ liệu cá nhân được sử dụng. | Người bán phải đóng gói hàng hóa cẩn thận trước khi giao. | Thấp | 0.318510 | Có |

> **Cách đo:** Nhúng từng câu bằng OpenAI `text-embedding-3-small`, sau đó gọi `compute_similarity()` trên từng cặp vector. Dự đoán được ghi trước khi chạy mô hình.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 làm tôi bất ngờ nhất: hai câu đều nói về đổi trả trong bảy ngày nhưng điểm `0.533952` thấp hơn rõ rệt so với hai cặp diễn đạt lại về người bán và giao hàng. Điều này cho thấy embedding không chỉ đếm từ khóa chung mà mã hóa toàn bộ ngữ cảnh và cách diễn đạt; vì vậy nên đánh giá điểm theo tương quan giữa các cặp thay vì dùng một ngưỡng tuyệt đối cứng nhắc.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Shopee có hỗ trợ đổi hàng không? Nếu hàng có vấn đề thì người mua phải làm gì? | `return-refund-general-rules/1`: Điều 1.1 nêu Shopee chưa hỗ trợ đổi hàng và hai cách xử lý khi hàng có vấn đề. | 0,7574 | Có, top-1 | Trả đúng: từ chối nhận khi đồng kiểm hoặc gửi yêu cầu Trả hàng/Hoàn tiền — **2/2**. |
| 2 | Thời hạn gửi yêu cầu trả hàng/hoàn tiền trên Shopee là bao lâu? | `return-refund-general-rules/2`: các mốc 24 giờ, 15 ngày và 20 ngày. | 0,7762 | Có, top-1 | Trả đúng đầy đủ thời hạn cho thực phẩm, đơn tiêu chuẩn và đơn người bán tự vận chuyển — **2/2**. |
| 3 | Người mua cần gửi yêu cầu trả hàng bằng cách nào trên ứng dụng Shopee? | `return-refund-request-guide/2`: biểu mẫu, bằng chứng và thao tác gửi; chunk `/1` ở top-2 chứa phần bắt đầu của cách 1. | 0,7712 | Có, top-1 và top-2 | Trả đúng hai cách, các bước, mô tả và ảnh/video cần cung cấp — **2/2**. |
| 4 | Người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào? Filter `customer_role=both`. | Không có kết quả: corpus thực tế không có record mang `customer_role=both`. | — | Không | Agent nói rõ không tìm thấy đủ ngữ cảnh, không suy đoán — **0/2**. |
| 5 | Có những phương thức gửi hàng hoàn trả nào và chi phí ra sao? | `return-shipping-methods/0`: heading đúng chủ đề; `/1` và `/7` ở top-2/top-3 chứa ba phương thức và chính sách phí. | 0,6849 | Có trong top-3 | Trả đúng ba phương thức và cơ chế trả trước/hoàn sau nhưng thiếu mức 25.000/40.000 Shopee Xu — **1/2**. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **4 / 5**

**Thiết lập chạy:** `PolicySectionChunker(chunk_size=800)` + OpenAI `text-embedding-3-small` + ChromaDB inner product; Agent dùng `gpt-4.1-mini`, chỉ trả lời từ top-3 context. Tổng điểm theo rubric: **7/10**.

**Failure case đáng chú ý:** Q4 trong benchmark nhóm yêu cầu filter `customer_role=both`, nhưng YAML front matter thực tế của `return-refund-policy.md` vẫn là `customer_role=buyer`. Vì pre-filter không tìm được candidate, recall bằng 0 dù Điều 7.1 có nội dung liên quan. Cần thống nhất enum metadata và kiểm tra số record theo từng filter trước khi so sánh chiến lược.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Kết quả RecursiveChunker của thành viên khác cho thấy chunk nhỏ theo ranh giới đoạn có thể đưa một điều khoản ngắn lên top-1 rất tốt, trong khi Policy Section giúp mỗi chunk giữ được nhãn điều khoản và dễ truy nguồn hơn. Quan trọng hơn, mọi thành viên phải chạy trên cùng một snapshot corpus và schema: sai khác `buyer`/`both` có thể làm thay đổi kết quả nhiều hơn cả lựa chọn chunker hoặc embedding model.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
