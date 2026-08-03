from src.chunking import compute_similarity
from src.embeddings import MockEmbedder


def main() -> None:
    embed = MockEmbedder()
    pairs = [
        (
            "Yêu cầu hoàn trả sản phẩm chưa sử dụng",
            "Hướng dẫn hoàn tiền khi trả hàng",
        ),
        (
            "Cách đăng ký bán hàng",
            "Quy định kích thước hình ảnh",
        ),
        (
            "Phí vận chuyển trả hàng",
            "Chi phí hoàn trả và bồi thường",
        ),
        (
            "Cách đổi mật khẩu",
            "Lịch sử giao dịch của tôi",
        ),
        (
            "Quy trình khi hàng bị hỏng",
            "Chính sách bảo hành sản phẩm",
        ),
    ]

    print("Mock similarity scores using MockEmbedder:\n")
    for index, (a, b) in enumerate(pairs, start=1):
        score = compute_similarity(embed(a), embed(b))
        print(f"{index}. {score:.6f} | {a} | {b}")


if __name__ == "__main__":
    main()
