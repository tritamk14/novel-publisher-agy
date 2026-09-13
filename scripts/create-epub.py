#!/usr/bin/env python3
"""Generate EPUB from translated chapters."""

import os
import sys
from ebooklib import epub

def create_epub(translated_dir, output_path, title, author):
    book = epub.EpubBook()
    
    # Metadata
    book.set_identifier('tam-tuong-noi-huong-cang-preview')
    book.set_title(title)
    book.set_language('vi')
    book.add_author(author)
    
    # CSS
    style = '''
    body { font-family: Georgia, "Times New Roman", serif; line-height: 1.8; margin: 1em; }
    h1 { font-size: 1.5em; text-align: center; margin-bottom: 1.5em; color: #333; }
    h2 { font-size: 1.1em; text-align: center; color: #666; font-style: italic; margin-bottom: 2em; }
    p { text-indent: 2em; margin: 0.5em 0; }
    .footnote { font-size: 0.85em; color: #666; border-top: 1px solid #ccc; margin-top: 2em; padding-top: 1em; }
    .separator { text-align: center; margin: 1.5em 0; color: #999; }
    '''
    css = epub.EpubItem(uid="style", file_name="style/default.css", media_type="text/css", content=style)
    book.add_item(css)
    
    # Collect chapter files
    chapter_files = sorted([f for f in os.listdir(translated_dir) if f.endswith('.txt')])
    
    chapters = []
    spine = ['nav']
    toc = []
    
    for i, fname in enumerate(chapter_files):
        filepath = os.path.join(translated_dir, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Parse title from first line
        lines = content.split('\n')
        chapter_title = lines[0].strip() if lines else f"Chương {i+1}"
        
        # Convert text to HTML
        html_content = text_to_html(content, chapter_title)
        
        # Create epub chapter
        ch = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapter_{i+1:03d}.xhtml',
            lang='vi'
        )
        ch.content = html_content
        ch.add_item(css)
        
        book.add_item(ch)
        chapters.append(ch)
        spine.append(ch)
        toc.append(epub.Link(f'chapter_{i+1:03d}.xhtml', chapter_title, f'ch{i+1}'))
    
    # TOC and spine
    book.toc = toc
    book.spine = spine
    
    # Navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Write
    epub.write_epub(output_path, book)
    print(f"✅ EPUB created: {output_path}")
    print(f"   Chapters: {len(chapters)}")
    print(f"   Size: {os.path.getsize(output_path) / 1024:.1f} KB")

def text_to_html(text, title):
    """Convert plain text chapter to HTML."""
    lines = text.split('\n')
    html_parts = []
    
    first_line = True
    subtitle_done = False
    in_footnote = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Chapter title (first line)
        if first_line:
            html_parts.append(f'<h1>{escape_html(line)}</h1>')
            first_line = False
            continue
        
        # Subtitle (second line, usually in parentheses)
        if not subtitle_done and line.startswith('('):
            html_parts.append(f'<h2>{escape_html(line)}</h2>')
            subtitle_done = True
            continue
        subtitle_done = True
        
        # Separator lines
        if line in ['—————', '---', '***', '* * *']:
            html_parts.append('<p style="text-align:center;color:#999">✦ ✦ ✦</p>')
            continue
        
        # Footnote section
        if 'Chú thích' in line:
            in_footnote = True
            html_parts.append('<hr/>')
            html_parts.append(f'<p><strong>{escape_html(line)}</strong></p>')
            continue
        
        if line.startswith('(*)'):
            html_parts.append(f'<p><em>{escape_html(line)}</em></p>')
            continue
        
        # Normal paragraph
        html_parts.append(f'<p>{escape_html(line)}</p>')
    
    return '\n'.join(html_parts) if html_parts else '<p>&nbsp;</p>'

def escape_html(text):
    """Escape HTML special characters."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

if __name__ == '__main__':
    translated_dir = '/home/netnam2/novel-publisher/genres/ngon-tinh/tam-tuong-noi-huong-cang/translated'
    output_path = '/home/netnam2/novel-publisher/genres/ngon-tinh/tam-tuong-noi-huong-cang/tam-tuong-preview-5chuong.epub'
    
    create_epub(
        translated_dir=translated_dir,
        output_path=output_path,
        title='Tâm Tường (港岛心蔷) — Preview 5 Chương Đầu',
        author='Ứng Vũ Trúc (应雨竹) | Dịch: AI Novel Publisher'
    )
