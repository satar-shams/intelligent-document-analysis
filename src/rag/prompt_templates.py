
class PromptBuilder:

    def build(self, instruction: str, query: str, context: str,) -> str:
        if instruction.strip() == "":
            raise ValueError("instruction is empty")
        
        if query.strip() == "":
            raise ValueError("query is empty")
        
        if context.strip() == "":
            raise ValueError("context is empty")
        
        combined_text = ""
        combined_text += f"Instruction:\n{instruction}\nContext:\n{context}\nQuestion:\n{query}"
        return combined_text

if __name__ == "__main__":
    prompt_builder = PromptBuilder()
    result = prompt_builder.build(instruction="Answer the question using only the provided context. Do not add or invent information that is not supported by the context. If the context does not contain enough information to answer the question, say that the available context does not provide enough information.", 
                                  query="some query", 
                                  context="some context"
                                  )
    print(result)