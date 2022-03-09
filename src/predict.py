import os

import numpy as np
import torch
from torch.utils.data import DataLoader, SequentialSampler, TensorDataset
from tqdm import tqdm

from model import RBERT
from utils import get_label, load_auto_tokenizer
import logging

logging.basicConfig()


relation_descriptions = dict()
with open("BERT_data/properties-with-labels.txt", encoding="utf-8") as f:
    for line in f:
        relation_descriptions[line.strip().split("\t")[0]] = line.strip().split("\t")[1]



def get_args(model_dir):
    return torch.load(os.path.join(model_dir, "training_args.bin"))
    

def load_model(model_dir, args, device):
    # Check whether model exists
    if not os.path.exists(model_dir):
        raise Exception("Model doesn't exists! Train first!")

    try:
        model = RBERT.from_pretrained(model_dir, args=args)
        model.to(device)
        model.eval()
    except:
        raise Exception("Some model files might be missing...")

    return model



model_dir = "./BERT_data"
args = get_args(model_dir)
if os.getenv("useGPU", False):
    device = "cuda"
else:
    device = "cpu"
model = load_model(model_dir, args, device)
tokenizer = load_auto_tokenizer(model_dir)
label_lst = get_label(args)



def get_device(pred_config):
    return "cuda" if torch.cuda.is_available() and not pred_config.no_cuda else "cpu"


def convert_input_file_to_tensor_dataset(
    sentences,
    args,
    model_dir,
    cls_token_segment_id=0,
    pad_token_segment_id=0,
    sequence_a_segment_id=0,
    mask_padding_with_zero=True,
):
    global tokenizer

    # Setting based on the current model type
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    pad_token_id = tokenizer.pad_token_id

    all_input_ids = []
    all_attention_mask = []
    all_token_type_ids = []
    all_e1_mask = []
    all_e2_mask = []

    for sentence in sentences:
            tokens = tokenizer.tokenize(sentence)

            e11_p = tokens.index("<e1>")  # the start position of entity1
            e12_p = tokens.index("</e1>")  # the end position of entity1
            e21_p = tokens.index("<e2>")  # the start position of entity2
            e22_p = tokens.index("</e2>")  # the end position of entity2

            # Replace the token
            tokens[e11_p] = "$"
            tokens[e12_p] = "$"
            tokens[e21_p] = "#"
            tokens[e22_p] = "#"

            # Add 1 because of the [CLS] token
            e11_p += 1
            e12_p += 1
            e21_p += 1
            e22_p += 1

            # Account for [CLS] and [SEP] with "- 2" and with "- 3" for RoBERTa.
            if args.add_sep_token:
                special_tokens_count = 2
            else:
                special_tokens_count = 1
            if len(tokens) > args.max_seq_len - special_tokens_count:
                tokens = tokens[: (args.max_seq_len - special_tokens_count)]

            # Add [SEP] token
            if args.add_sep_token:
                tokens += [sep_token]
            token_type_ids = [sequence_a_segment_id] * len(tokens)

            # Add [CLS] token
            tokens = [cls_token] + tokens
            token_type_ids = [cls_token_segment_id] + token_type_ids

            input_ids = tokenizer.convert_tokens_to_ids(tokens)

            for i in range(len(input_ids)):
                if input_ids[i] is None:
                    input_ids[i] = 32003

            # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
            attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

            # Zero-pad up to the sequence length.
            padding_length = args.max_seq_len - len(input_ids)
            input_ids = input_ids + ([pad_token_id] * padding_length)
            attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
            token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)

            # e1 mask, e2 mask
            e1_mask = [0] * len(attention_mask)
            e2_mask = [0] * len(attention_mask)

            for i in range(e11_p, e12_p + 1):
                e1_mask[i] = 1
            for i in range(e21_p, e22_p + 1):
                e2_mask[i] = 1

            all_input_ids.append(input_ids)
            all_attention_mask.append(attention_mask)
            all_token_type_ids.append(token_type_ids)
            all_e1_mask.append(e1_mask)
            all_e2_mask.append(e2_mask)

    # Change to Tensor
    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long)
    all_attention_mask = torch.tensor(all_attention_mask, dtype=torch.long)
    all_token_type_ids = torch.tensor(all_token_type_ids, dtype=torch.long)
    all_e1_mask = torch.tensor(all_e1_mask, dtype=torch.long)
    all_e2_mask = torch.tensor(all_e2_mask, dtype=torch.long)

    dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids, all_e1_mask, all_e2_mask)

    return dataset


def predict(sentence_data, call_id):
    global args
    global device
    global model_dir
    global model
    global label_lst
    global relation_descriptions
    # Convert input file to TensorDataset
    input_sentences = [i["BERT_input"] for i in sentence_data]
    dataset = convert_input_file_to_tensor_dataset(input_sentences, args, model_dir)

    # Predict
    sampler = SequentialSampler(dataset)
    data_loader = DataLoader(dataset, sampler=sampler, batch_size=1)

    preds = None

    for batch in tqdm(data_loader, desc="Predicting"):
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            inputs = {
                "input_ids": batch[0],
                "attention_mask": batch[1],
                "token_type_ids": batch[2],
                "labels": None,
                "e1_mask": batch[3],
                "e2_mask": batch[4],
            }
            outputs = model(**inputs)
            logits = outputs[0]

            if preds is None:
                preds = logits.detach().cpu().numpy()
            else:
                preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)

    preds_out = np.argmax(preds, axis=1)

    # Write to output file
    results = []
    for pred_out, pred, classla_data in zip(preds_out, preds, sentence_data):
       results.append({"sentence": classla_data["sentence_text"], 
                       "entity1": {
                            "text": classla_data["entity1_text"],
                            "sentence_position": classla_data["entity1_sentence_position"]
                       },
                       "entity2": {
                            "text": classla_data["entity2_text"],
                            "sentence_position": classla_data["entity2_sentence_position"]
                       },
                       "relation": {
                            "WikiData_tag": str(label_lst[pred_out]), 
                            "description": relation_descriptions[str(label_lst[pred_out])]
                       },
                       "score": float(pred[pred_out])})
    
    logging.info(f"call {call_id} Prediction Done!")
    return results
