#!/usr/bin/env bash
# ============================================================
# new-project.sh — Tạo dự án dịch truyện mới từ template
# Usage: ./scripts/new-project.sh <genre> <project-name>
# Example: ./scripts/new-project.sh ngon-tinh "tham-tinh-tong-tai"
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Validation ---
if [[ $# -lt 2 ]]; then
    echo "❌ Thiếu tham số!"
    echo ""
    echo "Cách dùng: ./scripts/new-project.sh <thể-loại> <tên-dự-án>"
    echo ""
    echo "Thể loại có sẵn:"
    for genre_dir in "$PROJECT_ROOT/genres"/*/; do
        if [[ -d "$genre_dir/_template" ]]; then
            genre_name=$(basename "$genre_dir")
            echo "  - $genre_name"
        fi
    done
    echo ""
    echo "Ví dụ: ./scripts/new-project.sh ngon-tinh \"tham-tinh-tong-tai\""
    exit 1
fi

GENRE="$1"
PROJECT_NAME="$2"
TEMPLATE_DIR="$PROJECT_ROOT/genres/$GENRE/_template"
TARGET_DIR="$PROJECT_ROOT/genres/$GENRE/$PROJECT_NAME"

# Check template exists
if [[ ! -d "$TEMPLATE_DIR" ]]; then
    echo "❌ Không tìm thấy template cho thể loại: $GENRE"
    echo "   Đường dẫn: $TEMPLATE_DIR"
    exit 1
fi

# Check target doesn't exist
if [[ -d "$TARGET_DIR" ]]; then
    echo "❌ Dự án đã tồn tại: $TARGET_DIR"
    echo "   Hãy chọn tên khác hoặc xóa dự án cũ."
    exit 1
fi

# --- Create project ---
echo "📦 Tạo dự án mới: $PROJECT_NAME (thể loại: $GENRE)"
cp -r "$TEMPLATE_DIR" "$TARGET_DIR"

# Remove .gitkeep files
find "$TARGET_DIR" -name ".gitkeep" -delete 2>/dev/null || true

echo ""
echo "✅ Tạo dự án thành công!"
echo ""
echo "📁 Đường dẫn: $TARGET_DIR"
echo ""
echo "📋 Các bước tiếp theo:"
echo "   1. Chỉnh sửa config.yaml với thông tin truyện"
echo "   2. Đặt các chương gốc vào thư mục raw/"
echo "      (đặt tên: chapter-001.txt, chapter-002.txt, ...)"
echo "   3. Chạy agent để trích xuất nhân vật:"
echo "      → Đọc và thực thi file prompts/01-extract-characters.md"
echo "   4. Review characters/registry.yaml và relationships.yaml"
echo "   5. Chạy agent để dịch (khuyến nghị dùng /goal):"
echo "      → Đọc và thực thi file prompts/02-translate-chapter.md"
echo ""
