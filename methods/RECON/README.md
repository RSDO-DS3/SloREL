This folder contains scripts from https://github.com/ansonb/RECON.

To train a model with this method use the dataset that was generated with methods from the `process_wikipedia_pages` folder.

To run the scripts you will first need to install dependancies with `pip install -r requirements.txt -f https://download.pytorch.org/whl/cpu/torch_stable.html`
for CPU version or `pip install -r requirements.txt -f https://download.pytorch.org/whl/cu101/torch_stable.html` for GPU accelerated version.

You will also need word vector embeddings like [FastText Wikipedia embeddings](https://fasttext.cc/docs/en/pretrained-vectors.html).

This method uses custom entity embeddings which are trained with `GAT_sep_space/main.py` script. To train these embeddings you can use the example data in 
`entity_context/entity_context.rar` archive or you can generate your own data with scripts in `process_wikipedia_pages` folder.

To train a model on your dataset set the parameters in `python train.py` script and run it.

To test your model on your dataset set the parameters in `python test.py` script and run it.