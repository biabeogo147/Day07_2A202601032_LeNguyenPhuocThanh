# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Kim Tính
**Nhóm:** Những con vịt bầu
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng oán độ tương tự (5) + Kết quả truy xuất của tôi (10).điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau. Trong bài toán xử lý văn bản, điều này thường cho thấy hai câu có nội dung hoặc ý nghĩa gần nhau, dù chúng không nhất thiết dùng cùng từ ngữ.

**Ví dụ có độ tương tự CAO:**
- Câu A: “Người mua muốn trả lại sản phẩm bị lỗi.”
- Câu B: “Khách hàng yêu cầu hoàn trả hàng hóa không đúng mô tả.”
- Tại sao tương đồng:Hai câu cùng nói về nhu cầu đổi trả một sản phẩm có vấn đề.

**Ví dụ có độ tương tự THẤP:**
- Câu A: “Người bán phải mô tả sản phẩm chính xác.”
- Câu B: “Python là một ngôn ngữ lập trình bậc cao.”
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau: thương mại điện tử và lập trình.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity thường được ưu tiên hơn khoảng cách Euclid vì nó tập trung vào hướng của vector thay vì độ lớn. Do đó, kết quả ít bị ảnh hưởng bởi độ dài văn bản hoặc độ lớn khác nhau của embedding.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> 
```text
step = chunk_size - overlap = 500 - 50 = 450
```

Số chunk được tính bằng:

```text
ceil((10000 - 500) / 450) + 1 = ceil(21,11) + 1 = 23 chunks
```



**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Nếu tăng overlap lên 100 thì bước nhảy còn 400 ký tự:

```text
ceil((10000 - 500) / 400) + 1 = ceil(23,75) + 1 = 25 chunks
```
> Số chunk tăng từ 23 lên 25. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk và hạn chế việc một ý quan trọng bị cắt rời, nhưng làm tăng lượng dữ liệu lưu trữ và chi phí tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi loại bỏ khoảng trắng thừa và trả về danh sách rỗng nếu đầu vào rỗng. Sau đó, biểu thức chính quy `(?<=[.!?])\s+` được dùng để tách câu tại khoảng trắng đứng sau dấu chấm, dấu chấm than hoặc dấu hỏi; các câu được gom theo `max_sentences_per_chunk`

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt các separator theo độ ưu tiên: đoạn văn, xuống dòng, dấu chấm, khoảng trắng và cuối cùng là ký tự. Trường hợp cơ sở là đoạn hiện tại đã nhỏ hơn `chunk_size`; nếu không còn separator phù hợp, văn bản được cắt trực tiếp theo kích thước cố định. Sau khi tách, các mảnh nhỏ liền kề được ghép lại nếu tổng độ dài không vượt quá giới hạn.


### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được chuyển thành một record gồm nội dung, metadata và embedding. Khi ChromaDB không khả dụng, record được lưu trong danh sách trên bộ nhớ; tìm kiếm tạo embedding của query, tính tích vô hướng với từng vector, sắp xếp score giảm dần và trả về tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Metadata được lọc trước khi tính độ tương tự để chỉ tìm trong tập ứng viên phù hợp. Khi tạo record, `Document.id` được giữ trong `metadata["doc_id"]`; nhờ đó `delete_document` có thể xóa đúng tất cả chunk thuộc một tài liệu và trả về `True` khi có dữ liệu bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Phương thức answer trước tiên tìm kiếm top_k đoạn văn liên quan nhất với câu hỏi từ EmbeddingStore. Nội dung các đoạn được nối lại và đưa vào phần Context của prompt, sau đó prompt bổ sung câu hỏi cùng yêu cầu trả lời dựa trên ngữ cảnh đã cung cấp. Cuối cùng, prompt được truyền cho llm_fn để sinh câu trả lời, giúp hạn chế việc mô hình trả lời ngoài dữ liệu truy xuất.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
(.venv) PS C:\Users\LENOVO\Desktop\LAB\lab 7\DAY07_2A202601560__LeKimTinh> pytest tests/ -v 
============================================================================ test session starts =============================================================================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\LENOVO\Desktop\LAB\lab 7\DAY07_2A202601560__LeKimTinh\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\LENOVO\Desktop\LAB\lab 7\DAY07_2A202601560__LeKimTinh
collected 42 items                                                                                                                                                            

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                                                   [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                                            [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                                                     [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                                                      [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                                                           [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                                                           [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                                                 [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                                                  [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                                                [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                                                  [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                                                  [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                                             [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                                                         [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                                                   [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                                                          [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                                              [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                                                        [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                                              [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                                                  [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                                                    [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                                                      [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                                            [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                                                 [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                                                   [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                                                       [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                                                    [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                                             [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                                            [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                                                       [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                                                   [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                                              [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                                                  [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                                                        [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                                                  [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                                               [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                                             [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                                            [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                                                [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                                                           [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                                                    [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                                                          [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                                              [100%]

============================================================================= 42 passed in 0.15s =============================================================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-------|-------|---------|--------------:|-------|
| 1 | Người mua muốn đổi trả sản phẩm bị lỗi. | Khách hàng yêu cầu hoàn tiền vì hàng bị hỏng. | Cao | 0.0697 | Không |
| 2 | Người bán phải mô tả sản phẩm chính xác. | Thông tin đăng bán phải đúng với tình trạng hàng. | Cao | 0.2574 | Không (mức trung bình) |
| 3 | Sản phẩm bị cấm không được đăng bán. | Python là một ngôn ngữ lập trình. | Thấp | 0.0391 | Đúng |
| 4 | Người mua cần cung cấp bằng chứng hàng bị lỗi. | Khách hàng gửi hình ảnh để yêu cầu đổi trả. | Cao | 0.1325 | Không |
| 5 | Người bán phải phản hồi yêu cầu đổi trả. | Hôm nay thời tiết có nhiều mây. | Thấp | 0.0971 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Kết quả bất ngờ nhất là cặp 1: hai câu có ý nghĩa gần giống nhau nhưng cosine similarity chỉ đạt 0.0697. Nguyên nhân là chương trình đang sử dụng `MockEmbedder`, vốn sinh vector dựa trên mã băm và không thực sự hiểu ý nghĩa của văn bản; vì vậy kết quả chỉ phù hợp để kiểm tra chương trình, không phản ánh chính xác độ tương đồng ngữ nghĩa. Với mô hình embedding thực, các câu gần nghĩa thường có điểm tương tự cao hơn.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Tôi sử dụng `RecursiveChunker` với `chunk_size=500` và mô hình embedding đa ngôn ngữ `paraphrase-multilingual-MiniLM-L12-v2`. Mỗi câu hỏi được truy xuất tối đa ba chunk; riêng câu 4 sử dụng `metadata_filter={"customer_role": "buyer"}`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | Shopee có hỗ trợ đổi hàng không? Nếu hàng có vấn đề thì người mua phải làm gì? | Nội dung về hỗ trợ phí trả hàng khi dùng đơn vị vận chuyển hỏa tốc và trường hợp phí không được hoàn lại | 0.7160 | Không; top-3 không chứa quy định Shopee chưa hỗ trợ đổi hàng | Agent không thể trả lời đúng vì ngữ cảnh truy xuất không chứa chính sách đổi hàng |
| 2 | Thời hạn gửi yêu cầu trả hàng/hoàn tiền trên Shopee là bao lâu? | Người mua vẫn có thể gửi yêu cầu sau khi bấm “Đã nhận được hàng” nếu còn trong thời hạn 15 ngày | 0.8870 | Có, nhưng chưa đầy đủ các trường hợp | Agent có thể trả lời thời hạn thông thường là 15 ngày, nhưng thiếu mốc 24 giờ đối với thực phẩm tươi sống/đông lạnh và 20 ngày đối với một số đơn người bán tự vận chuyển |
| 3 | Người mua cần gửi yêu cầu trả hàng bằng cách nào trên ứng dụng Shopee? | Top-1 nói về quyền của người bán khi nhận được yêu cầu trả hàng/hoàn tiền | 0.7871 | Top-1 không liên quan trực tiếp; top-3 có chunk hướng dẫn đúng | Dựa vào chunk top-3, Agent có thể hướng dẫn vào **Tôi → Trò Chuyện Với Shopee → Khiếu nại trả hàng hoàn tiền**, chọn đơn, cung cấp lý do và bằng chứng rồi gửi yêu cầu |
| 4 | Trong các tài liệu dành cho người mua, người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào? | Nội dung tổng quát về quyền và nghĩa vụ của các bên trong quá trình trả hàng/hoàn tiền | 0.7656 | Không; top-3 không chứa Điều 7.1 về trách nhiệm chi phí của người bán | Agent không thể trả lời đầy đủ trường hợp người bán phải chịu phí vì chunk quy định trực tiếp không xuất hiện trong top-3 |
| 5 | Có những phương thức gửi hàng hoàn trả nào và chi phí ra sao? | Nội dung về lưu ý khi đơn vị vận chuyển đến lấy hàng và số lần lấy hàng tối đa | 0.5906 | Có một phần; top-2 và top-3 chứa thông tin liên quan đến phí | Agent có thể trả lời rằng lấy hàng tại nhà và trả tại bưu cục được miễn phí; nếu tự sắp xếp thì người mua thanh toán trước và cần lưu hóa đơn để được hỗ trợ hoàn phí |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **3/5**

Các câu 2, 3 và 5 có ít nhất một chunk liên quan trong top-3. Câu 1 và câu 4 không truy xuất được chunk chứa trực tiếp gold answer, vì vậy được xem là hai trường hợp thất bại.

**Phân tích trường hợp lỗi**

Câu 1 truy xuất nhầm nội dung về phí vận chuyển hoàn trả thay vì quy định “Shopee chưa hỗ trợ đổi hàng”. Nguyên nhân có thể do câu hỏi chứa đồng thời nhiều ý như “đổi hàng”, “hàng có vấn đề” và “người mua phải làm gì”, trong khi corpus lặp lại nhiều từ khóa liên quan đến trả hàng và hoàn tiền. Có thể cải thiện bằng cách tách câu hỏi thành câu ngắn hơn hoặc chia tài liệu theo từng điều khoản và gắn metadata `subtopic`.

Câu 4 cũng thất bại dù đã dùng metadata filter. Nguyên nhân là toàn bộ tài liệu hiện đều được gắn `customer_role: buyer`, nên phép lọc không thực sự thu hẹp tập ứng viên; đồng thời nội dung Điều 7.1 bị tách thành một chunk không được xếp trong top-3. Nhóm nên gắn `customer_role: both` cho tài liệu chính sách áp dụng cho cả người mua và người bán, bổ sung metadata `subtopic: return-shipping-cost`, hoặc chia chunk theo tiêu đề điều khoản.

**Điều hay nhất tôi học được từ thành viên khác/nhóm khác qua demo**

Điều quan trọng nhất tôi học được là mô hình embedding tốt vẫn chưa bảo đảm kết quả chính xác nếu cấu trúc chunk và metadata chưa phù hợp. Việc chia văn bản theo tiêu đề, điều khoản và gắn metadata chi tiết có thể giúp giữ trọn câu trả lời chuẩn, đồng thời làm cho metadata filter thực sự thu hẹp không gian tìm kiếm thay vì chỉ đáp ứng yêu cầu về hình thức.
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
