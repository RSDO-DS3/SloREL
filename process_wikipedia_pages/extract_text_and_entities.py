from os.path import isfile, join, exists
from os import listdir, mkdir
from bs4 import BeautifulSoup
from json import dumps, load
from hashlib import sha1
import classla
import requests
from xml.dom.minidom import parseString
from time import sleep
from functools import lru_cache
from elastic import entitySearch


@lru_cache(maxsize=28000)
def get_wikidata_tag_from_api(entity):
    while True:
        try:
            x = requests.get(
                'https://www.wikidata.org/w/api.php?action=wbgetentities&format=xml&props=sitelinks&sitefilter=slwiki&sites=slwiki&titles=' + entity)
            dom = parseString(x.text)
            break
        except:
            print("conn err")
            sleep(10)

    tmp = dom.getElementsByTagName('entity')

    if len(tmp) == 1:
        val = tmp[0].attributes['id'].value
        if val != "-1":
            return val

    return None


def link_entities(marked_sentences):
    for sentence in marked_sentences:
        for entity in sentence["entities"]:
            entity["wikidata_tag"] = None
            if "title" in entity:
                entity["wikidata_tag"] = get_wikidata_tag_from_api(entity["title"])
                if entity["wikidata_tag"]:
                    continue
            if "lemmas" in entity:
                entity["wikidata_tag"] = get_wikidata_tag_from_api("_".join(entity["lemmas"]))
                if entity["wikidata_tag"]:
                    continue
            if "text" in entity:
                entity["wikidata_tag"] = get_wikidata_tag_from_api(entity["text"].replace(" ", "_"))
                if entity["wikidata_tag"]:
                    continue
            if "text" in entity:
                entity["wikidata_tag"] = entitySearch(entity["text"])
                if entity["wikidata_tag"]:
                    continue
            if "lemmas" in entity:
                entity["wikidata_tag"] = entitySearch(" ".join(entity["lemmas"]))
                if entity["wikidata_tag"]:
                    continue

    return marked_sentences



def process_tag(tag):
    # change wikipedia link to a marked entity
    if tag.name == "a":
            try:
                # remove (stran ne obstaja) from entity title because WikiData API (used for entity linking) works only with exact titles
                return tag.text, [{
                    "text": tag.text,
                    "title": tag["title"].replace(" (stran ne obstaja)", ""),
                    "entity_start": 0,
                    "entity_end": len(tag.text)
                }]
            except:
                return "", []
    else:
        try:
            out_text = ""
            out_entity_links = []

            for child in tag.children:
                text, entity_links = process_tag(child)

                for entity_link in entity_links:
                    # shift position of entities in text because new text appears before it.
                    entity_link["entity_start"] += len(out_text)
                    entity_link["entity_end"] += len(out_text)

                out_entity_links += entity_links
                out_text += text

            return out_text, out_entity_links
        except:
            try:
                if tag[0] == "<":
                    tag = tag.text
                return tag, []
            except:
                return "", []


def add_classla_entities_and_split_on_sentences(text, entities, nlp):
    # empty paragraphs can appear after html preprocessing and they break classla nlp call
    if text == "":
        return []
    used_entity_links = 0
    marked_text = nlp(text).to_dict()
    sentence_position_in_text = -1
    sentence_end_position = -1
    # list of sentences with marked entities
    marked_sentences = []
    marked_sentence = {"text": "", "entities": []}
    curr_position_in_sentence = 0
    curr_position_in_text = 0
    link_appears_on_next_sentence = False
    cur_entity_link = None

    # iterate through sentences and mark found entities
    for isen, sentence in enumerate(marked_text):

        sentence_text = sentence[1][sentence[1].find("# text = ") + 9:].strip()

        marked_sentence["text"] += sentence_text

        cur_classla_entity = None
        for word in sentence[0]:

            word_position_sentence = marked_sentence["text"].find(word["text"], curr_position_in_sentence)
            if word_position_sentence != -1:
                curr_position_in_sentence = word_position_sentence

            else:
                print("word not found in sentence", word["text"])

            word_position_text = text.find(word["text"], curr_position_in_text)
            if word_position_text != -1:
                curr_position_in_text = word_position_text
                if sentence_position_in_text == -1:
                    sentence_position_in_text = curr_position_in_text
                if link_appears_on_next_sentence:
                    # add characters which appear between concatenated strings
                    marked_sentence["text"] += text[sentence_end_position:curr_position_in_text]
                    link_appears_on_next_sentence = False
                sentence_end_position = curr_position_in_text + len(word["text"])
                if len(entities) < used_entity_links and curr_position_in_text > entities[used_entity_links]["entity_start"]:
                    print("entity link skipped")
                    used_entity_links += 1

            else:
                print("word not found in text", word["text"])

            if len(entities) > used_entity_links and cur_entity_link and curr_position_in_text >= entities[used_entity_links]["entity_end"]:
                cur_entity_link["text"] = sentence_text[
                                             cur_entity_link["entity_start"]:cur_entity_link["entity_end"]]
                marked_sentence["entities"].append(cur_entity_link)
                cur_entity_link = None
                used_entity_links += 1

            if len(entities) > used_entity_links and curr_position_in_text == entities[used_entity_links]["entity_start"]:
                if cur_classla_entity:
                    cur_classla_entity["text"] = sentence_text[
                                                 cur_classla_entity["entity_start"]:cur_classla_entity["entity_end"]]
                    marked_sentence["entities"].append(cur_classla_entity)

                cur_entity_link = {"text": "",
                                      "title": entities[used_entity_links]["title"],
                                      "entity_start": curr_position_in_sentence,
                                      "entity_end": curr_position_in_sentence + len(word["text"])
                                      }
            elif cur_entity_link:
                cur_entity_link["entity_end"] = curr_position_in_sentence + len(word["text"])
            # entity links take priority over entities found through classla
            if not cur_entity_link:
                if word["ner"][0] == "B":
                    if cur_classla_entity:
                        cur_classla_entity["text"] = sentence_text[cur_classla_entity["entity_start"]:cur_classla_entity["entity_end"]]
                        marked_sentence["entities"].append(cur_classla_entity)

                    cur_classla_entity = {"text": "",
                                          "lemmas": [word["lemma"]],
                                          "entity_start": curr_position_in_sentence,
                                          "entity_end": curr_position_in_sentence + len(word["text"]),
                                          "type": word["ner"][2:]
                                          }

                elif cur_classla_entity and word["ner"] == "I-" + cur_classla_entity["type"]:
                    cur_classla_entity["entity_end"] = curr_position_in_sentence + len(word["text"])
                    cur_classla_entity["lemmas"].append(word["lemma"])

                elif cur_classla_entity:
                    cur_classla_entity["text"] = sentence_text[cur_classla_entity["entity_start"]:cur_classla_entity["entity_end"]]
                    marked_sentence["entities"].append(cur_classla_entity)
                    cur_classla_entity = None

        if cur_entity_link and curr_position_in_text + len(word["text"]) >= entities[used_entity_links]["entity_end"]:
            cur_entity_link["text"] = sentence_text[
                                      cur_entity_link["entity_start"]:cur_entity_link["entity_end"]]
            marked_sentence["entities"].append(cur_entity_link)
            cur_entity_link = None
            used_entity_links += 1

        if not cur_entity_link:
            marked_sentences.append(marked_sentence)
            marked_sentence = {"text": "", "entities": []}
            curr_position_in_sentence = 0
            sentence_position_in_text = -1
            sentence_end_position = -1
        else:
            link_appears_on_next_sentence = True

    return link_entities(marked_sentences)


if __name__ == "__main__":

    with open("settings.json", "r") as settings_file:
        settings = load(settings_file)
    print("downloading classla data")
    classla.download('sl')
    nlp = classla.Pipeline('sl', processors='tokenize,pos,lemma,ner', use_gpu=True)
    processed_text = set()
    print("getting page filenames from ", settings["page_folder"])
    htmlfiles = [f for f in listdir(settings["page_folder"]) if isfile(join(settings["page_folder"], f))]
    print("collected filenames of", len(htmlfiles), "files")

    if not exists(settings["text_with_entities_folder"]):
        mkdir(settings["text_with_entities_folder"])

    last_file = None
    for file in htmlfiles:
        if exists(settings["text_with_entities_folder"] + file[:-4] + "txt"):
            last_file = file

    skip = False
    if last_file:
        skip = True

    for file in htmlfiles:

        # skip already processed pages
        if skip:
            if exists(settings["text_with_entities_folder"] + file[:-4] + "txt"):
                with open(settings["text_with_entities_folder"] + file[:-4] + "txt", "r", encoding='utf-8') as f:
                    processed_text.add(sha1(f.read().encode('utf-8')).hexdigest())

            if file == last_file:
                skip = False
            continue

        else:
            print("working on:", file)
            with open(settings["page_folder"] + file, "r", encoding='utf-8') as f:
                html = f.read()
                soup = BeautifulSoup(html, 'lxml')
                text = ''

                for paragraph in soup.find_all('p'):
                    paragraph_text, paragraph_entity_links = process_tag(paragraph)
                    # classla changes &lt; to < and &gt; to > which confuses the method for finding tokens in text
                    marked_sentences = add_classla_entities_and_split_on_sentences(paragraph_text.replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;").replace("&gt;", ">").replace("&lt;", "<").strip(), paragraph_entity_links, nlp)
                    for marked_sentence in marked_sentences:
                        text += dumps(marked_sentence) + "\n"

                # check if page is not a duplicate of an already processed page
                hash = sha1(text.encode('utf-8')).hexdigest()
                if hash not in processed_text:
                    with open(settings["text_with_entities_folder"] + file[:-4] + "txt", "w", encoding='utf-8') as out_file:
                        out_file.write(text)
                    processed_text.add(hash)

