import json
import os
from pathlib import Path

from dotenv import load_dotenv

from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.rag.context_builder import ContextBuilder
from src.rag.llm_client import LLMClient
from src.rag.prompt_templates import PromptBuilder
from src.rag.retriever import Retriever
from src.vectorstore.chroma_store import ChromaStore


INSTRUCTION = (
    "Answer the question using only the provided context. "
    "Do not add or invent information that is not supported by the context. "
    "If the context does not contain enough information to answer the question, "
    "say that the available context does not provide enough information."
)


class RAGPipeline:

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        prompt_builder: PromptBuilder,
        llm_client: LLMClient,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

    def process_question(
        self,
        query: str,
        top_k: int = 10,
    ) -> dict:
        search_results = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        context = self.context_builder.build(
            search_results=search_results,
        )

        prompt = self.prompt_builder.build(
            instruction=INSTRUCTION,
            query=query,
            context=context,
        )

        answer = self.llm_client.generate(
            prompt=prompt,
        )

        retrieved_results = []

        for rank, result in enumerate(search_results, start=1):
            retrieved_results.append(
                {
                    "rank": rank,
                    "chunk_id": result.chunk_id,
                    "document_id": result.document_id,
                    "page_start": result.page_start,
                    "page_end": result.page_end,
                    "distance": result.distance,
                }
            )

        return {
            "query": query,
            "prompt": prompt,
            "answer": answer,
            "retrieved_results": retrieved_results,
        }


def read_questions(
    input_path: str | Path,
) -> list[dict]:
    records = []

    with Path(input_path).open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            if "id" not in record:
                raise ValueError(
                    f"Missing 'id' on line {line_number}."
                )

            if "query" not in record:
                raise ValueError(
                    f"Missing 'query' on line {line_number}."
                )

            query = record["query"]

            if not isinstance(query, str):
                raise ValueError(
                    f"'query' must be a string on line {line_number}."
                )

            query = query.strip()

            if not query:
                raise ValueError(
                    f"Empty query on line {line_number}."
                )

            records.append(
                {
                    "id": record["id"],
                    "query": query,
                }
            )

    return records


def write_jsonl(
    records: list[dict],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def run_batch(
    input_path: str | Path,
    prompts_path: str | Path,
    results_path: str | Path,
    top_k: int = 10,
) -> None:
    load_dotenv()

    questions = read_questions(input_path)

    embedding_pipeline = EmbeddingPipeline()
    chroma_store = ChromaStore()

    retriever = Retriever(
        embedding_pipeline=embedding_pipeline,
        chroma_store=chroma_store,
    )

    context_builder = ContextBuilder()
    prompt_builder = PromptBuilder()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set."
        )

    llm_client = LLMClient(
        api_key=api_key,
    )

    rag_pipeline = RAGPipeline(
        retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_client=llm_client,
    )

    prompt_records = []
    result_records = []

    for question in questions:
        question_id = question["id"]
        query = question["query"]

        print(
            f"Processing question {question_id}: {query}"
        )

        pipeline_result = rag_pipeline.process_question(
            query=query,
            top_k=top_k,
        )

        prompt_records.append(
            {
                "id": question_id,
                "query": query,
                "top_k": top_k,
                "prompt": pipeline_result["prompt"],
                "retrieved_results": pipeline_result[
                    "retrieved_results"
                ],
            }
        )

        result_records.append(
            {
                "id": question_id,
                "query": query,
                "answer": pipeline_result["answer"],
                "retrieved_results": pipeline_result[
                    "retrieved_results"
                ],
            }
        )

    write_jsonl(
        records=prompt_records,
        output_path=prompts_path,
    )

    write_jsonl(
        records=result_records,
        output_path=results_path,
    )


def main() -> None:
    input_path = "data/evaluation/questions.jsonl"
    prompts_path = "data/evaluation/prompts.jsonl"
    results_path = "data/evaluation/results.jsonl"

    run_batch(
        input_path=input_path,
        prompts_path=prompts_path,
        results_path=results_path,
        top_k=10,
    )


if __name__ == "__main__":
    main()