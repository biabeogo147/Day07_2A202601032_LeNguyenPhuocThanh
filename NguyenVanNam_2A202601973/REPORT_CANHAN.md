# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn Nam  
**Mã học viên:** 2A202601973  
**Khóa:** K4  
**Nhóm:** Những con vịt bầu  
**Ngày:** 03/08/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector văn bản hướng về cùng một phía trong không gian vector biểu diễn (góc giữa hai vector xấp xỉ 0 độ), thể hiện mức độ tương đồng cao về mặt ý nghĩa, ngữ nghĩa và chủ đề, độc lập với độ dài ngắn của văn bản.

**Ví dụ có độ tương tự CAO:**
- Câu A: *Con mèo đang nằm ngủ say trên chiếc ghế sô pha.*
- Câu B: *Mèo con đang ngủ trên ghế dài phòng khách.*
- Tại sao tương đồng: Cả hai câu cùng mô tả trạng thái một chú mèo đang nằm ngủ trên ghế trong phòng khách, chia sẻ các khái niệm và ngữ cảnh cốt lõi giống nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: *Cầu thủ đã ghi bàn thắng quyết định ở phút 90.*
- Câu B: *Công thức hóa học của axit sunfuric là H2SO4.*
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn không liên quan (thể thao bóng đá và hóa học vô cơ), không có từ vựng hay ngữ cảnh tương đồng.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity đo góc định hướng giữa hai vector thay vì độ dài độ lớn (magnitude). Do đó, một câu ngắn và một đoạn văn dài có cùng nội dung vẫn đạt điểm tương đồng cao với Cosine, trong khi khoảng cách Euclid sẽ bị kéo giãn và sai lệch lớn do độ dài văn bản khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* 
> - Bước nhảy (stride) = `chunk_size - overlap` = `500 - 50 = 450` ký tự.
> - Số lượng chunk = `1 + ceil((10000 - 500) / 450) = 1 + ceil(9500 / 450) = 1 + ceil(21.111) = 1 + 22 = 23 chunks`.
> - *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> - Bước nhảy mới = `500 - 100 = 400` ký tự.
> - Số lượng chunk = `1 + ceil((10000 - 500) / 400) = 1 + ceil(9500 / 400) = 1 + 24 = 25 chunks`.
> - Ta muốn tăng overlap để đảm bảo thông tin và ngữ cảnh tại các ranh giới cắt giữa các chunk không bị chia tách hoặc đứt gãy, giúp hệ thống RAG truy xuất được đầy đủ ý nghĩa liên tục của câu văn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy `re.split(r'(?<=[.!?])\s+|\.\n', text)` để xác định ranh giới kết thúc câu một cách chuẩn xác theo dấu câu tiếng Việt và tiếng Anh. Sau khi loại bỏ câu rỗng và làm sạch khoảng trắng, các câu được gom nhóm thành các chunk văn bản với số lượng câu tối đa theo tham số `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng thuật toán chia đệ quy phân cấp với danh sách phân cách ưu tiên từ lớn đến nhỏ: `["\n\n", "\n", ". ", " ", ""]`. Nếu đoạn văn bản vượt quá `chunk_size`, hệ thống tách theo dấu phân cách ưu tiên hiện tại và ghép nối tuần tự với khoảng gối đầu `overlap`. Nếu bất kỳ đoạn con nào vẫn dài hơn `chunk_size`, hàm tiếp tục gọi đệ quy `_split` với dấu phân cách có mức ưu tiên tiếp theo.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` sinh mã định danh duy nhất (UUID), tính vector embedding cho từng Document chunk bằng `embedding_fn`, lưu trữ bản ghi vào danh sách nội bộ `_store` (và đồng bộ vào ChromaDB nếu có). `search` chuyển đổi câu truy vấn thành vector embedding, tính độ tương tự cosine / tích vô hướng chuẩn hóa với toàn bộ vector trong kho, sau đó sắp xếp giảm dần theo điểm số để trả về `top_k` kết quả có điểm cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` duyệt và tiền lọc danh sách bản ghi, chỉ giữ lại các chunk thỏa mãn toàn bộ các cặp key-value trong `metadata_filter` trước khi tiến hành tính toán độ tương đồng cosine. `delete_document` tìm kiếm và loại bỏ tất cả các chunk có `id == doc_id` hoặc `metadata.get('doc_id') == doc_id` và trả về `True` nếu có ít nhất một bản ghi bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tác tử nhận câu hỏi từ người dùng, gọi `store.search(query, top_k=top_k)` để thu thập ngữ cảnh liên quan nhất. Ngữ cảnh được định dạng vào cấu trúc Prompt RAG tiêu chuẩn gồm chỉ dẫn rõ ràng (`Context... Question... Answer:`). Sau đó, prompt được chuyển qua mô hình LLM (Gemini 2.5 Flash / `llm_fn`) để tổng hợp câu trả lời ngắn gọn, chính xác dựa trên dữ liệu thực tế.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua toàn bộ 42/42 bộ kiểm thử tự động của hệ thống.

### Kết Quả Kiểm Thử (Test Results)

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

Đo lường độ tương tự ngữ nghĩa thực tế sử dụng mô hình **Gemini Embedding 2** (`models/gemini-embedding-2`):

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (Gemini Embedding 2) | Đánh giá |
|------|-----------|-----------|---------|-----------------------------------|----------|
| 1 | Tôi yêu lập trình Python | Python là ngôn ngữ lập trình tuyệt vời | Cao | **0.7753** | Đúng |
| 2 | Tôi yêu lập trình Python | Trời hôm nay nhiều mây và có mưa | Thấp | **0.4175** | Đúng |
| 3 | Mèo là động vật nuôi trong nhà | Chó và mèo là thú cưng phổ biến | Cao | **0.8130** | Đúng |
| 4 | Thuật toán RAG kết hợp retrieval và LLM | Vector database dùng để lưu trữ embedding | Cao | **0.7757** | Đúng |
| 5 | Hà Nội là thủ đô của Việt Nam | Paris là thủ đô của nước Pháp | Cao | **0.7108** | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp số 5 ("Hà Nội là thủ đô của Việt Nam" và "Paris là thủ đô của nước Pháp") đạt điểm tương đồng cao (**0.7108**) dù không chia sẻ từ vựng về địa danh cụ thể nào. Điều này chứng minh không gian embedding của mô hình **Gemini Embedding 2** nắm bắt được cấu trúc quan hệ ngữ nghĩa mức cao (quan hệ *Thủ đô - Quốc gia* / *Capital-Country relationship*) chứ không chỉ so khớp từ khóa cơ học.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** với mô hình **Gemini Embedding 2** (`models/gemini-embedding-2`) và tác tử **Gemini 2.5 Flash**:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Quy định đổi trả hàng bị lỗi thế nào? | `returns-policy.md`: ...yêu cầu trả hàng hoặc hoàn tiền nếu sản phẩm bị lỗi do nhà sản xuất... | **0.6908** | Có | Người mua có quyền gửi yêu cầu đổi trả/hoàn tiền khi hàng lỗi, cần cung cấp bằng chứng và gửi trong thời hạn quy định. |
| 2 | Người bán có trách nhiệm gì khi đăng bán sản phẩm? | `seller-listing.md`: ...chịu trách nhiệm hoàn toàn về thông tin sản phẩm (giá, mô tả, tình trạng)... | **0.7020** | Có | Người bán chịu trách nhiệm toàn bộ về độ chính xác thông tin và không được bán hàng cấm. |
| 3 | Người mua có quyền gì khi hàng nhận không đúng mô tả? | `returns-policy.md`: ...yêu cầu trả hàng hoặc hoàn tiền nếu không đúng mô tả... | **0.6698** | Có | Người mua được quyền yêu cầu hoàn tiền/đổi trả trong thời hạn quy định kèm bằng chứng cụ thể. |
| 4 | Thời hạn gửi yêu cầu đổi trả hàng là khi nào? | `returns-policy.md`: ...phải được gửi trong thời hạn quy định ghi trên trang sản phẩm hoặc chính sách sàn... | **0.6558** | Có | Yêu cầu phải gửi trong thời hạn quy định ghi trên trang sản phẩm hoặc chính sách của sàn. |
| 5 | Sản phẩm nào bị cấm đăng bán trên sàn? | `seller-listing.md`: ...không được đăng bán sản phẩm bị hạn chế hoặc cấm theo quy định pháp luật... | **0.6622** | Có | Nghiêm cấm các sản phẩm bị hạn chế hoặc cấm theo pháp luật và chính sách của sàn thương mại điện tử. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (100%)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc áp dụng mô hình embedding ngữ nghĩa hiện đại như **Gemini Embedding 2** kết hợp cơ chế lọc siêu dữ liệu (`search_with_filter`) giúp hệ thống RAG định vị chính xác ngữ cảnh liên quan mà không bị nhầm lẫn giữa các vai trò (Người mua vs Người bán), qua đó giúp LLM tổng hợp câu trả lời đúng trọng tâm.

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
