# Loading model dependencies
import numpy as np
import torch
import torch.nn.functional as F
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from random import choice

# Downloading the model
tok = GPT2Tokenizer.from_pretrained("distilgpt2")
model = GPT2LMHeadModel.from_pretrained("distilgpt2")

# Redefining the predictions function since we now want to return a list of most likely next tokens 
# instead of a single token. Also, we want to return the proabilities in order to return them to 
# the user as well.

def get_preds(text, model=model, tok=tok, p=0.7):
    input_ids = torch.tensor(tok.encode(text)).unsqueeze(0)
    
    # changed from the basic app to reduce execution time by only passing las hidden layer to lm_head
    logits = model.lm_head(model.transformer(input_ids)[0][:,-1,:]) 
    
    probs = F.softmax(logits, dim=-1).squeeze()
    idxs = torch.argsort(probs, descending=True)
    res,pred_probs = [],[]
    for idx in idxs:
        res.append(idx)
        pred_probs.append(probs[idx])
        if sum(pred_probs) > p:
            pred_idxs = [idxs.new_tensor([p]) for p in res]
            break
    preds = [tok.convert_ids_to_tokens(int(p)) for p in pred_idxs]
    return [tok.convert_tokens_to_string(pred) for pred in preds], pred_probs

import panel as pn
pn.extension() # loading panel's extension for jupyter compatibility


text_input = pn.widgets.TextInput(value="",width=400)
generated_text = pn.pane.Str(text_input.value)
start_button = pn.widgets.Button(name="Generate",button_type="primary")

# creating radio buttons for the token options along with probabilities 
options = [""]
radio_button = pn.widgets.RadioButtonGroup(options=options,height=30,width=500)
prob_button = pn.widgets.RadioButtonGroup(options=options,height=30,width = 500)

# since the prob_button is only to inform the user of the probabilities, we don't need to be enabled
prob_button.disabled=True

# new click callback function which handles the updation of the radio buttons
def click_cb(event):
    if radio_button.value == "<|endoftext|>": 
        start_button.disabled = True
        return None
    updated_text = generated_text.object + radio_button.value
    generated_text.param.set_param(object=updated_text)
#     generated_text.object += radio_button.value
    preds, probs = get_preds(generated_text.object, model, tok)
    top_preds = preds[:10]
    radio_button.param.set_param(options=top_preds, value=top_preds[np.random.randint(0,len(top_preds))])
#     radio_button.options = preds[:10]
#     radio_button.value = radio_button.options[np.random.randint(0,len(radio_button.options))]
    prob_button.param.set_param(options=[str(round(float(i),2)) for i in probs[:10]])
#     prob_button.options = [str(round(float(i),2)) for i in probs[:10]]

start_button.on_click(click_cb)

# call back function in case the text input changes. Essentially, we need to reset our options. 
def text_change_cb(event):
    generated_text.object = event.new
    start_button.param.disabled = False
    radio_button.param.set_param(options=options, value=options[0])
#     radio_button.options = options
#     radio_button.value = radio_button.options[0]
    prob_button.param.set_param(options=options)
#     prob_button.options = options

# tying the callback function to the text_input widget
text_input.param.watch(text_change_cb, 'value')

# preparing the app
app = pn.Column(text_input,radio_button,prob_button,start_button,generated_text)

# Panel spacer object to center our title
h_spacer = pn.layout.HSpacer()

# defining the title and description 
title = pn.pane.Str("# **Text Generator**")
desc = pn.pane.HTML("<i>Welcome to the text generator! In order to get started, simply enter some starting input text below, click generate a few times and watch it go! You can also choose to select which token gets chosen using the radio buttons. Probabilities for each of which can be seen underneath. Give it a shot!</i>")

# setting up the final app
final_app = pn.Column(pn.Row(h_spacer,title,h_spacer), desc ,app)

#cleanup experiments

def cleanup():
    gc.collect()
    print("Finished cleaning")

final_app._cleanup = cleanup

# this command is needed in order to serve this app in production mode. (make sure to uncomment ofcourse)
final_app.servable()