# Thiết kế hoàn thiện Lab 7 của Trần Chí Hiển

## Mục tiêu

Hoàn thiện toàn bộ thư mục `TranChiHien_2A202601162`: triển khai các TODO trong gói `src`, đạt mức kiểm thử tốt nhất mà môi trường cho phép, hoàn tất báo cáo cá nhân và bổ sung phần chiến lược của Trần Chí Hiển vào báo cáo nhóm.

## Phạm vi

- Hoàn thiện `SentenceChunker`, `RecursiveChunker`, cosine similarity và bộ so sánh chiến lược.
- Hoàn thiện kho vector trong bộ nhớ, gồm thêm, tìm kiếm, lọc metadata, đếm và xóa tài liệu.
- Hoàn thiện `KnowledgeBaseAgent` theo luồng RAG đơn giản.
- Dùng `RecursiveChunker(chunk_size=500)` làm chiến lược cá nhân của Trần Chí Hiển.
- Dùng các benchmark query, gold answer và số liệu retrieval bằng Gemini Embedding 2 đã được nhóm ghi nhận trong `report/REPORT_NHOM.md`; không chạy lại dịch vụ Gemini khi không có khóa tương ứng.
- Hoàn tất `REPORT_CANHAN.md`, checklist `exercises.md` và mục Thành viên 5 trong `report/REPORT_NHOM.md`.
- Không sửa phần riêng của thành viên khác và không ghi credential vào file hoặc commit.

## Thiết kế mã nguồn

### Chunking

`SentenceChunker` tách tại dấu kết thúc câu rồi gom tối đa số câu được cấu hình. `RecursiveChunker` ưu tiên ranh giới đoạn, dòng, câu và từ; phần vẫn vượt kích thước sẽ tiếp tục được tách bằng separator tiếp theo, cuối cùng cắt cứng theo `chunk_size`. Bộ so sánh chạy ba chunker và trả về danh sách chunk, số lượng và độ dài trung bình.

### Vector store

Mỗi `Document` được chuẩn hóa thành record có ID lưu trữ duy nhất, ID tài liệu, nội dung, metadata và embedding. Store dùng bộ nhớ làm nguồn dữ liệu chính để kết quả ổn định trong lab; tìm kiếm tính cosine/dot product trên embedding đã chuẩn hóa, sắp xếp giảm dần và giới hạn `top_k`. Lọc metadata diễn ra trước khi xếp hạng. Xóa dựa trên `metadata.doc_id`, đồng thời hỗ trợ trường hợp tài liệu chưa có khóa này bằng ID gốc.

### Agent

Agent lấy `top_k` chunk, ghép nội dung cùng metadata nguồn vào context, thêm câu hỏi và chỉ dẫn trả lời dựa trên context, sau đó gọi `llm_fn`. Khi store rỗng, prompt vẫn nêu rõ không có ngữ cảnh để LLM không suy diễn từ tài liệu không tồn tại.

## Dữ liệu và báo cáo

Chiến lược cá nhân dùng `RecursiveChunker(chunk_size=500)` vì dữ liệu chính sách có cấu trúc điều/khoản và ranh giới đoạn rõ ràng. Báo cáo cá nhân sử dụng năm câu hỏi chung của nhóm. Các điểm retrieval Gemini đã có trong báo cáo nhóm được dẫn lại với ghi chú rõ đây là kết quả benchmark chung, tránh mô tả như một lần chạy mới. Phần warm-up, cách tiếp cận, kết quả test, phân tích và tự đánh giá được điền bằng nội dung có thể kiểm chứng từ code và dữ liệu hiện có.

## Kiểm thử và xử lý lỗi

Các hành vi mới được phát triển theo chu trình test thất bại trước, triển khai tối thiểu và chạy lại. Bộ `tests/test_solution.py` được chạy với `LAB_SOLUTION_PACKAGE=TranChiHien_2A202601162.src`. Bổ sung test tập trung cho validation, edge case chunking, lọc/xóa và prompt agent nếu bộ test chung chưa bao phủ. Nếu lỗi còn lại do dependency hoặc môi trường, báo cáo ghi nguyên nhân và số test thực tế; không bịa trạng thái 42/42.

## Git và bàn giao

Mỗi nhóm thay đổi hợp lý được commit với thông điệp rõ ràng. Trước khi push sẽ quét token/API key, chạy test và kiểm tra diff. Push vào nhánh `main` của remote hiện có bằng credential chỉ cấp qua tiến trình Git, không đưa token vào URL đã lưu, file cấu hình hoặc lịch sử commit.
