"""Local language-model configuration."""

from os import getenv

from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

DEFAULT_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"


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

    local_pipeline = HuggingFacePipeline.from_model_id(
        model_id=model_id,
        task="text-generation",
        device=device,
        pipeline_kwargs={
            "max_new_tokens": 160,
            "do_sample": False,
            "repetition_penalty": 1.05,
            "return_full_text": False,
        },
    )

    return ChatHuggingFace(llm=local_pipeline)