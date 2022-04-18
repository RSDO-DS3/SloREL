last_sentence = ""
skip = True
skip_to_sentence = "V zadevi Prevlada javne koristi energetike – obnovljivega vira nad javno koristjo ohranjanja narave za Hidroelektrarno HE Mokrice upravno sodišče v samem postopku ni našlo napak ."

relation_descriptions = dict()

count = 0

with open("properties-with-labels.txt", encoding="utf-8") as f:
    for line in f:
        relation_descriptions[line.strip().split("\t")[0]] = line.strip().split("\t")[1]


with open("_RECON", "r", encoding="utf-8") as file:
    for line in file:
            data = line.strip().split(" | ")
            if data[0] != last_sentence:
                print("\n\n" + str(count) + " " + data[0] + "\n")
                last_sentence = data[0]
                count += 1
            if data[0] == skip_to_sentence:
                skip = False
            if skip:
                continue
            if data[5] == "P0":
                continue

            print(data[3], data[4], data[7], "\n", data[5], relation_descriptions[data[5]])
            inp = input()
            while inp not in {"p", "c", "f"}:
                inp = input()
            with open("out_24_ur.txt", "a", encoding="utf-8") as out_file:
                if inp != "p":
                    out_file.write(data[7] + "\t" + data[5] + "\t")
                if inp == "c":
                    out_file.write("c\n")
                elif inp == "f":
                    out_file.write("f\n")
