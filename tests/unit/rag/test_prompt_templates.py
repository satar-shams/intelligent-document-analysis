import pytest
from src.rag.prompt_templates import PromptBuilder

def test_build_prompt_with_valid_input():
    prompt_builder = PromptBuilder()
    result = prompt_builder.build(instruction="Give the best result based on Context and quey", 
                                  query="some query", 
                                  context="some context"
                                  )

    assert  isinstance(result, str)
    assert "Instruction:\n" in result
    assert "Give the best result based on Context and quey\n" in result
    assert "Context:\n" in result
    assert "some context\n" in result
    assert "Question:\n" in result
    assert "some query" in result

def test_build_prompt_with_empty_instruction():
    with pytest.raises(ValueError):
        prompt_builder = PromptBuilder()
        result = prompt_builder.build(instruction="", 
                                    query="some query", 
                                    context="some context"
                                  )
    
def test_build_prompt_with_empty_query():
    with pytest.raises(ValueError):
        prompt_builder = PromptBuilder()
        result = prompt_builder.build(instruction="Give the best result based on Context and quey", 
                                    query="", 
                                    context="some context"
                                  )
    
def test_build_prompt_with_empty_context():
    with pytest.raises(ValueError):
        prompt_builder = PromptBuilder()
        result = prompt_builder.build(instruction="Give the best result based on Context and quey", 
                                    query="some query", 
                                    context=""
                                  )


    