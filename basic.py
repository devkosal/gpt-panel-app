# Loading model dependencies
import numpy as np
import torch
import torch.nn.functional as F
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from random import choice
import streamlit as st

@st.cache(allow_output_mutation=True)
def load_model_tok():
    return GPT2Tokenizer.from_pretrained("gpt2"), GPT2LMHeadModel.from_pretrained("gpt2")

tok, model = load_model_tok()


# Redefining the predictions function since we now want to return a list of most likely next tokens 
# instead of a single token. Also, we want to return the proabilities in order to return them to 
# the user as well.

@st.cache
def get_pred(text, model=model, tok=tok, p=0.7):
    # 1. tokenize/encode the input text
    input_ids = torch.tensor(tok.encode(text)).unsqueeze(0)
    # 2. extract the logits vector for the next possible token
    logits = model(input_ids,)[0][:, -1]
    # 3. apply softmax to the logits so we have the probabilities of each word add up to 1
    probs = F.softmax(logits, dim=-1).squeeze()
    # 4. sort the probabilities in descending order 
    idxs = torch.argsort(probs, descending=True)
    # 5. loop through the ordered probabilities until they sum up to p. Then, randomly choose an option
    res, cumsum = [], 0.
    for idx in idxs:
        res.append(idx)
        cumsum += probs[idx]
        if cumsum > p:
            pred_idx = idxs.new_tensor([choice(res)])
            break
    # 6. convert the chosen prediction into text
    pred = tok.convert_ids_to_tokens(int(pred_idx))
    return tok.convert_tokens_to_string(pred)

st.title('Text Generator')
text = st.text_area("Text Input")
generated_text = text
n = st.slider("length",1,200,100,1)

if st.button("Generate"):
    for i in range(n):
        generated_text += get_pred(generated_text)
generated_text
