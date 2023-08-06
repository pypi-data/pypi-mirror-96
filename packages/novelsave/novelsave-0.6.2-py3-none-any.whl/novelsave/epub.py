import hashlib
from pathlib import Path

from ebooklib import epub
from yattag import Doc

from .models import MetaData
from .tools import StringTools


class NovelEpub:
    def __init__(self, novel, cover, chapters, save_path):
        self.novel = novel
        self.cover = cover
        self.chapters = chapters
        self.save_path = save_path

    def create(self):
        # attribute validation
        if not self.chapters:
            raise ValueError("'chapters' cannot be 'None'")

        # prepare data
        self.chapters.sort(key=lambda c: c.index)

        book = epub.EpubBook()

        # metadata
        book.set_identifier(str(self.novel.id if hasattr(self.novel, 'id') else hashlib.md5(self.novel.title.encode('utf-8')).hexdigest()))
        book.set_title(self.novel.title)
        book.set_language(self.novel.lang)
        book.add_author(self.novel.author)

        if self.novel.synopsis:
            book.add_metadata(MetaData.DEFAULT_NAMESPACE, 'synopsis', self.novel.synopsis)

        for data in self.novel.meta:
            book.add_metadata(data['namespace'], data['name'], data['value'], data['others'])

        book.add_metadata(MetaData.DEFAULT_NAMESPACE, 'source', self.novel.url)

        # cover
        if self.cover.exists() and self.cover.is_file():
            with self.cover.open('rb') as f:
                book.set_cover('cover.jpg', f.read())

        # create chapters
        book_chapters = {}
        for chapter in self.chapters:
            epub_chapter = self._epub_chapter(chapter)
            book.add_item(epub_chapter)

            try:
                volume = tuple(chapter.volume) or (-1, '_default')
            except (AttributeError, TypeError, IndexError):
                volume = (-1, '_default')

            if volume in book_chapters.keys():
                book_chapters[volume].append(epub_chapter)
            else:
                book_chapters[volume] = [epub_chapter]

        # table of contents
        if len(book_chapters.keys()) == 1:  # no volume sections
            book.toc = list(book_chapters.values())[0]
        else:
            book.toc = (
                (epub.Section(volume[1]), tuple(book_chapters[volume]))
                for volume in sorted(book_chapters.keys(), key=lambda k: k[0])
            )

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = [c for volume in book_chapters.values() for c in volume]

        epub.write_epub(self.path, book, {})

    @property
    def path(self):
        return self.save_path / Path(f'{StringTools.slugify(self.novel.title)}.epub').resolve()

    def _epub_chapter(self, chapter):
        """
        create chapter xhtml

        :param chapter: novel chapter
        :return: chapter xhtml
        """
        prefix = f'{f"{StringTools.from_float(chapter.no)} " if chapter.no and chapter.no > 0 else ""}'
        title = f'{prefix}{chapter.title}'
        epub_chapter = epub.EpubHtml(title=title, file_name=f'{chapter.index}.xhtml', lang='en')

        # html content
        doc, tag, text = Doc().tagtext()
        with tag('h1'):
            text(title)

        # for the more neatly scraped
        if type(chapter.paragraphs) == list:
            for para in chapter.paragraphs:
                with tag('p'):
                    text(para)

        # those that are scraped as a single blob
        elif type(chapter.paragraphs) == str:
            doc.asis(chapter.paragraphs)

        epub_chapter.content = doc.getvalue()
        return epub_chapter
