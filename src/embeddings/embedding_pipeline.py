from sentence_transformers import SentenceTransformer

class EmbeddingPipeline:

    def __init__(
        self,
        model_name: str,
        model: SentenceTransformer | None = None,
    ):
        self.model = (
            model
            if model is not None
            else SentenceTransformer(model_name)
        )

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not isinstance(texts, list):
            raise TypeError(
                "texts must be a list of strings."
            )

        if not texts:
            return []

        for text in texts:
            if not isinstance(text, str):
                raise TypeError(
                    "Each item in texts must be a string."
                )

        embeddings = self.model.encode(texts)

        return embeddings.tolist()