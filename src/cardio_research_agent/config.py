"""Local language-model configuration."""

from os import getenv

from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

DEFAULT_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

def get_chat_model() -> ChatHuggingFace:
    """Load a local Hugging Face model through LangChain."""
    load_dotenv()

    model_id = getenv("HF_MODEL_ID", DEFAULT_MODEL)
    device_name = getenv("HF_DEVICE", "cpu")

    device: int | str
    if device_name == "cpu":
        device = -1
    else:
        device = device_name

    langchain_llm = HuggingFacePipeline.from_model_id(
        model_id=model_id,
        task="text-generation",
        device=device,
        pipeline_kwargs={
            "max_new_tokens": 160,
            "do_sample": False,
            "return_full_text": False,
            "clean_up_tokenization_spaces": False,
        },
    )

    return ChatHuggingFace(llm=langchain_llm)