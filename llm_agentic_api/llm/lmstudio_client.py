import os
from transformers import AutoTokenizer
from onnxruntime_genai import GenerativeModel

# Download the ONNX model from:
# https://huggingface.co/onnx-community/Llama-3.2-3B-Instruct-ONNX
# and set the path to the ONNX file below (e.g., cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/model.onnx)
ONNX_MODEL_PATH = os.getenv(
    "ONNX_MODEL_PATH",
    "./Llama-3.2-3B-Instruct-ONNX/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/model.onnx"
)
# Use the base model name for the tokenizer
MODEL_NAME = os.getenv(
    "HF_MODEL_NAME",
    "onnx-community/Llama-3.2-3B-Instruct-ONNX"
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)

MODEL_DIR = "./Llama-3.2-3B-Instruct-ONNX/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4"
model = GenerativeModel(MODEL_DIR)

def chat_with_llm(messages, functions=None):
    """
    Runs inference on the Llama-3.2-3B-Instruct-ONNX model for chat completion.
    Only supports simple prompt completion (no function/tool calling logic inside the model).
    """
    # Concatenate messages into a single prompt
    prompt = "\n".join([m["content"] for m in messages if m["role"] in ("system", "user")])
    output = model.generate(prompt, max_new_tokens=128)
    return {"content": output} 