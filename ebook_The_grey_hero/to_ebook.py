'''
    File    : to_ebook.py
    Author  : Jack V.
    Date    : 18 september 2025
    Purpose : Create epub from 2 txt and 2 jpg files
    Do      : Change variables : author, chapter_identifier and language
    Usage   : python3 to_ebook.py 'book.epub' 'cover.jpg' 'back_cover.jpg' 'book.txt' 'about_book.txt'
        - book.epub     : name of ebook to generate like The_grey_hero.epub
        - cover.jpg     : see elephant.jpg
        - back_cover    : see elephant.jpg
        - book.txt      : the book see The_grey_hero.txt 
        - about_book.txt: last chapter see The_grey_hero_about.txt
        
Format book.txt:

    Line 1 : Book title (appears above Contents)
    Line 2 : empty
    Line 3 : Book subtitle (is inserted below title)
    Line 4 : empty
    Line 5 ....
    at line 5 the chapters start and since I wrote this script for Dutch
        books each chapter starts with 'Hoofdstuk'
        When you want this script to work for your language, you want to
        find the variable chapter_identifier in the code below and change that.

Format about_book.txt:

    Line 1 : Title
    Line 2 : empty
    Next lines may contain:
    - your motivation to write the book
    - introductory information
    - cover information
    - publication details (author, publisher, ISBN, date, version)
    - acknowledgments
    - ....

To create the The_grey_hero.epub ebook:
    
    python3 to_ebook.py The_grey_hero.epub The_grey_hero.jpg The_grey_hero_mouse.jpg The_grey_hero.txt The_grey_hero_about.txt
    
'''
import sys, os, shutil, tempfile, zipfile
from ebooklib import epub

# Change author, chapter_identifier and language

print("\nDid you update the variables author, chapter_identifier and language?\n")
author='Jack V.'
chapter_identifier='Chapter' # 'Hoofdstuk' or 'Chapter' or whatever you use
language='en'

# 📗 Generate ebook
def txt_to_epub(basic_epub_path, cover, back_cover, txt_path, about_path):

    basic_epub_path = basic_epub_path.replace(".epub", "_basic.epub")
    
    # 📖 Read main text
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        print("Empty main text file.")
        return

    # Extract the 3 parts we need
    
    book_title = lines[0].strip()
    book_subtitle = lines[2].strip()
    content_lines = lines[4:]

    # Create the book
    
    book = epub.EpubBook()
    book.set_title(book_title)
    # We can not add the subtitle, at the end we use a function to do that.
    book.add_author(author)

    # 📕 First create the cover
    cover_data = open(cover, 'rb').read()
    cover_image = epub.EpubItem(uid="cover", file_name="images/cover.jpg", media_type="image/jpeg", content=cover_data)
    book.add_item(cover_image)
    book.set_cover(cover, cover_data)
    
    # Create a page with the cover
    
    cover_page = epub.EpubHtml(title='Coverpage', file_name='coverpage.xhtml', lang=language)
    cover_page.content = '<div style="text-align: center;"><img src="images/cover.jpg" alt="Cover"/></div>'
    book.add_item(cover_page)

    # Start to build the chapters
    chapters = [cover_page]
    content = ''
    chapter_title = ''
    chapter_count = 0

    # 📚 Process chapters
    for line in content_lines:
        line = line.strip()
        if line.startswith(chapter_identifier):
            if content:
                chapter = epub.EpubHtml(title=chapter_title, file_name=f'chap_{chapter_count}.xhtml', lang=language)
                chapter.content = f'<h2>{chapter_title}</h2>\n{content}'
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
        chapter.content = f'<h2>{chapter_title}</h2>\n{content}<hr width=75%>'
        book.add_item(chapter)
        chapters.append(chapter)

    if True:
        # 📙 Add the about_book.txt
        with open(about_path, 'r', encoding='utf-8') as f:
            about_lines = f.readlines()        
        about_content = ''
        about_title=about_lines[0]
        for line in about_lines[2:]:
            line = line.strip()
            if line == '':
                about_content += '<p></p>\n'
            else:
                about_content += f'<p>&nbsp;&nbsp;{line}</p>\n'

        about_chapter = epub.EpubHtml(title=about_title, file_name='about.xhtml', lang=language)
        about_chapter.content = '<center><h2>'+about_title+'</h2>' + about_content + '<hr width=75%></center>'
        book.add_item(about_chapter)
        chapters.append(about_chapter)

    back_cover_img = epub.EpubItem(
        uid="back_cover_img",
        file_name="images/back_cover.jpg",
        media_type="image/jpeg",
        content=open(back_cover, 'rb').read()
    )
    book.add_item(back_cover_img)

    back_cover_chapter = epub.EpubHtml(
        title='📘',
        file_name='back_cover.xhtml',
        lang=language
    )

    back_cover_chapter.content = '<div style="text-align: center; margin-top: 0em;"><img src="images/back_cover.jpg" alt="BackCover" style="max-width: 100%; height: auto;" /></div>'

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
    print(f"✅ Created intermediate EPUB '{basic_epub_path}' for: '{book_title}'")

    if True:
        update_nav_title(basic_epub_path, book_title, book_subtitle)
'''
To insert the subtitle between the title and the contents we need to:
- unpack the ebup which is a zip file
- update the file 'nav.xhtm'
- create a new zip file as the epub file 
'''
def update_nav_title(basic_epub_path, title, subtitle):
    
    # 📁 Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="epub_edit_")

    try:
        # 📦 Unpack EPUB in temporary directory
        with zipfile.ZipFile(basic_epub_path, 'r') as zin:
            zin.extractall(temp_dir)

        # 📄 Path to nav.xhtml
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

        # 📝 Read and update nav.xhtml
        with open(nav_path, 'r', encoding='utf-8') as f:
            nav_content = f.read()

        lookfor = f"<h2>{title}</h2>"
        changeto = f"{lookfor}\n<p><em>{subtitle}</em></p>"
        new_nav = nav_content.replace(lookfor, changeto)

        with open(nav_path, 'w', encoding='utf-8') as f:
            f.write(new_nav)

        # 📦 Create new EPUB
        epub_final_path = basic_epub_path.replace("_basic.epub", ".epub")
        with zipfile.ZipFile(epub_final_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, temp_dir)
                    zout.write(full_path, rel_path)

        print(f"✅ Updated nav.xhtml and saved final EPUB: '{epub_final_path}'")

    finally:
        # 🧹 Remove temporary directory and basic_epub_path
        shutil.rmtree(temp_dir)
        os.remove(basic_epub_path)
    
# 🖥️ Command-line interface
if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("\n\nUsage: python3 to_ebook.py 'book.epub' 'cover.jpg' 'back_cover.jpg' 'book.txt' 'about_book.txt'\n")
    else:
        txt_to_epub(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
