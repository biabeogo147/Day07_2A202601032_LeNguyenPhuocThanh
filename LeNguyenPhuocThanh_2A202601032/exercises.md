# Ngày 7 — Bài tập
## Nền tảng Dữ liệu: Embedding & Vector Store | Bài tập thực hành

> **Trạng thái cập nhật ngày 03/08/2026:** Đã hoàn thành toàn bộ nội dung bài tập cá nhân, `42/42` tests, 5 dự đoán similarity và benchmark retrieval trên đúng 5 câu hỏi mới của nhóm. Chiến lược cá nhân là `PolicySectionChunker` + OpenAI `text-embedding-3-small`; kết quả retrieval là `4/5` câu có chunk liên quan trong top-3 và `7/10` điểm theo rubric.

---

## Phần 1 — Khởi động (Cá nhân)

### Bài tập 1.1 — Cosine Similarity (Độ tương tự Cosine) bằng ngôn ngữ đời thường

Không yêu cầu toán học — hãy giải thích về mặt khái niệm:

- Điều gì xảy ra khi hai đoạn văn bản có độ tương tự cosine cao?
- Đưa ra một ví dụ cụ thể về hai câu sẽ có độ tương tự CAO và hai câu sẽ có độ tương tự THẤP.
- Tại sao độ tương tự cosine lại được ưu tiên hơn khoảng cách Euclid (Euclidean distance) đối với text embeddings?

**Kết quả:**

- Cosine similarity cao nghĩa là hai vector embedding có hướng gần giống nhau, nên hai đoạn văn thường gần nhau về nội dung hoặc ý nghĩa.
- Cặp tương tự cao: “Khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày” và “Người mua được phép hoàn hàng trong bảy ngày kể từ khi nhận”. Cặp tương tự thấp: “Khách hàng có thể thanh toán bằng thẻ tín dụng” và “Rừng nhiệt đới có đa dạng sinh học cao”.
- Cosine tập trung vào góc giữa hai vector nên ít chịu ảnh hưởng của độ lớn vector. Euclidean distance phụ thuộc cả hướng và độ lớn, vì vậy có thể xem hai embedding cùng ý nghĩa nhưng khác norm là cách xa nhau.

> **Ghi kết quả vào:** REPORT_CANHAN.md — Phần 1 (Khởi động)
>
> ✅ **Đã hoàn thành:** Xem `REPORT_CANHAN.md`, Phần 1.

---

### Bài tập 1.2 — Bài toán tính toán Chunking

- Một tài liệu có độ dài 10,000 ký tự. Bạn tiến hành chia nhỏ (chunk) với `chunk_size=500` (kích thước chunk), `overlap=50` (độ chồng chéo). Bạn dự kiến sẽ có bao nhiêu chunks?
- Công thức: `số lượng chunk = làm_tròn_lên((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))`
- Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk sẽ thay đổi như thế nào? Tại sao bạn lại muốn tăng độ chồng chéo?

**Kết quả:**

- Với overlap 50: `ceil((10.000 - 50) / (500 - 50)) = ceil(22,111...) = 23 chunks`.
- Với overlap 100: `ceil((10.000 - 100) / (500 - 100)) = ceil(24,75) = 25 chunks`.
- Overlap lớn hơn giữ được ngữ cảnh gần ranh giới chunk tốt hơn, đổi lại làm tăng dữ liệu trùng lặp, số vector và chi phí xử lý.

> **Ghi kết quả vào:** REPORT_CANHAN.md — Phần 1 (Khởi động)
>
> ✅ **Đã hoàn thành:** Kết quả là 23 chunks khi overlap bằng 50 và 25 chunks khi overlap bằng 100; xem `REPORT_CANHAN.md`, Phần 1.

---

## Phần 2 — Lập trình cốt lõi (Cá nhân)

Hoàn thành tất cả các TODOs trong `src/chunking.py`, `src/store.py`, và `src/agent.py`. `Document` dataclass và `FixedSizeChunker` đã được triển khai sẵn làm ví dụ — hãy đọc kỹ để hiểu cấu trúc trước khi lập trình phần còn lại.

Chạy `pytest tests/` để kiểm tra tiến độ.

### Danh sách cần làm (Checklist)
- [x] `Document` dataclass — ĐÃ TRIỂN KHAI SẴN
- [x] `FixedSizeChunker` — ĐÃ TRIỂN KHAI SẴN
- [x] `SentenceChunker` — tách dựa trên ranh giới câu, nhóm lại thành các chunks
- [x] `RecursiveChunker` — thử nghiệm các dấu phân cách (separators) theo thứ tự, thực hiện đệ quy trên các đoạn có kích thước quá lớn
- [x] `compute_similarity` — công thức tính độ tương tự cosine kèm cơ chế bảo vệ chia cho 0
- [x] `ChunkingStrategyComparator` — gọi cả ba chiến lược, tính toán các chỉ số thống kê
- [x] `EmbeddingStore.__init__` — khởi tạo store (lưu trữ trong bộ nhớ hoặc ChromaDB)
- [x] `EmbeddingStore.add_documents` — nhúng (embed) và lưu trữ từng tài liệu
- [x] `EmbeddingStore.search` — nhúng truy vấn, xếp hạng theo tích vô hướng (dot product)
- [x] `EmbeddingStore.get_collection_size` — trả về số lượng
- [x] `EmbeddingStore.search_with_filter` — lọc theo siêu dữ liệu (metadata), sau đó tìm kiếm
- [x] `EmbeddingStore.delete_document` — xóa tất cả các chunks của một doc_id
- [x] `KnowledgeBaseAgent.answer` — truy xuất (retrieve) + tạo prompt + gọi LLM

**Kết quả triển khai:**

- `SentenceChunker` tách theo ranh giới `.`, `!`, `?`, giữ dấu câu và gom tối đa số câu cấu hình.
- `RecursiveChunker` ưu tiên đoạn văn → dòng → câu → từ → hard-split; mảnh nhỏ được ghép tới giới hạn.
- `EmbeddingStore` dùng ChromaDB Ephemeral với HNSW inner product, có mirror in-memory để fallback; hỗ trợ ID trùng, filter nhiều trường và xóa toàn bộ chunks theo `doc_id`.
- `KnowledgeBaseAgent` đánh số context, kèm nguồn và yêu cầu LLM chỉ trả lời dựa trên thông tin truy xuất.

> **Nộp code:** thư mục `src/`
> **Ghi lại hướng tiếp cận vào:** REPORT_CANHAN.md — Phần 2 (Hướng tiếp cận của tôi)
>
> ✅ **Đã hoàn thành:** `42/42` tests pass bằng Python 3.10.6 trong `.venv` Day04; xem `REPORT_CANHAN.md`, Phần 2–3.

---

## Phần 3 — So Sánh Chiến Lược Truy Xuất (Nhóm)

### Bài tập 3.0 — Chuẩn Bị Tài Liệu (Giờ đầu tiên)

Chủ đề Giai đoạn 2 **cố định theo lớp K4**: chính sách TMĐT / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán). Nhóm chuẩn bị bộ tài liệu trong phạm vi này:

> Đọc trước [Hướng dẫn crawl và format dữ liệu](../docs/DATA_COLLECTION.md). Tài liệu này quy định nguồn được dùng, quy trình crawl an toàn, cấu trúc thư mục, metadata và `sources.csv`.
>
> **Nạp dữ liệu (đã cung cấp sẵn):** dùng `build_knowledge_base(data_dir, embedding_fn, chunker=...)` trong `../ingest.py` — nó parse YAML front matter → chia chunk bằng chunker bạn chọn → gắn `doc_id` + metadata lên **từng** chunk → nạp vào `EmbeddingStore`. Bạn không phải tự viết lại pipeline này; chỉ cần tạo file `.md` đúng định dạng và chọn chunker.

**Bước 1 — Khoanh phạm vi cụ thể trong chủ đề cố định của lớp K4** (chính sách TMĐT / hỗ trợ khách hàng): ví dụ chính sách đổi trả, điều kiện người bán, quy định thanh toán, chính sách giao hàng, quyền riêng tư.

**Bước 2 — Thu thập 5-10 tài liệu.** Chỉ dùng nguồn công khai hoặc nguồn nhóm có quyền sử dụng; lưu dưới dạng `.txt` hoặc `.md` vào thư mục `data/`.

**Quy tắc dữ liệu bắt buộc:**
- Không đưa dữ liệu cá nhân, thông tin đăng nhập, hồ sơ nội bộ hoặc nội dung có quyền sử dụng không rõ ràng vào repo.
- Với mỗi tài liệu, ghi `source_url`, `retrieved_at` (ngày lấy) và `document_version` hoặc ngày hiệu lực nếu nguồn có nêu.
- Đưa ba trường trên vào siêu dữ liệu (metadata) khi nạp (ingest); chúng giúp kiểm tra độ mới và truy vết câu trả lời.

> **Mẹo chuyển PDF sang Markdown:**
> - `pip install marker-pdf` → `marker_single input.pdf output/` (chất lượng cao, giữ cấu trúc)
> - `pip install pymupdf4llm` → `pymupdf4llm.to_markdown("input.pdf")` (nhanh, đơn giản)
> - Hoặc sao chép-dán (copy-paste) nội dung từ PDF/web vào file `.txt`

Ghi vào bảng:

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `return-refund-general-rules.md` | https://help.shopee.vn/portal/4/article/188931 | 2026-08-03 / `not-stated` | 6.234 | `customer_role=buyer`, `category=returns-and-refunds`, `language=vi` |
| 2 | `return-refund-policy.md` | https://help.shopee.vn/portal/4/article/77251 | 2026-08-03 / `not-stated` | 19.609 | `customer_role=buyer`, `category=returns-and-refunds`, `language=vi` |
| 3 | `return-refund-request-guide.md` | https://help.shopee.vn/portal/4/article/79233 | 2026-08-03 / `not-stated` | 2.521 | `customer_role=buyer`, `category=returns-and-refunds`, `language=vi` |
| 4 | `return-shipping-methods.md` | https://help.shopee.vn/portal/4/article/189477 | 2026-08-03 / `not-stated` | 5.987 | `customer_role=buyer`, `category=returns-and-refunds`, `language=vi` |
| 5 | `shipping-faq.md` | https://help.shopee.vn/portal/4/article/79492 | 2026-08-03 / `not-stated` | 2.832 | `customer_role=buyer`, `category=shipping,vi,,`, `language=vi`; title/body không khớp |

**Bước 3 — Thiết kế cấu trúc metadata (metadata schema):** Mỗi tài liệu cần `source_url`, `retrieved_at`, `document_version` và ít nhất 2 trường hữu ích cho việc truy xuất (ví dụ: `category`, `customer_role`, `language`, `difficulty`).

**Kết quả:** Mỗi file có `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `customer_role`, `category`, `language`; khi ingest bổ sung `chunk_index` và `strategy`. Corpus thực tế hiện gán `customer_role=buyer` cho cả 5 file. `shipping-faq.md` có lỗi crawl: metadata nói về vận chuyển nhưng body là bài Gói Siêu Voucher và category bị sai định dạng.

> **Ghi kết quả vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md) — Phần 1 (Lựa chọn tài liệu)

---

### Bài tập 3.1 — Thiết Kế Chiến Lược Truy Xuất (Mỗi người thử riêng)

Mỗi thành viên **tự chọn chiến lược riêng** để thử nghiệm trên cùng bộ tài liệu của nhóm.

**Bước 1 — Đường cơ sở (Baseline):** Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu. Ghi lại kết quả.

> **Dùng embedder thật để so sánh có ý nghĩa:** đặt `EMBEDDING_PROVIDER=local` (xem README, mục *Tùy Chọn Mô Hình Nhúng*). Trình nhúng giả lập (mock) chỉ dùng cho unit test và cho điểm gần như ngẫu nhiên — **không** phản ánh chất lượng ngữ nghĩa tiếng Việt nên đừng dùng mock để kết luận chiến lược nào tốt hơn.

**Bước 2 — Chọn hoặc thiết kế chiến lược của bạn:**
- Dùng 1 trong 3 chiến lược có sẵn (built-in strategies) với tham số tối ưu, HOẶC
- Thiết kế chiến lược tùy chỉnh cho chủ đề của bạn (ví dụ: chia nhỏ theo cặp Câu hỏi-Đáp án, theo các phần (sections), theo tiêu đề (headers))
- Mỗi thành viên nên thử một chiến lược **khác nhau** để có cơ sở so sánh

```python
import re

from src.chunking import RecursiveChunker


class PolicySectionChunker:
    """Giữ heading/điều khoản cùng nội dung chính sách Shopee."""

    HEADING = re.compile(
        r"^(?:#{1,6}\s+.+|\d+(?:\.\d+)*(?:\.)?\s+\S.+)$"
    )

    def __init__(self, chunk_size: int = 800) -> None:
        self.recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        chunks, heading, body_lines = [], "Mở đầu", []

        def flush_section() -> None:
            body = "\n".join(body_lines).strip()
            for part in self.recursive.chunk(body):
                chunks.append(f"{heading}\n{part}".strip())
            body_lines.clear()

        for line in text.splitlines():
            line = line.strip()
            if line and self.HEADING.match(line):
                flush_section()
                heading = line
            elif line:
                body_lines.append(line)

        flush_section()
        return chunks
```

**Bước 3 — So sánh:** So sánh chiến lược tùy chỉnh/được tinh chỉnh (custom/tuned strategy) với đường cơ sở (baseline) trên cùng tài liệu.

**Kết quả baseline (`chunk_size=500`, Fixed Size overlap 50, Sentence 3 câu/chunk):**

| Tài liệu | Fixed Size | Sentence | Recursive |
|---|---:|---:|---:|
| `return-refund-policy.md` | 44 chunks / TB 494,5 | 43 / 453,3 | 62 / 313,7 |
| `return-refund-request-guide.md` | 6 / 461,8 | 8 / 311,6 | 6 / 416,3 |
| `return-shipping-methods.md` | 14 / 474,1 | 9 / 662,9 | 14 / 424,3 |

**Chiến lược đã chọn:** `PolicySectionChunker(chunk_size=800)` giữ heading/điều khoản đánh số với nội dung, sau đó dùng `RecursiveChunker` cho section quá dài. Trên toàn corpus, chiến lược tạo **54 chunks**, độ dài trung bình **574,6 ký tự**; retrieval dùng OpenAI `text-embedding-3-small` và ChromaDB inner product.

> **Ghi kết quả vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md) — Phần 2 (Thiết kế chiến lược)

---

### Bài tập 3.2 — Chuẩn Bị Câu Hỏi Đánh Giá (Benchmark Queries)

Mỗi nhóm viết **đúng 5 câu hỏi đánh giá** kèm theo **câu trả lời chuẩn (gold answers)**.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Shopee có hỗ trợ đổi hàng không? Nếu hàng có vấn đề thì người mua phải làm gì? | Shopee chưa hỗ trợ đổi hàng; có thể từ chối nhận khi đồng kiểm hoặc gửi yêu cầu Trả hàng/Hoàn tiền. | `return-refund-general-rules.md`, Điều 1.1 |
| 2 | Thời hạn gửi yêu cầu trả hàng/hoàn tiền trên Shopee là bao lâu? | Thực phẩm tươi sống/đông lạnh: 24 giờ; đơn tiêu chuẩn: 15 ngày; đơn người bán tự giao: tối đa 20 ngày. | `return-refund-general-rules.md`, Điều 1.2 |
| 3 | Người mua cần gửi yêu cầu trả hàng bằng cách nào trên ứng dụng Shopee? | Từ trang đơn hàng hoặc mục Trò Chuyện Với Shopee > Khiếu nại. | `return-refund-request-guide.md`, Điều 1 |
| 4 | Người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào? Filter `customer_role=both`. | Khi sản phẩm lỗi/hư hỏng/không đúng mô tả do người bán, hoặc trường hợp ngoại lệ theo quyết định Shopee. | `return-refund-policy.md`, Điều 7.1 |
| 5 | Có những phương thức gửi hàng hoàn trả nào và chi phí ra sao? | Đến lấy và gửi tại bưu cục: miễn phí; tự sắp xếp: trả trước rồi được hỗ trợ hoàn. Non-Mall nhận 25.000/40.000 Shopee Xu tùy địa chỉ. | `return-shipping-methods.md`, Điều 1.1 và 2 |

**Yêu cầu:**
- Câu hỏi phải đa dạng (không hỏi 5 câu có nội dung/cấu trúc giống hệt nhau)
- Câu trả lời chuẩn phải cụ thể và có thể kiểm chứng (verify) từ tài liệu
- Ít nhất 1 câu hỏi yêu cầu lọc bằng metadata (metadata filtering) để trả lời tốt

> **Ghi kết quả vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md) — Phần 3 (Câu hỏi đánh giá & Chất lượng truy xuất)

---

### Bài tập 3.3 — Dự Đoán Độ Tương Tự Cosine (Cá nhân)

Gọi hàm `compute_similarity()` trên 5 cặp câu. **Trước khi chạy**, hãy dự đoán xem cặp câu nào sẽ có độ tương tự cao nhất/thấp nhất. Ghi lại các dự đoán của bạn và kết quả thực tế. Suy ngẫm xem điều gì khiến bạn ngạc nhiên nhất.

| Cặp | Dự đoán | Điểm thực tế (`text-embedding-3-small`) | Kết quả |
|---|---|---:|---|
| 1 — hai câu về đổi trả 7 ngày | Cao | 0,533952 | Đúng |
| 2 — hai câu về mô tả trung thực | Cao | 0,650115 | Đúng |
| 3 — hai câu về giao hàng 3–5 ngày | Cao nhất | 0,667857 | Đúng |
| 4 — thẻ tín dụng và rừng nhiệt đới | Thấp nhất | 0,271100 | Đúng |
| 5 — bảo mật và đóng gói | Thấp | 0,318510 | Đúng |

Cặp 1 bất ngờ nhất vì cùng nói về đổi trả trong bảy ngày nhưng score thấp hơn các cặp diễn đạt lại về người bán và giao hàng. Điều này cho thấy embedding mã hóa toàn bộ ngữ cảnh, không chỉ đếm từ khóa; nên đánh giá tương quan giữa các cặp thay vì dùng một ngưỡng tuyệt đối.

> **Ghi kết quả vào:** REPORT_CANHAN.md — Phần 4 (Dự đoán độ tương tự)
>
> ✅ **Đã hoàn thành:** Đã dự đoán trước và đo 5 cặp câu bằng OpenAI `text-embedding-3-small`; xem `REPORT_CANHAN.md`, Phần 4.

---

### Bài tập 3.4 — Chạy Đánh Giá & So Sánh Trong Nhóm

**Bước 1:** Mỗi thành viên chạy 5 câu hỏi đánh giá với chiến lược riêng. Ghi lại kết quả top-3 cho mỗi câu hỏi.

**Bước 2:** So sánh kết quả trong nhóm:
- Chiến lược nào cho việc truy xuất tốt nhất? Tại sao?
- Có câu hỏi nào mà chiến lược A tốt hơn B nhưng lại ngược lại ở câu hỏi khác không?
- Lọc bằng metadata (Metadata filtering) có giúp ích không?

**Bước 3:** Thảo luận và rút ra bài học — chuẩn bị cho phần demo (thuyết trình) với các nhóm khác.

**Kết quả cá nhân — `PolicySectionChunker` + `text-embedding-3-small`:**

| # | Top-1 retrieval | Score | Đánh giá Agent |
|---|---|---:|---|
| 1 | `return-refund-general-rules/1` — nguyên tắc không đổi hàng | 0,7574 | Đúng đầy đủ — 2/2 |
| 2 | `return-refund-general-rules/2` — các mốc 24 giờ/15 ngày/20 ngày | 0,7762 | Đúng đầy đủ — 2/2 |
| 3 | `return-refund-request-guide/2` — biểu mẫu, bằng chứng và gửi yêu cầu | 0,7712 | Đúng đầy đủ; top-2 chứa cách 1 — 2/2 |
| 4 | Không có kết quả khi filter `customer_role=both` | — | Agent nói không đủ ngữ cảnh — 0/2 |
| 5 | `return-shipping-methods/0`; nội dung chi tiết nằm ở top-2/top-3 | 0,6849 | Đúng 3 phương thức nhưng thiếu 25.000/40.000 Xu — 1/2 |

**Tổng hợp:** `4/5` câu có chunk liên quan trong top-3; Agent đạt **7/10**. Sentence/Recursive có lợi thế với điều khoản ngắn, còn Policy Section giữ được tiêu đề để dễ truy nguồn. Metadata filter chỉ hữu ích khi giá trị trong corpus được gán đúng; Q4 chứng minh filter chính xác có thể trả rỗng nếu schema và dữ liệu không thống nhất.

> **Ghi kết quả vào:** REPORT_CANHAN.md — Phần 5 (Kết quả truy xuất của tôi) + [REPORT_NHOM.md](../report/REPORT_NHOM.md) — Phần 3 (Chất lượng truy xuất của nhóm)
> **Gợi ý đánh giá:** xem danh sách kiểm tra ngắn trong [README.md](../README.md) mục **Cách Tự Đánh Giá Kết Quả Retrieval** hoặc chi tiết hơn trong [docs/EVALUATION.md](../docs/EVALUATION.md).

---

### Bài tập 3.5 — Phân Tích Lỗi (Failure Analysis)

Tìm ít nhất **1 trường hợp lỗi (failure case)** trong quá trình so sánh. Mô tả:
- Câu hỏi nào mà quá trình truy xuất gặp thất bại?
- Tại sao? (do chunk quá nhỏ/quá lớn, thiếu metadata, câu hỏi mơ hồ, v.v.)
- Đề xuất cải thiện?

**Failure case:** Q4 yêu cầu `customer_role=both`, nhưng YAML front matter thực tế của `return-refund-policy.md` vẫn là `customer_role=buyer`. `search_with_filter()` vì thế trả danh sách rỗng dù Điều 7.1 có nội dung cần tìm; Agent đúng khi nói không đủ ngữ cảnh.

- **Nguyên nhân:** Benchmark/report nhóm và metadata corpus không thống nhất, không phải lỗi similarity search.
- **Ảnh hưởng:** Recall của Q4 bằng 0 sau pre-filter; semantic similarity không có cơ hội xếp hạng đúng chunk.
- **Cải thiện:** Nhóm cần thống nhất enum cho `customer_role`, kiểm tra metadata trước ingest và chỉ đổi policy sang `both` khi nội dung thực sự áp dụng cho cả buyer/seller. Nên thêm test đếm số record theo từng filter trước khi chạy benchmark.

> **Ghi kết quả vào:** [REPORT_NHOM.md](../report/REPORT_NHOM.md) — Phần 4 (Demo & Bài học nhóm)
> **Gợi ý:** phân tích lỗi nên tham chiếu từ các góc nhìn như độ chính xác (precision), tính mạch lạc của chunk (chunk coherence), tính hữu dụng của metadata, và chất lượng thông tin nền (grounding quality).

---

## Danh Sách Kiểm Tra Nộp Bài (Submission Checklist)

- [x] Vượt qua tất cả các bài kiểm thử (tests): `pytest tests/ -v` — **42/42 tests pass**
- [x] Cập nhật thư mục `src/` (cá nhân)
- [x] Hoàn thành phần chiến lược cá nhân trong báo cáo nhóm (`../report/REPORT_NHOM.md`)
- [x] Hoàn thành toàn bộ câu trả lời trong `exercises.md`, gồm benchmark retrieval `4/5` và `7/10`
- [x] Hoàn thành báo cáo cá nhân (`REPORT_CANHAN.md`) — **retrieval 7/10, tổng cá nhân 57/60**
