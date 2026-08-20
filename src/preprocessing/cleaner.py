import re
import unicodedata


class TextCleaner:
    """
    Clean and denoise extracted document text while preserving
    the original document content and structure as much as possible.
    """

    def clean_text(self, text: str) -> str:
        """
        Clean and denoise a single text string.
        """
        text = self._normalize_encoding(text)
        text = self._remove_invisible_characters(text)
        text = self._normalize_whitespace(text)
        text = self._remove_repeated_characters(text)

        return text.strip()

    def _normalize_encoding(self, text: str) -> str:
        """
        Normalize Unicode characters using NFKC normalization.
        """
        return unicodedata.normalize("NFKC", text)

    def _remove_invisible_characters(self, text: str) -> str:
        """
        Remove Unicode formatting/control characters while preserving
        normal whitespace characters.
        """
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

    def _remove_repeated_characters(self, text: str) -> str:
        """
        Remove obvious excessive character repetition caused by
        formatting or OCR noise.
        """
        return re.sub(r"([^\w\s])\1{4,}", r"\1", text)

    def _remove_repeated_lines(
        self,
        records: list[dict],
    ) -> list[dict]:
        """
        Remove lines that are repeated across multiple records.

        This is intended to remove common headers and footers while
        preserving the rest of the document content.
        """
        line_counts: dict[str, int] = {}

        for record in records:
            lines = set(
                line.strip()
                for line in record["text"].splitlines()
                if line.strip()
            )

            for line in lines:
                line_counts[line] = line_counts.get(line, 0) + 1

        repeated_lines = {
            line
            for line, count in line_counts.items()
            if count >= 3
        }

        cleaned_records = []

        for record in records:
            cleaned_record = record.copy()

            lines = record["text"].splitlines()

            cleaned_lines = [
                line
                for line in lines
                if line.strip() not in repeated_lines
            ]

            cleaned_record["text"] = "\n".join(cleaned_lines).strip()

            cleaned_records.append(cleaned_record)

        return cleaned_records