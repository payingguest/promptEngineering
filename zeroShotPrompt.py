import torch
import transformers
from transformers import pipeline

model_name = 'gpt2'
tokenizer = transformers.GPT2Tokenizer.from_pretrained(model_name)
model = transformers.GPT2LMHeadModel.from_pretrained(model_name).to(torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
classifier = pipeline("zero-shot-classification")

def generate_response(prompt, max_length=50):
    candidate_labels = ["technology", "science", "sports", "politics", "entertainment"]
    classification = classifier(prompt, candidate_labels)
    top_label = classification["labels"][0]
    modified_prompt = top_label + ": " + prompt
    input_ids = tokenizer.encode(modified_prompt, return_tensors='pt').to(model.device)
    outputs = model.generate(input_ids, max_length=max_length, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

prompt = "What is the meaning of life?"
response = generate_response(prompt)
print("Prompt:", prompt)
print("Response:", response)
