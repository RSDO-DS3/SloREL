This folder contains scripts from https://github.com/monologg/R-BERT.

To train a model with this method use the dataset that was generated with methods from the `process_wikipedia_pages` folder and a bert model like SloBERTa or CroSloEngual.

To run the scripts you will first need to install dependancies with `pip install -r requirements.txt -f https://download.pytorch.org/whl/cpu/torch_stable.html`
for CPU version or `pip install -r requirements.txt -f https://download.pytorch.org/whl/cu101/torch_stable.html` for GPU accelerated version.

To train a model on your data set the parameters in `main.py` and run it. 

**Note** Sentences that have more tokens than max_seq_len will be skipped when training or testing the model with no errors.

To test a model on your dataset set the parameters in `predict.py` and run it. 