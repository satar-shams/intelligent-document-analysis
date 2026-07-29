import re
import unicodedata
class TextCleaner:
    def clean_text(self, text: str) -> str:
        text = self._normalize_encoding(text)
        text = self._remove_invisible_characters(text)
        text = self._normalize_whitespace(text)

        return text.strip()

    def clean_pages(self, pages: list[dict]) -> list[dict]:
        cleaned_pages = []

        for page in pages:
            cleaned_page = page.copy()
            cleaned_page["text"] = self.clean_text(page["text"])
            cleaned_pages.append(cleaned_page)

        return cleaned_pages



    def _normalize_encoding(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text
        )

    def _remove_invisible_characters(self, text: str) -> str:
        return "".join(
            char
            for char in text
            if unicodedata.category(char) not in {"Cf"}
        )


    def _normalize_whitespace(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove spaces around line breaks
        text = re.sub(r"[ \t]+\n", "\n", text)

        # Collapse multiple spaces
        text = re.sub(r"[ \t]+", " ", text)

        # Preserve paragraphs but remove excessive empty lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text
        
        