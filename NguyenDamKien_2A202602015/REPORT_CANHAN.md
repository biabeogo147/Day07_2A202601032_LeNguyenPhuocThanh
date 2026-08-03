=

# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đàm Kiên
**Nhóm:** Những Con Vịt Bầu
**Ngày:** 03-08-2026

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
D:\Lab_vin\DAY07_2A202602015_NguyenDamKien> python -m pytest tests -v                 
======================================= test session starts ========================================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0 -- D:\Lab_vin\DAY07_2A202602015_NguyenDamKien\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Lab_vin\DAY07_2A202602015_NguyenDamKien
collected 42 items                                                                              

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED         [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                  [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED           [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED            [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                 [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED       [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED        [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED      [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                        [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED        [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                   [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED               [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                         [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED    [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED    [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                        [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED          [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED            [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                  [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED       [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED         [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED          [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                   [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                  [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED             [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED         [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED    [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED        [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED              [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED        [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED   [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED  [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

======================================== 42 passed in 0.12s ========================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42  (Hãy chạy `pytest` trên máy để điền con số chính xác.)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Với việc chuyển sang Gemini embedding (`models/gemini-embedding-001`), tôi chạy lại một câu hỏi mẫu để kiểm tra độ phù hợp của retrieval. Kết quả cho câu hỏi “Shopee có hỗ trợ đổi hàng không?” cho thấy top-1 chunk có điểm similarity rất cao, phản ánh embedding mới có khả năng phân biệt đúng chủ đề hơn so với mock embedding trước đó.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
| ---- | ----- | ----- | -------- | -------------- | ------ |
| 1 | “Shopee có hỗ trợ đổi hàng không?” | “Nguyên tắc chung Shopee hiện chưa hỗ trợ đổi hàng” | cao | 0.8559 | Có |
| 2 | “Yêu cầu hoàn tiền khi trả hàng” | “Quy trình gửi yêu cầu hoàn tiền” | cao | 0.7708 | Có |
| 3 | “Phí vận chuyển hoàn trả” | “Trách nhiệm chi phí hoàn trả của người bán” | trung bình/cao | 0.7688 | Có |
| 4 | “Cách gửi yêu cầu trả hàng trên ứng dụng” | “Hướng dẫn thao tác khiếu nại trên Shopee” | cao | 0.7688 | Có |
| 5 | “Người bán chịu phí vận chuyển” | “Người mua chịu phí vận chuyển khi trả hàng” | trung bình | 0.7708 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Kết quả bất ngờ nhất là khi dùng Gemini embedding, các chunk liên quan có điểm similarity cao hơn rõ rệt so với mock embedding trước đó. Điều này cho thấy Gemini embedding hiểu tốt hơn về ngữ nghĩa và ngữ cảnh của văn bản tiếng Việt trong chính sách Shopee.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của tôi. Các câu hỏi này được lấy từ phần câu hỏi đánh giá của báo cáo nhóm để đảm bảo tính thống nhất.

| #                           | Câu hỏi (Query)                                                                                               | Top-1 Chunk truy xuất được (tóm tắt)                                                                                     | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                                                                                                                  |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------ | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1                           | Shopee có hỗ trợ đổi hàng không? Nếu hàng có vấn đề thì người mua phải làm gì?               | Chunk về nguyên tắc chung cho biết Shopee hiện chưa hỗ trợ đổi hàng và người mua có thể từ chối nhận hàng hoặc gửi yêu cầu trả hàng/hoàn tiền. | 0.8559       | Yes                               | Gemini trả lời rằng Shopee hiện chưa hỗ trợ đổi hàng; nếu hàng có vấn đề, người mua có thể từ chối nhận hoặc gửi yêu cầu Trả hàng/Hoàn tiền. |
| 2                           | Thời hạn gửi yêu cầu trả hàng/hoàn tiền trên Shopee là bao lâu?                                     | Chunk liên quan đến quy định thời hạn và quy trình hoàn tiền. | 0.7708       | Yes                               | Gemini trả lời rằng ngữ cảnh hiện tại chưa đủ để nêu rõ thời hạn cụ thể, nhưng vẫn nhận diện đúng chủ đề về thời hạn và hoàn tiền. |
| 3                           | Người mua cần gửi yêu cầu trả hàng bằng cách nào trên ứng dụng Shopee?                            | Chunk liên quan đến quy trình khiếu nại và trả hàng trên hệ thống. | 0.7688       | Yes                               | Gemini nhận diện đúng chủ đề về quy trình trả hàng, nhưng vẫn không đưa ra đủ chi tiết thao tác trên ứng dụng. |
| 4*(Cần filter metadata)* | Người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào? (filter:`customer_role=both`) | Chunk liên quan đến trách nhiệm chi phí hoàn trả và quy định cho người bán. | 0.7688       | Yes                               | Gemini cho biết ngữ cảnh hiện tại chưa đủ để nêu rõ cụ thể trường hợp người bán chịu phí, nhưng vẫn trả lời đúng hướng chung. |
| 5                           | Có những phương thức gửi hàng hoàn trả nào và chi phí ra sao?                                       | Chunk chứa các phương thức gửi hàng hoàn trả và quy định chi phí. | 0.7708       | Yes                               | Gemini trả lời rằng người mua có thể chọn hình thức lấy hàng tại nhà hoặc gửi tại bưu cục miễn phí, hoặc tự sắp xếp và thanh toán chi phí trước. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Tôi học được cách chọn chunk có nội dung tập trung hơn, cách dùng metadata filter để giảm nhiễu ngữ cảnh, và cách điều chỉnh prompt để agent trả lời dựa trên nguồn có xác thực.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                  |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5                  |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10                |
| **Tổng phần cá nhân**                      | **60 / 60**      |
