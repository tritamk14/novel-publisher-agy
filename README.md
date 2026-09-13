# 📚 Novel Publisher — Hệ Thống Dịch Truyện Chất Lượng Xuất Bản

Hệ thống dịch truyện Trung → Việt với chất lượng đạt chuẩn nhà xuất bản, sử dụng AI agent (Gemini/Antigravity).

## ✨ Tính Năng Nổi Bật

- **Character Registry** — Quản lý nhân vật chặt chẽ, không bao giờ nhầm lẫn
- **Ma trận xưng hô** — Xưng hô chính xác theo quan hệ & tiến trình tình cảm
- **Dịch tự nhiên** — Văn phong Việt mượt mà, không dịch word-by-word
- **Ngữ cảnh liên tục** — Tóm tắt chương trước, duy trì mạch truyện
- **Template theo thể loại** — Mỗi thể loại có quy chuẩn riêng

## 🏗️ Cấu Trúc Dự Án

```
novel-publisher/
├── genres/                          # Thể loại truyện
│   └── ngon-tinh/                   # Ngôn tình
│       └── _template/               # Template gốc (clone khi dịch truyện mới)
│           ├── README.md            # Hướng dẫn sử dụng template
│           ├── config.yaml          # Cấu hình truyện
│           ├── characters/          # Hồ sơ nhân vật
│           │   ├── registry.yaml    # Danh sách nhân vật
│           │   └── relationships.yaml # Ma trận xưng hô
│           ├── glossary/            # Bảng thuật ngữ
│           │   └── terms.yaml       # Ánh xạ thuật ngữ cố định
│           ├── context/             # Ngữ cảnh liên chương
│           │   └── chapter-summaries.yaml
│           ├── raw/                 # Bản gốc tiếng Trung
│           ├── translated/          # Bản dịch tiếng Việt
│           └── prompts/             # Prompt cho AI agent
│               ├── 01-extract-characters.md
│               ├── 02-translate-chapter.md
│               └── 03-review-chapter.md
├── shared/                          # Tài nguyên dùng chung
│   ├── rules/                       # Quy tắc dịch thuật
│   │   ├── xung-ho-guide.md         # Hướng dẫn xưng hô tiếng Việt
│   │   ├── ngon-tinh-conventions.md # Quy chuẩn thể loại ngôn tình
│   │   └── translation-standards.md # Tiêu chuẩn chất lượng dịch
│   └── examples/
│       └── xung-ho-matrix-example.yaml
└── scripts/                         # Script tiện ích
    └── new-project.sh               # Tạo dự án mới từ template
```

## 🚀 Cách Sử Dụng

### Bước 1: Tạo dự án mới

```bash
./scripts/new-project.sh ngon-tinh "ten-truyen-cua-ban"
```

### Bước 2: Cấu hình truyện

Chỉnh sửa `config.yaml` với thông tin truyện (tên, tác giả, bối cảnh, số chương...).

### Bước 3: Thêm bản gốc

Đặt các chương tiếng Trung vào thư mục `raw/`:
- `raw/chapter-001.txt`
- `raw/chapter-002.txt`
- ...

### Bước 4: Xây dựng hồ sơ nhân vật

Chạy agent với prompt `01-extract-characters.md` để tự động quét và trích xuất nhân vật:

```
Đọc và thực thi file prompts/01-extract-characters.md
```

→ Agent sẽ quét raw chapters, tạo `characters/registry.yaml` và `characters/relationships.yaml`.

### Bước 5: Kiểm tra nhân vật

Review file `registry.yaml` và `relationships.yaml`. Điều chỉnh nếu cần (tên dịch, xưng hô...).

### Bước 6: Dịch truyện

Chạy agent (khuyến nghị dùng `/goal` để chạy liên tục) với prompt `02-translate-chapter.md`:

```
Đọc và thực thi file prompts/02-translate-chapter.md
```

→ Agent dịch từng chương, lưu vào `translated/`, cập nhật `chapter-summaries.yaml`.

### Bước 7: Kiểm tra chất lượng

Chạy agent với prompt `03-review-chapter.md` để soát lỗi:

```
Đọc và thực thi file prompts/03-review-chapter.md
```

## 🎯 Triết Lý Dịch Thuật

> **Dịch cho NGƯỜI ĐỌC, không dịch cho TỪ ĐIỂN.**

- Mỗi câu phải đọc như thể viết bằng tiếng Việt từ đầu
- Thành ngữ Trung → tương đương Việt hoặc diễn đạt tự nhiên
- Giữ CẢM XÚC và NHỊP VĂN, không chỉ giữ CHỮ
- Xưng hô phải phản ánh đúng mối quan hệ và cảm xúc

## 📋 Thể Loại Được Hỗ Trợ

| Thể loại | Trạng thái | Ghi chú |
|-----------|-----------|---------|
| Ngôn tình | ✅ Sẵn sàng | Hiện đại & Cổ đại |
| Tiên hiệp | 🔜 Sắp tới | |
| Huyền huyễn | 🔜 Sắp tới | |
| Đô thị | 🔜 Sắp tới | |
