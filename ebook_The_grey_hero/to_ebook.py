import sys, os, shutil, tempfile, zipfile
from ebooklib import epub
from PIL import Image

# Change author, chapter_identifier and language
author='Jack V.'
chapter_identifier='Chapter' # 'Hoofdstuk' or 'Chapter' or 'Kapitel' or 'Any_Other_String_Without_Spaces'
language='nl' # 'nl' or 'en' or any other language

# 📗 Generate ebook
def txt_to_epub(basic_epub_path, cover, back_cover, txt_path, about_path):
    basic_epub_path = basic_epub_path.replace(".epub", "_basic.epub")
    
    # 📖 Read main text
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        print("Empty main text file.")
        return

    book_title = lines[0].strip()       # Line 1 : Book title
    book_subtitle = lines[2].strip()    # Line 3 : Book subtitle
    content_lines = lines[4:]           # Line 5 etc : All chapters

    # 📗 Create the book
    book = epub.EpubBook()
    
    book.set_title(book_title)
    book.add_author(author)
    book.set_language(language)

    # You can add any metadata to content.opf
#    book.add_metadata('DC', 'publisher', 'Your name / Publisher')
#    book.add_metadata('DC', 'date', '2025-09-25')
#    book.add_metadata('DC', 'identifier', 'urn:uuid:...')
#    book.add_metadata('DC', 'whatever', 'value for whatever')

    # Check cover file format and extension
    image = Image.open(cover)
    image_format = image.format.lower()
    image_extension = cover.split(".")[-1].lower()

    # Mappingvan format -> extensions
    allowed = {
        "jpeg": ["jpg", "jpeg"],
        "png": ["png"],
        "gif": ["gif"],
        "svg": ["svg"]
    }

    if image_format not in allowed or image_extension not in allowed[image_format]:
        print(f"ERROR: Cover '{cover}' format '{image_format}' does not match extension '.{image_extension}'!")
        return

    # 📕 First create the cover
    
    cover_data = open(cover, 'rb').read()
    book.set_cover("cover."+image_extension, cover_data)
    
    # 📘 Create a page with the cover
    cover_page = epub.EpubHtml(title='Coverpage', file_name='coverpage.xhtml', lang=language)
    cover_page.content = '<div style="text-align: center;"><img src="cover.'+image_extension+'" alt="Cover"/></div>'
    book.add_item(cover_page)

    # 📚 Initialise to create the chapters
    chapters = [cover_page]
    content = ''
    chapter_title = ''
    chapter_count = 0

    # 📚 Process chapters
    for line in content_lines:
        line = line.strip()
        if line.startswith(chapter_identifier):
            print(line)
            if content:
                chapter = epub.EpubHtml(title=chapter_title, file_name=f'chap_{chapter_count}.xhtml', lang=language)
                chapter.content = f'<h2><i>{chapter_title}</i></h2>\n{content}'
                book.add_item(chapter)
                chapters.append(chapter)
                content = ''
            chapter_title = line
            chapter_count += 1
        elif line == '':
            content += '<p></p>\n'
        else:
            content += f'<p>&nbsp;&nbsp;{line}</p>\n'
    
    # 📘 Add last chapter from the book.txt file
    if content:
        chapter = epub.EpubHtml(title=chapter_title, file_name=f'chap_{chapter_count}.xhtml', lang=language)
        chapter.content = f'<h2><i>{chapter_title}</i></h2>\n{content}<hr style="width:75%;" />'
        book.add_item(chapter)
        chapters.append(chapter)

    # 📙 Add the about_book.txt
    with open(about_path, 'r', encoding='utf-8') as f:
        about_lines = f.readlines()
    about_content = ''
    about_title = about_lines[0].strip()
    for line in about_lines[2:]:
        line = line.strip()
        if line == '':
            about_content += '<p></p>\n'
        else:
            about_content += f'<p>&nbsp;&nbsp;{line}</p>\n'

    about_chapter = epub.EpubHtml(title=about_title, file_name='about.xhtml', lang=language)
    about_chapter.content = '<div style="text-align:center;"><h2>'+about_title+'</h2>' + about_content + '<hr style="width:75%;" /></div>'
    book.add_item(about_chapter)
    chapters.append(about_chapter)

    # Check back cover file format and extension
    image = Image.open(back_cover)
    image_format = image.format.lower()
    image_extension = back_cover.split(".")[-1].lower()

    if image_format not in allowed or image_extension not in allowed[image_format]:
        print(f"ERROR: Back cover '{back_cover}' format '{image_format}' does not match extension '.{image_extension}'!")
        return

    # 📗 Back cover
    image = Image.open(back_cover)
    # Mapping format to media types
    mime_types = {
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        'tiff': 'image/tiff',
    }
    image_type = mime_types.get(image_format, 'application/octet-stream')  # Default is a general binary stream

    back_cover_img = epub.EpubItem(
        uid="back_cover_img",
        file_name="images/back_cover."+image_extension,
        media_type=image_type,
        content=open(back_cover, 'rb').read()
    )
    book.add_item(back_cover_img)

    back_cover_chapter = epub.EpubHtml(
        title='Back Cover',
        file_name='back_cover.xhtml',
        lang=language
    )
    back_cover_chapter.content = '<div style="text-align: center;"><img src="images/back_cover.'+image_extension+'" alt="BackCover" style="max-width:100%; height:auto;" /></div>'
    book.add_item(back_cover_chapter)
    chapters.append(back_cover_chapter)

    # 📑 TOC and spine
    book.toc = chapters[1:]  # Skip cover page
    book.spine = [chapters[0], 'nav'] + chapters[1:]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 🎨 Add some CSS
    style = '''
    body { font-family: serif; }
    h2 { font-size: 1.5em; margin-top: 1em; }
    p { text-indent: 2ch; line-height: 1.4; }
    '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # 🧵 Create ebook
    epub.write_epub(basic_epub_path, book)
    print(f"\n✅ Created intermediate EPUB '{basic_epub_path}' for: '{book_title}'")

    update_nav_title(basic_epub_path, book_title, book_subtitle)

def update_nav_title(basic_epub_path, title, subtitle):
    temp_dir = tempfile.mkdtemp(prefix="epub_edit_")

    try:
        with zipfile.ZipFile(basic_epub_path, 'r') as zin:
            zin.extractall(temp_dir)

        nav_path = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('nav.xhtml'):
                    nav_path = os.path.join(root, file)
                    break
            if nav_path:
                break

        if not nav_path:
            print("nav.xhtml missing.")
            return

        with open(nav_path, 'r', encoding='utf-8') as f:
            nav_content = f.read()

        lookfor = f"<body>"
        changeto = f"{lookfor}\n<div class=\"subtitle\"><em>{subtitle}</em></div>"
        new_nav = nav_content.replace(lookfor, changeto)

        with open(nav_path, 'w', encoding='utf-8') as f:
            f.write(new_nav)

        epub_final_path = basic_epub_path.replace("_basic.epub", ".epub")
        repack_epub(temp_dir, epub_final_path)
        print(f"✅ Updated nav.xhtml and saved final EPUB: '{epub_final_path}'")

    finally:
        shutil.rmtree(temp_dir)
        os.remove(basic_epub_path)

def repack_epub(folder, epub_path):
    mimetype_path = os.path.join(folder, "mimetype")
    with zipfile.ZipFile(epub_path, 'w') as zout:
        # mimetype must be first and uncompressed
        zout.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)
        # all other files
        for root, dirs, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder)
                if rel_path == "mimetype":
                    continue
                zout.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)

# 🖥️ Command-line interface
if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("\n\nUsage: python3 to_ebook.py 'book.epub' 'cover.jpg' 'back_cover.jpg' 'book.txt' 'about_book.txt'\n")
    else:
        print(f"\n\nCreate '{sys.argv[1]}' for '{author}' in language '{language}' using chapter identifier '{chapter_identifier}'\n")
        txt_to_epub(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
