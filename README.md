[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)

## License

This project, including all materials for the books, is licensed under the terms of the Unlicense.
<br>For more details, please refer to [UNLICENSE.md](UNLICENSE.md).
<br>For more information, please refer to <http://unlicense.org>.

---

# txt text to ePub ebook

As an ePub reader, I once wondered if I could create my own ebook. This curiosity led to the development of a simple script: one that takes two text files for the content, along with two JPG files for the cover and back cover, to generate a complete ePub book.

To create an ePub ebook, I needed text—a story—which I divided into chapters, which were then divided into paragraphs, and then I inserted some text in each paragraph. The result is a 30,000-word book about the life of an Alexander who, initially unaware that he is a descendant of the last Tsar, is kidnapped by his father, a Russian general, and manipulated by the president to become his successor. There are secret meetings, ambushes, exiles to Siberia, a marriage, a son, a dramatic ending and flashbacks to his youth and more. Well worth reading, I must say. Unfortunately it's in Dutch, but at least you can use the tool to create ebooks in any language.

I have created a small booklet in English as a demonstration, so you can get started quickly.

With the text available in a plain txt file, I created a Python script that I called <i><b>to_ebook.py</b></i> and put that in the same directory as my txt file.

Each book needs additional information, so I've added an additional text file which appears as the last chapter.
I also added front and back covers to complete the ebook.

I added an additional function to the script to insert a subtitle between the title and the table of contents.
This function extracts the ePub file, updates the page with the table of contents, and recreates the ePub file based on the extracted files. It also cleans up all extracted files.
This feature is an example of how you can place additional items in the ebook.

The Python script requires:

 - Python 3.x
 - required Python-modules:
    - ebooklib
    - sys
    - os
    - shutil
    - tempfile
    - zipfile
  - which you may need to install like:
    - pip install ebook

<hr width=75%>

There are some directories in this repository that start with 'ebook_' and these contain everything to create the ebook in it..

The directory ebook_De_Schaduw_van_de_Tsaar contains my first book, written in Dutch, and includes all the files needed to create the ePub ebook. You’ll find:

 - De_Schaduw_van_de_Tsaar.txt: The main text file
 - cover.jpg: The cover image
 - back_cover.jpg: The back cover image
 - Over_dit_boek.txt: The "About this book" chapter
 - to_ebook.py: the script to create the ePub file

To recreate the book, follow these steps:

 - Open a command prompt
 - Navigate to the directory
 - Run the following command:
```
python3 to_ebook.py De_Schaduw_van_de_Tsaar.epub cover.jpg back_cover.jpg De_Schaduw_van_de_Tsaar.txt Over_dit_boek.txt
```

The directory ebook_The_grey_hero contains a very short demo book, written in English, and includes all the files needed to create the ePub ebook. You’ll find:

 - The_grey_hero.txt: The main text file
 - The_grey_hero.jpg: The cover image
 - The_grey_hero_mouse.jpg: The back cover image
 - The_grey_hero_about.txt: The "About this book" chapter
 - to_ebook.py: the script to create the ePub file

To recreate the book, follow these steps:

 - Open a command prompt
 - Navigate to the directory
 - Run the following command:
```
python3 to_ebook.py The_grey_hero.epub The_grey_hero.jpg The_grey_hero_mouse.jpg The_grey_hero.txt The_grey_hero_about.txt
```
<hr width=75%>

When you look into both directories, and in the scripts, you will understand how you can use this to create your own ePub ebooks.

Creating Your Own ePub Ebook

To create your own ebook:

 - Create a directory with the required files.
 - Add a copy of the to_ebook.py script to the directory.
 - Edit the script to change the following settings:
    - author: your name
    - chapter_identifier: a unique marker for identifying chapters
    - language: a two-letter language code (e.g., "en" for English, "nl" for Dutch)

And to create 'your-ebook.epub' you run:
```
python3 to_ebook.py your-ebook.epub your-cover.jpg your-back-cover.jpg text-with-all-chapters.txt the-about-chapter.txt
```

Note that the formats for the input .txt files are described in the to_ebook.py script itself. I haven't included that information in this README, as you can always refer to the script for the necessary documentation. No need for the README as long as you have the script.

I hope this helps authors generate their ePub books from plain text files.

Jack
<hr width=75%>
