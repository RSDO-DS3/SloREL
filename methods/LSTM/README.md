This folder contains scripts from https://github.com/UKPLab/emnlp2017-relation-extraction.

To train a model with this method use the dataset that was generated with methods from the `process_wikipedia_pages` folder.

To run the scripts you will first need to install dependancies with `pip install -r requirements.txt`.
Because tensorflow version 1.15.0 is no longer avaliable from PyPI you will need to change the link for tensorflow in `requirements.txt` based on your OS and if you want
the tensorflow to have GPU acceleration.

You will need word vector embeddings like [FastText Wikipedia embeddings](https://fasttext.cc/docs/en/pretrained-vectors.html).

To train a model on your data run `python model_train.py train {location_of_your_train_set} {location_of_your_validation_set}`.

To test your model on your dataset run `python test.py {location_of_your_test_set}`