from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

app = FastAPI()

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
model_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)

@app.post("/summarize")
async def summarize(request: Request):
    try:
        body = await request.json()
        context = body.get("chunks", [])
        question = body.get("question", "")

        prompt = (
            f"User question: {question}\n"
            f"Context:\n{''.join(context)}\n"
            "Give a concise spoken-style financial summary based on the context."
        )

        output = model_pipeline(prompt)[0]["generated_text"]
        response_text = output.replace(prompt, "").strip()

        return {"summary": response_text}
    except Exception as e:
        print("🔴 LOCAL LLM ERROR:", e)
        return {"error": str(e)}, 500
