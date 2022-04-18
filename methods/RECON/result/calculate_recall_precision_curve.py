import json
import matplotlib.pyplot as plt
from sklearn.metrics import ndcg_score


def plot_recall_precision(all_corr, correct, wrong, label):
    all_corr = float(all_corr)
    i = 0
    j = 0
    recall = []
    precision = []
    while i < len(correct) or j < len(wrong):
        if j < len(wrong) and (i == len(correct) or wrong[j] > correct[i]):
            j += 1
        else:
            i += 1
        if True: #i + j > (len(correct) + len(wrong)) / 100.0:
            if len(recall) == 0:
                recall.append(0.0)
                precision.append(float(i)/float(i+j))
            recall.append(float(i)/all_corr)
            precision.append(float(i)/float(i+j))
    plt.plot(recall, precision, label=label)


def process_file(file, label):
    with open(file, "r") as infile:
        results = json.load(infile)



    all_all_correct = 0
    all_correct = []
    all_false = []

    for i, rel in enumerate(results):
        print(i)
        all_all_correct += results[rel]["all_correct"]
        all_correct += results[rel]["correct"]
        all_false += results[rel]["false"]
        #plot_recall_precision(results[rel]["all_correct"], results[rel]["correct"], results[rel]["false"])

    all_correct = sorted(all_correct, reverse=True)
    all_false = sorted(all_false, reverse=True)
    plot_recall_precision(all_all_correct, all_correct, all_false, label)


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def process_file2(file, d, a):
    with open(file, "r") as infile:
        results = json.load(infile)

    rels = list(results)

    rels = sorted(rels, key=lambda x: float(len(results[x]["correct"]))/float(results[x]["all_correct"] + len(results[x]["false"])))

    rels = list(split(rels, 4))
    rels = rels[1] + rels[2] + rels[3]
    rels = list(split(rels, d))[a]

    results = results

    mn = float("inf")
    mx = -float("inf")

    for rel in rels:
        mn = min(mn,
                 float(len(results[rel]["correct"])) / float(results[rel]["all_correct"] + len(results[rel]["false"])))
        mx = max(mx,
                 float(len(results[rel]["correct"])) / float(results[rel]["all_correct"] + len(results[rel]["false"])))
        if rel == "P3450":
            continue
        plot_recall_precision(max(results[rel]["all_correct"], 1), sorted(results[rel]["correct"], reverse=True),
                                                                       sorted(results[rel]["false"], reverse=True),
                                label=rel)

    mn = int(100.0 * mn)
    mx = int(100.0 * mx) + 1
    print("\\caption{Točnost med $" + str(mn) + "\\%$ in $" + str(mx) + "\\%$.}")


relation_descriptions = dict()
with open("../../emnlp2017-relation-extraction-master/resources/properties-with-labels.txt", encoding="utf-8") as f:
    for line in f:
        relation_descriptions[line.strip().split("\t")[0]] = line.strip().split("\t")[1]


def numb_of_correct_rels(file):
    with open(file, "r") as infile:
        results = json.load(infile)
    out = []
    for rel in results:
        out.append((rel, relation_descriptions[rel], len(results[rel]["correct"]), len(results[rel]["false"])))
    out = sorted(out, key=lambda x: x[2]+x[3], reverse=True)

    #with open("wiki_recon.txt", "w") as out_file:
    #    json.dump(out, out_file)
    with open("24ur_recon.txt", "r") as infile:
        out_recon = json.load(infile)
    with open("24ur_bert.txt", "r") as infile:
        out_bert = json.load(infile)
    with open("24ur_lstm.txt", "r") as infile:
        out_lstm = json.load(infile)
    rels = set()
    for i in out_recon+out_bert+out_lstm:
        rels.add(i[0])
    out = []
    for rel in rels:
        tmp = [rel, relation_descriptions[rel]]
        for i in out_lstm:
            if i[0] == rel:
                tmp.append(i[2] + i[3])
                break
        if len(tmp) == 2:
            tmp.append(0)

        for i in out_bert:
            if i[0] == rel:
                tmp.append(i[2] + i[3])
                break
        if len(tmp) == 3:
            tmp.append(0)

        for i in out_recon:
            if i[0] == rel:
                tmp.append(i[2] + i[3])
                break
        if len(tmp) == 4:
            tmp.append(0)
        out.append(tmp)

    out = sorted(out, key=lambda x: x[2] + x[3] + x[4], reverse=True)
    for rel, desc, lstm_num, bert_num, recon_num in out:
        print(" & ".join([rel, desc, "$"+str(lstm_num)+"$", "$"+str(bert_num)+"$", "$"+str(recon_num)+"$"]) + "\\\\")


def percentage_of_correct_rels(file):
    with open(file, "r") as infile:
        results = json.load(infile)
    corr = 0
    false = 0
    for rel in results:
        corr += len(results[rel]["correct"])
        false += len(results[rel]["false"])
    print("$", float(corr) / float(corr+false), "\\%$")


def calculate_precision_recall_ndcg(all_correct, correct, wrong):
    all_corr = float(all_correct)
    i = 0
    j = 0
    retrieval = []
    while i < len(correct) or j < len(wrong):
        if j < len(wrong) and (i == len(correct) or wrong[j] > correct[i]):
            retrieval.append(0)
            j += 1
        else:
            retrieval.append(1)
            i += 1
    best_retrieval = sorted(retrieval, reverse=True)
    try:
        ndcg = ndcg_score([best_retrieval], [retrieval])
    except:
        ndcg = 0
    precision = float(sum(retrieval)) / float(len(retrieval))
    recall = float(sum(retrieval)) / float(max(1, all_corr))
    #recall = all_correct
    return [round(ndcg, 2), round(precision, 2), round(recall, 2)]


def get_precision_recall_ndcg(file, out_file):
    with open(file, "r") as infile:
        results = json.load(infile)

    all_all_correct = 0
    all_cor = []
    all_false = []
    out = []

    for i, rel in enumerate(results):
        all_correct = results[rel]["all_correct"]
        correct = results[rel]["correct"]
        wrong = results[rel]["false"]
        all_all_correct += all_correct
        all_cor += correct
        all_false += wrong
        out.append([rel] + calculate_precision_recall_ndcg(all_correct, correct, wrong))

    out.append(["all"] + calculate_precision_recall_ndcg(all_all_correct, all_cor, all_false))
    out = sorted(out)
    with open(out_file, "w") as o:
        json.dump(out, o)


# process_file("sorted_out_wikidata_test.txt", "Wikipedija testna množica")
# process_file("sorted_out_wikidata_train.txt", "Wikipedija učna množica")
# process_file("sorted_out_24_ur.txt", "24ur testna množica")

# process_file2("sorted_out_24_ur.txt", 4, 3)
# process_file2("sorted_out_wikidata_test.txt", 4, 3)
# numb_of_correct_rels("sorted_out_wikidata_test.txt")

get_precision_recall_ndcg("sorted_out_wikidata_train.txt", "ndcg_wikipedia_train_recon.json")
# plt.xlabel("priklic")
# plt.ylabel("točnost")
# plt.legend()
# plt.show()
