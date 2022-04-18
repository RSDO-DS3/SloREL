with open("_RECON_train_wiki", "r", encoding="utf-8") as file:
    with open("out_wikidata_train.txt", "w", encoding="utf-8") as out_file:
        for line in file:
            data = line.strip().split(" | ")
            out_file.write(data[-1] + "\t" + data[-3] + "\t")
            if data[-3] == data[-2]:
                out_file.write("c\n")
            else:
                out_file.write("f\n")