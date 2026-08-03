# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn Nam  
**Mã học viên:** 2A202601973  
**Khóa:** K4  
**Nhóm:** Những con vịt bầu  
**Ngày:** 03/08/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm nộp chung trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao nghĩa là gì?**
> Hai vector văn bản hướng về cùng một phía trong không gian vector (góc xấp xỉ 0 độ), thể hiện tương đồng cao về ngữ nghĩa, độc lập với độ dài văn bản.

**Ví dụ có độ tương tự CAO:**
- Câu A: Con mèo đang nằm ngủ say trên chiếc ghế sô pha.
- Câu B: Mèo con đang ngủ trên ghế dài phòng khách.
- Tại sao: Cùng mô tả mèo ngủ trên ghế, chia sẻ khái niệm cốt lõi.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Cầu thủ đã ghi bàn thắng quyết định ở phút 90.
- Câu B: Công thức hóa học của axit sunfuric là H2SO4.
- Tại sao: Hai lĩnh vực hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance?**
> Cosine chỉ đo góc giữa vector, không bị ảnh hưởng bởi magnitude. Câu ngắn và đoạn văn dài cùng ý nghĩa vẫn đạt điểm cao, trong khi Euclidean bị sai lệch do độ dài khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**10,000 ký tự, chunk_size=500, overlap=50:**
> stride = 500-50 = 450. Chunks = ceil((10000-50)/(500-50)) = ceil(9950/450) = ceil(22.11) = **23 chunks**

**Overlap tăng lên 100:**
> stride = 500-100 = 400. Chunks = ceil((10000-100)/(500-100)) = ceil(9900/400) = **25 chunks**. Tăng overlap giúp giữ ngữ cảnh liên tục tại ranh giới chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`:**
> Dùng regex `re.split(r'(?<=[.!?])\s+|\.\n', text)` nhận diện ranh giới câu. Loại bỏ câu rỗng, gom nhóm theo `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`:**
> Thuật toán đệ quy với phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Tách theo phân cách hiện tại, ghép tuần tự; nếu đoạn con vượt `chunk_size` thì gọi đệ quy với phân cách tiếp theo.

### Lớp EmbeddingStore

**`add_documents` + `search`:**
> `add_documents` sinh UUID, tính embedding bằng `embedding_fn`, lưu vào `_store`. `search` nhúng query thành vector, tính cosine similarity với toàn bộ vector, sắp xếp giảm dần trả `top_k`.

**`search_with_filter` + `delete_document`:**
> `search_with_filter` tiền lọc theo `metadata_filter` rồi mới tính similarity. `delete_document` xóa tất cả chunk có `id == doc_id` hoặc `metadata.doc_id == doc_id`.

### KnowledgeBaseAgent

**`answer`:**
> Gọi `store.search(query, top_k)` → tổng hợp ngữ cảnh → xây prompt RAG → gọi Gemini 2.5 Flash qua `llm_fn` để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Paste the FULL test results below:

```
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Namdr\Downloads\DAY07_2A202601973_NguyenVanNam
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.22s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42 (100%)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Using **Gemini Embedding 2** (`models/gemini-embedding-2`):

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (Gemini Embedding 2) | Đánh giá |
|------|-----------|-----------|---------|-----------------------------------|----------|
| 1 | Tôi yêu lập trình Python | Python là ngôn ngữ lập trình tuyệt vời | Cao | **0.7753** | Đúng |
| 2 | Tôi yêu lập trình Python | Trời hôm nay nhiều mây và có mưa | Thấp | **0.4175** | Đúng |
| 3 | Mèo là động vật nuôi trong nhà | Chó và mèo là thú cưng phổ biến | Cao | **0.8130** | Đúng |
| 4 | Thuật toán RAG kết hợp retrieval và LLM | Vector database dùng để lưu trữ embedding | Cao | **0.7757** | Đúng |
| 5 | Hà Nội là thủ đô của Việt Nam | Paris là thủ đô của nước Pháp | Cao | **0.7108** | Đúng |

**Kết quả nào bất ngờ nhất?**
> Cặp 5 đạt 0.7108 dù không chia sẻ từ vựng địa danh nào. Chứng tỏ Gemini Embedding 2 nắm bắt được quan hệ ngữ nghĩa mức cao (Capital-Country relationship) chứ không chỉ so khớp từ khóa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy 5 câu hỏi đánh giá trên bộ dữ liệu **chính sách Shopee thực tế** (5 tài liệu, 83 chunks) với **Gemini Embedding 2** + **Gemini 2.5 Flash**:

| # | Câu hỏi (Query) | Top-1 Chunk (tóm tắt) | Điểm Score | Relevant? | Agent Answer (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Shopee có hỗ trợ đổi hàng không? Nếu hàng có vấn đề thì người mua phải làm gì? | `return-refund-general-rules`: Shopee hiện chưa hỗ trợ đổi hàng. Nếu hàng có vấn đề, có thể từ chối nhận khi đồng kiểm hoặc gửi yêu cầu TH/HT | **0.7284** | Có | Shopee chưa hỗ trợ đổi hàng; người mua có thể từ chối nhận khi đồng kiểm hoặc gửi yêu cầu Trả hàng/Hoàn tiền. |
| 2 | Thời hạn gửi yêu cầu trả hàng/hoàn tiền trên Shopee là bao lâu? | `return-refund-general-rules`: Thực phẩm tươi sống 24 giờ, đơn tiêu chuẩn 15 ngày, người bán tự giao tối đa 20 ngày | **0.7305** | Có | 24 giờ cho thực phẩm tươi sống/đông lạnh, 15 ngày cho đơn tiêu chuẩn, tối đa 20 ngày cho đơn người bán tự giao. |
| 3 | Người mua cần gửi yêu cầu trả hàng bằng cách nào trên ứng dụng Shopee? | `return-refund-request-guide`: Hai cách — qua trang đơn hàng hoặc qua mục Hỗ trợ khách hàng | **0.7500** | Có | Cách 1: Tôi > Chờ giao hàng/Đã giao > Trả hàng/Hoàn tiền. Cách 2: Tôi > Trò Chuyện Với Shopee > Khiếu nại. |
| 4 | Người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào? (filter: customer_role=both) | `return-refund-policy`: Người Bán chịu chi phí vận chuyển hoàn trả khi sản phẩm thuộc lỗi của Người Bán | **0.7569** | Có | Người bán chịu phí khi sản phẩm lỗi/hư hỏng/không đúng mô tả do người bán, hoặc trường hợp ngoại lệ theo quyết định Shopee. |
| 5 | Có những phương thức gửi hàng hoàn trả nào và chi phí ra sao? | `return-shipping-methods`: 3 phương thức — ĐV vận chuyển đến lấy, trả tại bưu cục, tự sắp xếp | **0.7689** | Có | 3 phương thức: (1) ĐV vận chuyển đến lấy (miễn phí), (2) Trả tại bưu cục SPX/GHN (miễn phí), (3) Tự sắp xếp (tự trả trước, Shopee hoàn sau). |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (100%)

**Điều hay nhất tôi học được:**
> Khi sử dụng Gemini Embedding 2 trên dữ liệu chính sách Shopee thực tế (~50,000 ký tự, 83 chunks), metadata filter (`customer_role: both`) giúp truy xuất chính xác các điều khoản dành cho người bán mà không bị nhiễu bởi các chunk chỉ dành cho người mua. Ở câu hỏi 4 (về phí vận chuyển hoàn trả), khi dùng filter `customer_role=both`, hệ thống trả về đúng chunk chứa Điều 7.1 về chi phí vận chuyển mà Người Bán phải chịu (score 0.7569), trong khi không dùng filter có thể trả về chunk về thời hạn gửi yêu cầu (không liên quan).

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
