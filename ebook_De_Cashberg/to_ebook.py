'''
    File    : to_ebook.py
    Author  : Jack V.
    Date    : 18 september 2025
    Purpose : Create epub from 2 txt and 2 jpg files

    Usage   : python3 to_ebook.py book.epub cover.image back_cover.image book.txt about_book.txt
    
        - book.epub         : name of ebook to generate like The_grey_hero.epub
        - cover.image       : name of the cover image like cover.jpg or cover.png (1748 x 2480 for A5)
        - back_cover.image  : same but now for the back cover
        - book.txt          : the text for the book, see below for the format
        - about_book.txt    : the last chapter, see below for the format

Requirements:

    Do----- > : put this script with the your 2 txt files in a folder
                    change variables below : author, chapter_identifier and language
                
                put all images you want to use in your book in a subdirectory named images
                    this includes the cover pages
                    all images are imported in your ePub for you
                    use them in your txt file like:
        <div style="text-align: center;"><img src="images/spinning-coin.png" style="width:100px; height:100px; object-fit:contain; display:inline-block;"></img></div>

    Create--> : marker.png, a little png shown with the book subtitle on the contents page
                    put it in the images subdirectory
                    (you may modify the code below to skip this)

Format book.txt:

    Line 1 : Title:Book title
    Line 2 : Subtitle:Book subtitle
    Line 3 : Author:Your name
    Line 4 : Language:2 letter for the language like nl or en
    Line 5 : Identifiers: semicolon seperated list of chapter identifiers like : Inleiding;Hoofdstuk;Epiloog;... or Introduction;Chapter;Epilogue;....
    Line 6 : empty
    Line 7 : the chapters start with the chapter Identifier you specified above like :
            Chapter 1 The Beginning or Hoofdstuk 1 Het begin

    Note: each line starting with an '#' is treated as comment and not included in the ebook
        you can use this to keep notes in the text.

Format about_book.txt:

    Line 1 : Title
    Line 2 : empty
    Next lines may contain anything:
    - your motivation to write the book
    - introductory information
    - cover information
    - publication details (author, publisher, ISBN, date, version)
    - acknowledgments
    - ....

To create the The_grey_hero.epub ebook:
    
    python3 to_ebook.py The_grey_hero.epub cover.png back_cover.png The_grey_hero.txt about.txt
    
'''
import sys, os, shutil, tempfile, zipfile
from ebooklib import epub
from PIL import Image

# 📗 Generate ebook
def txt_to_epub(basic_epub_path, cover, back_cover, txt_path, about_path):
    basic_epub_path = basic_epub_path.replace(".epub", "_basic.epub")
    
    # 📖 Read main text
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        print("Empty main text file.")
        return

    book_title = lines[0].split(":", 1)[1].strip()
    book_subtitle = lines[1].split(":", 1)[1].strip()
    author = lines[2].split(":", 1)[1].strip()
    language = lines[3].split(":", 1)[1].strip()
    chapter_identifier = lines[4].split(":", 1)[1].strip()   # Chapter identifier like 'Hoofdstuk' or 'Chapter'
    chapter_identifiers = lines[4].split(":", 1)[1].strip()   # Chapter identifier like 'Hoofdstuk' or 'Chapter'
    content_lines = lines[6:]               # Line 6 etc : All chapters

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
    cover = f"./images/{cover}"
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
        if not line.startswith('#'):
            #if line.startswith(chapter_identifier):
            if line and  line.split()[0] in chapter_identifiers.split(';'):
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
    
    back_cover = f"./images/{back_cover}"
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
    
    # 📁 Add extra images from 'images/' subdirectory (png, jpg, gif except cover and back_cover)
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    excluded_files = [os.path.basename(cover), os.path.basename(back_cover)]
    image_dir = 'images'

    if os.path.isdir(image_dir):
        for file in os.listdir(image_dir):
            full_path = os.path.join(image_dir, file)
            if not os.path.isfile(full_path):
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions and file not in excluded_files:
                media_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif'
                }[ext]
                image_item = epub.EpubItem(
                    uid=f"img_{file}",
                    file_name=f"{image_dir}/{file}",
                    media_type=media_type,
                    content=open(full_path, 'rb').read()
                )
                book.add_item(image_item)
    else:
        print(f"⚠️ Subdirectory '{image_dir}' does not exist. No extra images added.")

    # 🧵 Create ebook
    epub.write_epub(basic_epub_path, book)
    print(f"\n✅ Created intermediate EPUB '{basic_epub_path}' for: '{book_title}'")

    update_nav_title(basic_epub_path, book_title, book_subtitle)
    print("")

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
        changeto = f"{lookfor}\n<div class=\"subtitle\"><img src='images/marker.png' alt='❄️' style='width:40px; height:40px; object-fit:contain; display:inline-block;'></img><em>{subtitle}</em></div>"
        # use the next line to skip the gif
        # changeto = f"{lookfor}\n<div class=\"subtitle\"><em>{subtitle}</em></div>"
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
        print(f"\nCreate '{sys.argv[1]}'\n")
        txt_to_epub(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
