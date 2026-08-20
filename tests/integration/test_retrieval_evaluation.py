from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.vectorstore.chroma_store import ChromaStore


EVALUATION_QUERIES = [
    {
        "query": "How did the Canadian soldiers feel about the war and dying near Amiens?",
        "relevant_chunk_ids": {"117"},
    },
    {
        "query": "How did the soldier described in this passage behave toward his men?",
        "relevant_chunk_ids": {"233"},
    },
    {
        "query": "Which different nationalities and ethnic groups were represented among the soldiers in France?",
        "relevant_chunk_ids": {"349"},
    },
    {
        "query": "What does the phrase 'test of scarlet' refer to in the passage?",
        "relevant_chunk_ids": {"465"},
    },
    {
        "query": "How were the artillery guns going to be prepared before the attack?",
        "relevant_chunk_ids": {"581"},
    },
    {
        "query": "Why was the scale of yesterday's attack unexpected?",
        "relevant_chunk_ids": {"697"},
    },
    {
        "query": "What happened when the infantry attacked the barricade?",
        "relevant_chunk_ids": {"1052"},
    },
    {
        "query": "What happened to the men and horses along the mud-track?",
        "relevant_chunk_ids": {"929"},
    },
]


def test_retrieval_hit_at_k():
    embedding_pipeline = EmbeddingPipeline()
    chroma_store = ChromaStore()

    ks = [1, 3, 5]

    hit_counts = {k: 0 for k in ks}

    print("\nRetrieval Evaluation")

    for index, evaluation in enumerate(EVALUATION_QUERIES, start=1):
        query = evaluation["query"]
        relevant_chunk_ids = evaluation["relevant_chunk_ids"]

        query_embedding = embedding_pipeline.embed_texts(
            [query]
        )[0]

        results = chroma_store.search(
            query_embedding=query_embedding,
            top_k=max(ks),
        )

        result_chunk_ids = [
            str(result.chunk_id)
            for result in results
        ]

        print(f"\nQuery {index}: {query}")
        print(f"Relevant chunks: {sorted(relevant_chunk_ids)}")

        for k in ks:
            top_k_ids = set(result_chunk_ids[:k])

            hit = bool(
                top_k_ids.intersection(relevant_chunk_ids)
            )

            if hit:
                hit_counts[k] += 1

            print(
                f"  Hit@{k}: {'✓' if hit else '✗'}"
            )

    total_queries = len(EVALUATION_QUERIES)

    print("\nResults:")

    for k in ks:
        percentage = (
            hit_counts[k] / total_queries
        ) * 100

        print(
            f"  Hit@{k}: "
            f"{hit_counts[k]}/{total_queries} "
            f"({percentage:.1f}%)"
        )

    # The evaluation should retrieve at least one
    # relevant chunk somewhere in the top 5.
    assert hit_counts[5] > 0