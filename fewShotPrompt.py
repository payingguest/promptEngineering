import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

model_name = 'gpt2'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

examples = [
    {'prompt': "Once upon a time", 'completion': "in a magical kingdom, there was a brave knight."},
    {'prompt': "The cat jumped", 'completion': "over the lazy dog."},
    {'prompt': "To be or", 'completion': "not to be, that is the question."}
]

training_instances = [
    {'input_ids': tokenizer.encode(example['prompt'], add_special_tokens=False, return_tensors='pt').squeeze(),
     'labels': tokenizer.encode(example['completion'], add_special_tokens=False, return_tensors='pt').squeeze()}
    for example in examples
]

input_prompt = "Once upon"
input_tokens = tokenizer.encode(input_prompt, add_special_tokens=False, return_tensors='pt')

generated_tokens = model.generate(
    input_ids=input_tokens,
    max_length=50,
    num_return_sequences=1,
    no_repeat_ngram_size=2,
    pad_token_id=tokenizer.eos_token_id
)

generated_completion = tokenizer.decode(generated_tokens.squeeze(), skip_special_tokens=True)
print("Generated completion:", generated_completion)
