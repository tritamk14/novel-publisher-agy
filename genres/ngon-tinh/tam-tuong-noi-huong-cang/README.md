# 📖 Template Ngôn Tình — Hướng Dẫn Sử Dụng

Template dịch truyện ngôn tình (Trung → Việt) với chất lượng xuất bản.

## Quy Trình Dịch

### Giai đoạn 1: Chuẩn bị

1. **Cấu hình** — Chỉnh `config.yaml` với thông tin truyện
2. **Bản gốc** — Đặt các chương tiếng Trung vào `raw/`
   - Đặt tên: `chapter-001.txt`, `chapter-002.txt`, ...
   - Mỗi file = 1 chương
   - Encoding: UTF-8

### Giai đoạn 2: Xây dựng nhân vật

3. **Trích xuất** — Chạy agent với `prompts/01-extract-characters.md`
   - Agent quét 5-10 chương đầu
   - Tạo `characters/registry.yaml` (danh sách nhân vật)
   - Tạo `characters/relationships.yaml` (ma trận xưng hô)

4. **Review** — Kiểm tra và điều chỉnh:
   - Tên dịch có đúng không?
   - Xưng hô có phù hợp không?
   - Quan hệ có chính xác không?
   - Bổ sung nhân vật bị thiếu

### Giai đoạn 3: Dịch thuật

5. **Dịch** — Chạy agent với `prompts/02-translate-chapter.md`
   - Khuyến nghị dùng `/goal` để agent chạy liên tục
   - Agent dịch từng chương, lưu vào `translated/`
   - Tự động cập nhật `context/chapter-summaries.yaml`
   - Tự động tra cứu `characters/` và `glossary/` khi dịch

### Giai đoạn 4: Kiểm tra

6. **Review** — Chạy agent với `prompts/03-review-chapter.md`
   - Kiểm tra nhất quán xưng hô
   - Kiểm tra tên nhân vật
   - Kiểm tra văn phong tự nhiên
   - Đánh dấu đoạn cần sửa

## Cấu Trúc Thư Mục

```
├── config.yaml              # Cấu hình truyện (BẮT BUỘC chỉnh)
├── characters/
│   ├── registry.yaml        # Hồ sơ nhân vật (agent tạo, user review)
│   └── relationships.yaml   # Ma trận xưng hô (agent tạo, user review)
├── glossary/
│   └── terms.yaml           # Thuật ngữ cố định (agent + user bổ sung)
├── context/
│   └── chapter-summaries.yaml # Tóm tắt chương (agent tự cập nhật)
├── raw/                     # Bản gốc tiếng Trung (user đặt vào)
├── translated/              # Bản dịch tiếng Việt (agent tạo)
└── prompts/                 # Prompt cho agent (KHÔNG chỉnh)
```

## Lưu Ý Quan Trọng

- **KHÔNG sửa file trong `prompts/`** trừ khi bạn hiểu rõ hệ thống
- Luôn review `registry.yaml` sau khi agent trích xuất — đây là "bộ não" của hệ thống
- Nếu phát hiện lỗi xưng hô, sửa `relationships.yaml` rồi dịch lại chương bị lỗi
- Có thể bổ sung thuật ngữ vào `glossary/terms.yaml` bất cứ lúc nào
