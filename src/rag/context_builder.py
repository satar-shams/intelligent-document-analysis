from src.schemas import SearchResultData


class ContextBuilder:
    def build(
        self,
        search_results: list[SearchResultData],
    ) -> str:
        chunks: list[str] = []

        for result in search_results:
            chunk = (
                f"chunk_id: {result.chunk_id}\n"
                f"document_id: {result.document_id}\n"
                f"page_start: {result.page_start}\n"
                f"page_end: {result.page_end}\n"
                f"text: {result.text}"
            )

            chunks.append(chunk)

        return "\n\n".join(chunks)


if __name__ == "__main__":
    from src.embeddings.embedding_pipeline import EmbeddingPipeline
    from src.vectorstore.chroma_store import ChromaStore

    chroma_store = ChromaStore()
    embedding_pipeline = EmbeddingPipeline()
    context_builder = ContextBuilder()

    query = "When he came to the war he was barely eighteen"

    query_embedding = embedding_pipeline.embed_texts(
        [query]
    )[0]

    results = chroma_store.search(
        query_embedding=query_embedding,
        top_k=5,
    )

    print(context_builder.build(results))