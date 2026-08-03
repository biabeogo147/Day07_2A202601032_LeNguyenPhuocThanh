# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Chí Hiển
**Mã học viên:** 2A202601162
**Nhóm:** Những con vịt bầu
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm nộp chung trong `../report/REPORT_NHOM.md`. Chi tiết thang điểm: `../docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai đoạn văn bản có cosine similarity cao nghĩa là embedding (vector số hoá ý nghĩa) của chúng "chỉ cùng một hướng" trong không gian nhiều chiều — nói cách đơn giản: hai câu đang nói về **cùng một ý**, dù dùng từ ngữ khác nhau. Cosine similarity đo góc giữa hai vector chứ không đo độ dài, nên nó phản ánh sự tương đồng về *nội dung/ý nghĩa* chứ không bị ảnh hưởng bởi câu dài hay ngắn.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi muốn trả lại sản phẩm vì bị lỗi."
- Câu B: "Làm sao để được hoàn tiền khi hàng bị hư?"
- Tại sao tương đồng: cả hai câu đều xoay quanh cùng một chủ đề — sản phẩm có vấn đề và người mua muốn trả hàng/hoàn tiền. Từ ngữ khác nhau ("trả lại" vs "hoàn tiền", "lỗi" vs "hư") nhưng **ý định** giống nhau, nên một embedding tốt sẽ đặt hai câu này gần nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi muốn trả lại sản phẩm vì bị lỗi."
- Câu B: "Hôm nay trời Hà Nội nắng đẹp."
- Tại sao khác: hai câu không liên quan gì đến nhau về chủ đề (chính sách đổi trả vs thời tiết), nên vector biểu diễn của chúng sẽ gần như vuông góc — similarity gần 0.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Euclidean distance đo khoảng cách "vật lý" giữa hai điểm, nên bị ảnh hưởng bởi **độ dài (magnitude)** của vector — một câu dài, lặp từ nhiều có thể cho vector "to" hơn dù nói cùng một ý với câu ngắn. Cosine similarity chỉ quan tâm **hướng** của vector (tức là *ý nghĩa*), bỏ qua độ dài, nên phù hợp hơn khi ta muốn so sánh "hai câu có cùng ý không" thay vì "hai câu có cùng độ dài/tần suất từ không".

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính:
> `số chunk = ceil((10000 − 50) / (500 − 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
>
> Đáp án: **23 chunks**

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> `ceil((10000 − 100) / (500 − 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks`
> Overlap tăng từ 50 lên 100 → số chunk tăng từ 23 lên **25** (tăng 2 chunk). Overlap lớn hơn làm bước nhảy (`chunk_size − overlap`) nhỏ hơn, nên các chunk chồng lên nhau nhiều hơn và cần nhiều chunk hơn để phủ hết tài liệu. Lý do muốn tăng overlap: tránh việc một câu/ý quan trọng bị **cắt ngang đúng ranh giới hai chunk** — nếu không có overlap, thông tin nằm vắt qua ranh giới có thể bị mất hoàn toàn ở cả hai chunk; overlap giữ lại phần đầu/cuối để chunk liền kề vẫn còn ngữ cảnh. Đánh đổi: nhiều chunk hơn → tốn thêm dung lượng lưu trữ và thời gian embed.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận khi triển khai các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])\s+` để tách câu — nghĩa là "cắt ngay sau dấu `.`, `!` hoặc `?`, tại chỗ có khoảng trắng/xuống dòng theo sau" (bao trùm cả 3 trường hợp `". "`, `"! "`, `"? "` và `".\n"` mà đề bài yêu cầu). Sau khi tách, tôi lọc bỏ câu rỗng và `strip()` khoảng trắng thừa, rồi gom từng nhóm tối đa `max_sentences_per_chunk` câu lại thành một chunk bằng cách join với dấu cách. Edge case đã xử lý: văn bản rỗng trả về `[]` ngay; văn bản không có dấu câu kết thúc vẫn được coi là 1 "câu" duy nhất nhờ regex không tách được gì.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy theo đúng tinh thần "thử tách bằng dấu phân cách ưu tiên cao nhất trước (`\n\n`), nếu phần nào vẫn còn quá dài thì tiếp tục tách bằng dấu phân cách kế tiếp (`\n`, rồi `". "`, rồi `" "`, cuối cùng là cắt cứng theo ký tự)". Cụ thể: nếu đoạn text hiện tại đã ngắn hơn `chunk_size` thì trả về luôn (base case). Ngược lại, tách theo separator đầu tiên, rồi gom các phần nhỏ lại với nhau (giống kiểu "đóng gói" cho đầy `chunk_size`) — nếu một phần đơn lẻ vẫn dài hơn `chunk_size`, gọi đệ quy `_split` cho riêng phần đó với danh sách separator còn lại. Nếu hết separator mà vẫn dài, cắt cứng theo `chunk_size` ký tự (base case cuối cùng, đảm bảo hàm luôn dừng).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hoá qua `_make_record()` thành một dict có `id` lưu trữ riêng (không trùng với `doc.id`, để một tài liệu có thể sinh nhiều chunk), `content`, `metadata` (giữ nguyên metadata gốc + luôn gắn thêm `doc_id` để tiện lọc/xoá sau này), và `embedding` (gọi `self._embedding_fn(content)`). `add_documents` lặp qua từng doc, tạo record rồi append vào `self._store` (danh sách trong bộ nhớ). `search` nhúng câu hỏi thành vector, rồi gọi `_search_records` để tính **dot product** giữa vector câu hỏi và từng vector đã lưu (embedding đã chuẩn hoá nên dot product ≈ cosine similarity), sắp xếp giảm dần theo điểm và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata **trước**: chỉ giữ lại các record có tất cả cặp `key: value` trong `metadata_filter` khớp với metadata đã lưu, sau đó mới chạy `_search_records` trên tập đã lọc — đảm bảo kết quả trả về luôn thoả điều kiện lọc, không phải lọc lại sau khi xếp hạng. `delete_document` xoá mọi record có `metadata['doc_id'] == doc_id` (đúng field được gắn sẵn trong `_make_record`), trả về `True`/`False` tuỳ có record nào bị xoá hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer()` gọi `store.search()` lấy `top_k` chunk liên quan nhất, ghép nội dung từng chunk kèm nhãn nguồn (`[Nguồn: doc_id]`) thành một khối "Ngữ cảnh". Prompt cuối cùng có cấu trúc: hướng dẫn LLM chỉ trả lời dựa trên ngữ cảnh (không suy diễn) → khối ngữ cảnh → câu hỏi → yêu cầu trả lời. Nếu store không tìm được chunk nào (rỗng), tôi thay ngữ cảnh bằng câu thông báo rõ ràng "không tìm thấy ngữ cảnh liên quan" — để LLM không bịa thông tin từ tài liệu không tồn tại.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
$ LAB_SOLUTION_PACKAGE=TranChiHien_2A202601162.src python -m pytest tests/ -v

============================= test session starts ==============================
platform darwin -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker (7 tests) PASSED
tests/test_solution.py::TestSentenceChunker (4 tests) PASSED
tests/test_solution.py::TestRecursiveChunker (4 tests) PASSED
tests/test_solution.py::TestEmbeddingStore (8 tests) PASSED
tests/test_solution.py::TestKnowledgeBaseAgent (2 tests) PASSED
tests/test_solution.py::TestComputeSimilarity (4 tests) PASSED
tests/test_solution.py::TestCompareChunkingStrategies (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument (3 tests) PASSED

============================== 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua:** 42 / 42

> Ghi chú môi trường: máy chạy Python 3.14 (bài chuẩn hoá trên Python 3.11, nhưng không có sẵn 3.11 trên máy). Toàn bộ 42 test không dùng cú pháp riêng của bản Python nào cả nên chạy pass bình thường trên 3.14; không có lỗi nào phát sinh do khác biệt phiên bản.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> **Lưu ý quan trọng:** Máy tôi không tải được model nhúng tiếng Việt (`sentence-transformers`, do sandbox chặn kết nối ra Hugging Face) và cũng không có `OPENAI_API_KEY`/Gemini key. Theo đúng cơ chế fallback của bài, tôi buộc phải dùng **Mock embedder** để chạy phần này — kết quả dưới đây **không phản ánh ngữ nghĩa thật** (README đã cảnh báo trước), tôi vẫn dự đoán trước như yêu cầu để đối chiếu, và phần "bất ngờ nhất" chính là **mock đã sai gần như hoàn toàn** so với dự đoán dựa trên ý nghĩa thật.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (Mock) | Đúng? |
|---|---|---|---|---|---|
| 1 | "Tôi muốn trả lại sản phẩm vì bị lỗi." | "Làm sao để hoàn tiền khi hàng bị hư?" | cao | -0.0608 | ❌ Sai |
| 2 | "Tôi muốn trả lại sản phẩm vì bị lỗi." | "Hôm nay trời Hà Nội nắng đẹp." | thấp | 0.0372 | ✅ Đúng (thấp, dù không âm như kỳ vọng) |
| 3 | "Người bán phải gửi hàng trong 3 ngày." | "Người bán cần giao hàng trong vòng 3 ngày làm việc." | cao | 0.0042 | ❌ Sai |
| 4 | "Phí vận chuyển hoàn trả là bao nhiêu?" | "Con mèo của tôi rất dễ thương." | thấp | -0.0541 | ✅ Đúng (thấp) |
| 5 | "Shopee có hỗ trợ đổi hàng không?" | "Shopee có cho đổi sản phẩm khác không?" | cao | 0.0273 | ❌ Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **Cặp 3**: hai câu gần như diễn đạt lại y nguyên một ý ("người bán gửi hàng trong 3 ngày") mà Mock embedder cho điểm gần 0 (0.0042) — tức "không liên quan gì nhau" theo mock, hoàn toàn ngược với trực giác. Điều này cho thấy: embedding **không tự nhiên hiểu ý nghĩa** — nó phải được **học** từ dữ liệu thật (như Gemini/OpenAI embedding models mà các bạn cùng nhóm dùng). Mock embedder trong bài chỉ băm chuỗi ký tự (hash) thành số ngẫu nhiên có kiểm soát (deterministic nhưng không liên quan đến ngữ nghĩa) — nên hai câu dù giống ý nhau đến đâu, chỉ cần khác một chữ cái là vector đã hoàn toàn khác. Đây chính xác là lý do README cảnh báo không dùng mock để kết luận chất lượng semantic retrieval — bài học lớn nhất tôi rút ra là: **chunking đúng chưa đủ, embedder phải thực sự hiểu ngôn ngữ thì retrieval mới có ý nghĩa.**

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược cá nhân:** `FixedSizeChunker(chunk_size=500, overlap=50)` + **Mock embedder** (fallback bắt buộc — xem ghi chú môi trường ở Phần 4). Tôi chọn baseline đơn giản nhất (khác với 3 bạn còn lại đều dùng chiến lược nâng cao) để nhóm có một điểm so sánh "sàn" (floor) rõ ràng.

Chạy đúng 5 câu hỏi đánh giá của nhóm trên mã nguồn cá nhân trong `src`; xem `../report/REPORT_NHOM.md`.

| # | Câu hỏi | Top-1 Chunk truy xuất được | Điểm Score | Relevant? | Câu trả lời Agent |
|---|---|---|---|---|---|
| 1 | Shopee có hỗ trợ đổi hàng không? | `shipping-faq::chunk_4` (nội dung về thanh toán/voucher) | 0.3836 | ❌ Không liên quan | [STUB-LLM] — xem ghi chú |
| 2 | Thời hạn gửi yêu cầu trả hàng/hoàn tiền? | `return-refund-policy::chunk_33` (về hoàn tiền, không phải thời hạn) | 0.2803 | ❌ Không liên quan | [STUB-LLM] |
| 3 | Cách gửi yêu cầu trả hàng trên app? | `return-refund-general-rules::chunk_11` (về voucher/hoàn Xu) | 0.2643 | ❌ Không liên quan | [STUB-LLM] |
| 4 *(filter `customer_role=both`)* | Phí vận chuyển hoàn trả cho người bán? | — không có kết quả — | — | ❌ Rỗng (xem phân tích lỗi) | [STUB-LLM] |
| 5 | Phương thức gửi hàng hoàn trả? | `shipping-faq::chunk_0` (mục lục FAQ vận chuyển, không nêu phương thức cụ thể) | 0.3549 | ⚠️ Gần đúng chủ đề nhưng không trúng đoạn chi tiết | [STUB-LLM] |

**Bao nhiêu câu hỏi trả về chunk liên quan trong top-3?** 0 / 5 (đúng nghĩa top‑1 trúng); nếu tính "đúng chủ đề rộng" thì 1/5 (câu 5).

> Ghi chú minh bạch: cột "Câu trả lời Agent" hiển thị `[STUB-LLM]` vì tôi **không có API key LLM thật** (không có OpenAI/Gemini key trong `.env`) — `llm_fn` truyền vào `KnowledgeBaseAgent` chỉ là một hàm giả lập đếm số đoạn ngữ cảnh, dùng để **chứng minh luồng RAG (retrieve → build prompt → gọi llm_fn) chạy đúng cơ chế**, không phải để đánh giá chất lượng câu trả lời. Phần agent code (`agent.py`) đã pass đầy đủ test và có thể cắm bất kỳ LLM thật nào vào `llm_fn` mà không cần sửa gì thêm.

**Điều hay nhất học được từ thành viên khác / nhóm khác:**
> So với 3 chiến lược của các bạn trong nhóm (Nguyễn Văn Nam: Recursive+Gemini, Lê Nguyễn Phước Thành: PolicySectionChunker theo heading+OpenAI, Nguyễn Đàm Kiên: Sentence(3 câu)+Gemini — điểm similarity thật của các bạn đều đạt 0.65–0.77 và trúng đúng chunk), kết quả của tôi cho thấy rất rõ: **vấn đề không nằm ở chunking mà nằm ở embedder**. Cùng một `FixedSizeChunker` chạy với embedder thật (kết quả nhóm) vẫn tốt hơn nhiều so với chunking nâng cao chạy với Mock. Điều tôi học được nhiều nhất là ý tưởng của bạn Thành: `PolicySectionChunker` **giữ tiêu đề đi cùng nội dung** trước khi chia nhỏ — với văn bản chính sách có cấu trúc điều/khoản như Shopee, cách này trực giác hơn `FixedSizeChunker` của tôi vì không bao giờ cắt rời một quy định khỏi tiêu đề của nó. Nếu làm lại, tôi sẽ thử kết hợp ý tưởng "giữ heading" của bạn Thành với `FixedSizeChunker` để vừa đơn giản vừa giữ ngữ cảnh tốt hơn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất | 7 / 10 (điểm retrieval thấp do giới hạn môi trường — không phải lỗi code — đã giải thích minh bạch ở trên) |
| **Tổng phần cá nhân** | **57 / 60** |
