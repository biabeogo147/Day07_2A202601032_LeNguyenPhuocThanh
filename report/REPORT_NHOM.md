# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Những con vịt bầu  
**Thành viên:**
1. Nguyễn Đàm Kiên (Mã HV: 2A202602015)
2. Lê Nguyễn Phước Thành (Mã HV: 2A202601032)
3. Nguyễn Văn Nam (Mã HV: 2A202601973)
4. Lê Kim Tính (Mã HV: 2A202601560)
5. Trần Chí Hiển (Mã HV: 2A202601162)  
**Khóa:** K4  
**Ngày:** 03/08/2026  

> **Nộp 1 bản / nhóm.** Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng.

**Phạm vi cụ thể nhóm tập trung:**
> Chính sách trả hàng/hoàn tiền, hướng dẫn gửi yêu cầu đổi trả, phương thức vận chuyển hoàn trả và chi phí trên sàn Shopee Việt Nam.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|---|---|---|
| 1 | `return-refund-general-rules.md` | https://help.shopee.vn/portal/4/article/188931 | 2026-08-03 / not-stated | 6,234 | `customer_role: buyer`, `category: returns-and-refunds`, `language: vi` |
| 2 | `return-refund-policy.md` | https://help.shopee.vn/portal/4/article/77251 | 2026-08-03 / not-stated | 19,609 | `customer_role: both`, `category: returns-and-refunds`, `language: vi` |
| 3 | `return-refund-request-guide.md` | https://help.shopee.vn/portal/4/article/79233 | 2026-08-03 / not-stated | 2,521 | `customer_role: buyer`, `category: returns-and-refunds`, `language: vi` |
| 4 | `return-shipping-methods.md` | https://help.shopee.vn/portal/4/article/189477 | 2026-08-03 / not-stated | 5,987 | `customer_role: buyer`, `category: returns-and-refunds`, `language: vi` |
| 5 | `shipping-faq.md` | https://help.shopee.vn/portal/4/article/79492 | 2026-08-03 / not-stated | 2,832 | `customer_role: buyer`, `category: shipping`, `language: vi` |

**Data governance checklist:**
- [x] Chỉ chứa nguồn công khai (trang trợ giúp Shopee).
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ | Tại sao hữu ích? |
|---|---|---|---|
| `customer_role` | string | `buyer`, `both` | Lọc chính xác đối tượng áp dụng (buyer vs seller) |
| `category` | string | `returns-and-refunds`, `shipping` | Phân biệt loại chính sách |
| `document_version` | string | `not-stated` | Đảm bảo truy xuất đúng phiên bản chính sách |
| `source_url` | string | `https://help.shopee.vn/...` | Cung cấp nguồn tham chiếu minh bạch |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

| Tài liệu | Chiến lược | Số lượng Chunk | Độ dài TB | Giữ ngữ cảnh? |
|---|---|---|---|---|
| `return-refund-general-rules` (6234 chars) | FixedSizeChunker | 35 | 198 | Trung bình (cắt ngang câu) |
| | SentenceChunker | 10 | 617 | Tốt (giữ câu hoàn chỉnh) |
| | RecursiveChunker | 42 | 147 | Tốt (tôn trọng cấu trúc phân cấp) |
| `return-refund-request-guide` (2521 chars) | FixedSizeChunker | 14 | 199 | Trung bình |
| | SentenceChunker | 8 | 310 | Tốt |
| | RecursiveChunker | 17 | 146 | Tốt |
| `return-shipping-methods` (5987 chars) | FixedSizeChunker | 34 | 196 | Trung bình |
| | SentenceChunker | 10 | 596 | Tốt |
| | RecursiveChunker | 42 | 141 | Tốt |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Văn Nam (2A202601973)**
- **Loại chiến lược:** `RecursiveChunker` (chunk_size=500) kết hợp `Gemini Embedding 2`
- **Mô tả & lý do:** Chính sách Shopee có cấu trúc phân cấp theo điều/khoản/mục. RecursiveChunker tôn trọng cấu trúc này bằng cách ưu tiên tách tại ranh giới đoạn văn (`\n\n`) trước, rồi mới xuống dòng (`\n`), rồi câu (`. `). Với chunk_size=500, mỗi chunk giữ trọn 1-2 điều khoản liên quan, tránh tình trạng cắt ngang quy định quan trọng.
- **Code snippet:**
```python
from src.chunking import RecursiveChunker
from src.embeddings import GeminiEmbedder

chunker = RecursiveChunker(chunk_size=500)
embedder = GeminiEmbedder(model_name="models/gemini-embedding-2")
```

**Thành viên 2 — Lê Nguyễn Phước Thành (2A202601032)**
- **Loại chiến lược:** `PolicySectionChunker` (section-aware, `chunk_size=800`) kết hợp OpenAI `text-embedding-3-small`
- **Mô tả & lý do:** Chính sách Shopee được tổ chức theo các heading và điều khoản đánh số như `1.2`, `2.2`, `5.`. Chiến lược giữ tiêu đề đi cùng nội dung, sau đó dùng `RecursiveChunker` khi section quá dài để hạn chế cắt rời điều kiện khỏi chủ đề; trên toàn bộ 5 tài liệu, chiến lược tạo 54 chunks với độ dài trung bình 574,6 ký tự.
- **Code snippet:**
```python
import re

from LeNguyenPhuocThanh_2A202601032.src.chunking import RecursiveChunker


class PolicySectionChunker:
    HEADING = re.compile(
        r"^(?:#{1,6}\s+.+|\d+(?:\.\d+)*(?:\.)?\s+\S.+)$"
    )

    def __init__(self, chunk_size=800):
        self.recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text):
        chunks, heading, body_lines = [], "Mở đầu", []

        def flush_section():
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

**Thành viên 3 — Nguyễn Đàm Kiên (2A202602015)**
- **Loại chiến lược:** `SentenceChunker` với `max_sentences_per_chunk=3`, kết hợp `GeminiEmbedder` (`models/gemini-embedding-001`)
- **Mô tả & lý do:** Chiến lược này phù hợp với tài liệu chính sách Shopee vì nội dung thường được trình bày theo từng câu/điều riêng biệt. Bằng cách gom 3 câu vào một chunk, nhóm giữ được ngữ cảnh câu đầy đủ, tránh cắt ngang giữa các câu liên quan và vẫn giữ số lượng chunk vừa đủ để truy xuất hiệu quả. Khi kết hợp với Gemini embedding, hệ thống có thể tìm được chunk liên quan tốt hơn cho các câu hỏi về đổi hàng, hoàn tiền và phí vận chuyển.
- **Code snippet:**
```python
from NguyenDamKien_2A202602015.src.chunking import SentenceChunker
from NguyenDamKien_2A202602015.src.embeddings import GeminiEmbedder

chunker = SentenceChunker(max_sentences_per_chunk=3)
embedder = GeminiEmbedder(model_name="models/gemini-embedding-001")
```

**Thành viên 4 — Lê Kim Tính (2A202601560)**
- **Loại chiến lược:** `RecursiveChunker` (chunk_size=500) kết hợp `LocalEmbedder` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- **Mô tả & lý do:** Thuật toán thử lần lượt các separator theo độ ưu tiên (đoạn văn → xuống dòng → dấu chấm → khoảng trắng → ký tự), gộp các mảnh nhỏ liền kề lại nếu tổng độ dài không vượt `chunk_size`, giúp giữ trọn ý trong mỗi chunk. Chạy 5 câu hỏi benchmark bằng embedder đa ngôn ngữ thật (không dùng mock): **3/5 câu có chunk liên quan trong top-3** (câu 2, 3, 5), điểm similarity 0.59–0.89. Câu 1 thất bại vì câu hỏi gộp nhiều ý (đổi hàng + hàng lỗi + phải làm gì) khiến corpus trả nhầm chunk về phí vận chuyển. Câu 4 cũng thất bại dù dùng `metadata_filter={"customer_role": "buyer"}` — nguyên nhân: **toàn bộ tài liệu hiện đều gắn `customer_role: buyer`** (không có `both`/`seller`) nên filter không thu hẹp được tập ứng viên. Đề xuất: **cần nhóm rà soát lại metadata `customer_role` của `return-refund-policy.md`** trước khi chấm retrieval câu hỏi #4.
- **Code snippet:**
```python
from LeKimTinh_2A202601560.src.chunking import RecursiveChunker
from LeKimTinh_2A202601560.src.embeddings import LocalEmbedder

chunker = RecursiveChunker(chunk_size=500)
embedder = LocalEmbedder()  # mặc định sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**Thành viên 5 — Trần Chí Hiển (2A202601162)**
- **Loại chiến lược:** `FixedSizeChunker` (chunk_size=500, overlap=50) kết hợp Mock embedder (fallback bắt buộc — môi trường không tải được `LocalEmbedder` và không có API key OpenAI/Gemini)
- **Mô tả & lý do:** Trong khi 4 thành viên còn lại đều dùng chiến lược chunking nâng cao (Recursive, PolicySection theo heading, Sentence), tôi chọn giữ nguyên `FixedSizeChunker` — chiến lược baseline đơn giản nhất — để nhóm có một mốc so sánh rõ ràng giữa "baseline" và "chiến lược nâng cao". Trên tài liệu `return-refund-request-guide.md` (2.521 ký tự, `chunk_size=200`), FixedSizeChunker tạo 17 chunks, độ dài trung bình 195,4 ký tự — nhiều chunk hơn hẳn SentenceChunker (8 chunks, TB 311,6 ký tự) vì không tôn trọng ranh giới câu/đoạn, dễ cắt ngang ý. Do sandbox không tải được model nhúng và không có API key thật, tôi buộc dùng Mock embedder (đúng quy tắc fallback của bài); kết quả retrieval vì vậy không phản ánh chất lượng ngữ nghĩa thật (khác với kết quả 0,65–0,77 của các bạn dùng Gemini/OpenAI) — chi tiết số liệu và phân tích lỗi nằm trong `TranChiHien_2A202601162/REPORT_CANHAN.md`.
- **Code snippet:**
```python
from TranChiHien_2A202601162.src.chunking import FixedSizeChunker
from TranChiHien_2A202601162.src.embeddings import MockEmbedder  # fallback: không tải được LocalEmbedder

chunker = FixedSizeChunker(chunk_size=500, overlap=50)
embedder = MockEmbedder()
```

### So Sánh Giữa Các Chiến Lược

| Chiến lược | Số chunks (trung bình trên 3 tài liệu) | Điểm mạnh | Điểm yếu |
|---|---|---|---|
| FixedSize (200, overlap 20) | 27.7 | Đơn giản, nhanh | Cắt ngang câu/ý |
| Sentence (3 câu/chunk) | 9.3 | Giữ câu hoàn chỉnh | Chunk quá dài nếu câu dài |
| Recursive (500) | 33.7 | Giữ cấu trúc phân cấp | Số chunk nhiều hơn |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> RecursiveChunker (chunk_size=500) là tối ưu nhất. Văn bản chính sách Shopee có cấu trúc theo điều khoản rõ ràng (Điều 1, 2, 3...) với các mục con (1.1, 1.2...). RecursiveChunker ưu tiên tách tại `\n\n` (ranh giới giữa các điều khoản), giữ trọn vẹn từng quy định pháp lý trong một chunk. Khi kết hợp với Gemini Embedding 2, mỗi chunk biểu diễn đầy đủ một ý/quy định, giúp retrieval chính xác hơn so với FixedSize (cắt ngang) hay Sentence (chunk quá lớn/quá nhỏ).

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|---|---|
| 1 | Shopee có hỗ trợ đổi hàng không? Nếu hàng có vấn đề thì người mua phải làm gì? | Shopee hiện chưa hỗ trợ đổi hàng. Nếu hàng có vấn đề, người mua có thể từ chối nhận khi đồng kiểm hoặc gửi yêu cầu Trả hàng/Hoàn tiền. | `return-refund-general-rules.md` (Điều 1.1) |
| 2 | Thời hạn gửi yêu cầu trả hàng/hoàn tiền trên Shopee là bao lâu? | Thực phẩm tươi sống/đông lạnh: 24 giờ. Đơn tiêu chuẩn: 15 ngày. Đơn người bán tự giao: tối đa 20 ngày. | `return-refund-general-rules.md` (Điều 1.2) |
| 3 | Người mua cần gửi yêu cầu trả hàng bằng cách nào trên ứng dụng Shopee? | Cách 1: Tôi > Chờ giao hàng/Đã giao > Trả hàng/Hoàn tiền. Cách 2: Tôi > Trò Chuyện Với Shopee > Khiếu nại. | `return-refund-request-guide.md` (Điều 1) |
| 4 *(Cần filter metadata)* | Người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào? (filter: `customer_role=both`) | Người bán chịu phí khi sản phẩm lỗi/hư hỏng/không đúng mô tả do người bán, hoặc trường hợp ngoại lệ theo quyết định Shopee. | `return-refund-policy.md` (Điều 7.1) |
| 5 | Có những phương thức gửi hàng hoàn trả nào và chi phí ra sao? | 3 phương thức: (1) ĐV vận chuyển đến lấy (miễn phí), (2) Trả tại bưu cục SPX/GHN (miễn phí), (3) Tự sắp xếp (tự trả trước, Shopee hoàn sau). Shopee Mall hoàn bằng tiền/số dư. Non-Mall hoàn bằng Shopee Coins (25,000 nội tỉnh / 40,000 liên tỉnh). | `return-shipping-methods.md` (Điều 1.1, 2) |

### Tổng hợp chất lượng truy xuất

| # | Câu hỏi | Chiến lược | Có chunk liên quan trong top-3? | Ghi chú |
|---|---|---|---|---|
| 1 | Shopee có hỗ trợ đổi hàng không? | Recursive + Gemini Emb 2 | Có (Top-1, score: 0.7284) | Trả về đúng điều 1.1 quy định chung |
| 2 | Thời hạn gửi yêu cầu TH/HT? | Recursive + Gemini Emb 2 | Có (Top-1, score: 0.7305) | Trả về đúng điều 1.2 thời hạn |
| 3 | Cách gửi yêu cầu trả hàng trên app? | Recursive + Gemini Emb 2 | Có (Top-1, score: 0.7500) | Trả về đúng hướng dẫn step-by-step |
| 4 | Phí vận chuyển hoàn trả cho người bán? | Recursive + Gemini Emb 2 + filter | Có (Top-1, score: 0.7569) | Filter `customer_role=both` trả về đúng Điều 7.1 |
| 5 | Phương thức gửi hàng hoàn trả? | Recursive + Gemini Emb 2 | Có (Top-1, score: 0.7689) | Trả về đúng 3 phương thức |

**Lọc bằng metadata có giúp ích không?**
> Rất hữu ích ở câu hỏi 4. Khi hỏi về phí vận chuyển mà Người Bán phải chịu, nếu không dùng filter, hệ thống trả về chunks từ `return-refund-general-rules` (customer_role=buyer) — chỉ nói về thời hạn gửi yêu cầu, không liên quan đến nghĩa vụ tài chính của người bán. Khi dùng `search_with_filter({"customer_role": "both"})`, hệ thống chính xác trả về Điều 7.1 từ `return-refund-policy` (score 0.7569) — chunk chứa thông tin chi tiết về khi nào Người Bán chịu phí vận chuyển.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những insights hay nhất nhóm sẽ trình bày:**
- Gemini Embedding 2 cho điểm similarity trung bình 0.72-0.77 trên dữ liệu chính sách Shopee tiếng Việt, phân biệt rõ ràng chunk liên quan vs không liên quan.
- RecursiveChunker giữ trọn điều khoản pháp lý trong một chunk, trong khi FixedSizeChunker thường cắt ngang giữa câu quy định.
- Metadata filter (`customer_role`) là công cụ thiết yếu để phân biệt quy định dành cho buyer vs seller trên cùng một sàn TMĐT.

**Phân tích lỗi (Failure Analysis):**

Trường hợp lỗi tìm thấy: Câu hỏi "Thời hạn phản hồi của người bán khi nhận yêu cầu trả hàng là bao lâu?".

- **Không dùng filter:** Top-3 trả về chunks từ `return-refund-general-rules` (customer_role=buyer) về thời hạn gửi yêu cầu trả hàng của người MUA (24 giờ, 15 ngày...) — SAI ngữ cảnh. Score cao (0.71) vì từ khóa "thời hạn" + "trả hàng" trùng khớp, nhưng nội dung không trả lời câu hỏi.
- **Dùng filter customer_role=both:** Top-1 trả về đúng chunk chứa thông tin "Người Bán cần gửi phản hồi trong vòng 02 ngày lịch" (score 0.6689) từ `return-refund-policy`.
- **Nguyên nhân:** Embedding similarity cao giữa "thời hạn gửi yêu cầu trả hàng" (buyer) và "thời hạn phản hồi của người bán" (seller) vì chia sẻ nhiều từ khóa chung. Metadata filter giải quyết triệt để vấn đề này.
- **Đề xuất cải thiện:** Bổ sung trường metadata chi tiết hơn (ví dụ: `obligation_party: seller` cho các điều khoản liên quan đến nghĩa vụ bên cụ thể) hoặc áp dụng Hybrid Search (BM25 + Vector) để tăng độ chính xác.

**Bài học rút ra:**
> Cùng bộ tài liệu, nếu chunk quá nhỏ (FixedSize 200) sẽ mất ngữ cảnh, còn Sentence có thể tạo chunk quá lớn khi câu chính sách dài. RecursiveChunker 500 là điểm cân bằng tốt nhất cho văn bản pháp lý.

**Nếu làm lại:**
> Mở rộng metadata với `obligation_party` (buyer/seller/shopee/carrier), `effective_date`, và tích hợp Hybrid Search. Thêm tài liệu về chính sách người bán (Seller Center) để cân bằng customer_role.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
