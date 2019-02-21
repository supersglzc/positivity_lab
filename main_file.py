import csv
from math import log
from twitter_specials import *
import string
not_character = set(string.punctuation)
word_counts_dict = {}
total = [0, 0, 0, 0, 0]

with open("labeled_corpus.tsv", encoding="utf-8") as csvfile:
    readCSV = csv.reader(csvfile, delimiter='\t')
    for row in readCSV:
        line_arr = list(row)

        text = line_arr[0]
        cat = line_arr[1]

        if cat == 'positive':
            category = 0
        elif cat == 'negative':
            category = 1
        elif cat == 'neutral':
            category = 2
        elif cat == 'irrelevant':
            category = 3
        else:
            continue

        text = clean_tweet(text, emo_repl_order, emo_repl, re_repl)

        text_list = text.split()
        text_list1 = []
        for i in text_list:
            if '@' not in i and '#' not in i:
                buffer = ''
                for j in i:
                    if j not in not_character:
                        buffer += j
                if buffer == 'rt':
                    continue
                text_list1.append(buffer)

        total[4] += 1
        total[category] += 1
        for i in text_list1:
            if i not in word_counts_dict:
                word_counts_dict[i] = [0, 0, 0, 0, 0]
            word_counts_dict[i][4] += 1
            word_counts_dict[i][category] += 1

csvfile.close()

probability = {}
for i, j in word_counts_dict.items():
    probability[i] = [j[0] / total[0], j[1] / total[1], j[2] / total[2], j[3] / total[3]]

probability2 = [total[0] / total[4], total[1] / total[4], total[2] / total[4], total[3] / total[4]]

#print(probability)
text_list5 = {}
write_file = open('locations_classified.tsv', 'w', newline='')
writeTSV = csv.writer(write_file, delimiter='\t')
with open("geo_twits_squares.tsv", encoding="utf-8") as tsvfile:
    readTSV = csv.reader((line.replace('\0', '') for line in tsvfile), delimiter='\t')
    for row in readTSV:
        line_arr = list(row)
        latitude = line_arr[0]
        longitude = line_arr[1]
        tweet = line_arr[2]

        text_list3 = tweet.split()
        text_list4 = []
        for i in text_list3:
            if '@' not in i and '#' not in i:
                buffer = ''
                for j in i:
                    if j not in not_character:
                        buffer += j
                if buffer == 'rt':
                    continue
                text_list4.append(buffer)
        #print(text_list4)
        probability3 = [log(probability2[0]), log(probability2[1]), log(probability2[2]), log(probability2[3])]
        for i in text_list4:
            for j in range(4):
                try:
                    probability[i]
                except:
                    continue
                if probability[i][j] != 0:
                    probability3[j] += log(probability[i][j])
        #print(probability2)
        #print(probability3)
        m = max(probability3)
        index = probability3.index(m)
        if index == 0:
            k = 'positive'
        elif index == 1:
            k = 'negative'
        elif index == 2:
            k = 'neutral'
        elif index == 3:
            k = 'irrelevant'
        else:
            print('error')

        writeTSV.writerow([latitude, longitude, k])

        if (latitude, longitude) not in text_list5:
            text_list5[(latitude, longitude)] = [0, 0, 0, 0]

        text_list5[(latitude, longitude)][index] += 1
write_file.close()
tsvfile.close()

text_list6 = {}
for (i, j) in text_list5.items():
    total = j[0] + j[1] + j[2] + j[3]
    score = (j[0] / total - j[1] / total + 1) / 2
    text_list6[i] = score

file_object = open('./public_html/data.js', 'w', newline='')
file_object.write("var data = [")
count = 0
for (i, j) in text_list6.items():
    if count == 0:
        file_object.write('{"score": ' + str(j) + ', "g": ' + str(float(i[1])+0.05/2) + ', "t": ' + str(float(i[0])+0.05/2) +
                          '}')
    else:
        file_object.write(', {"score": ' + str(j) + ', "g": ' + str(float(i[1]) + 0.05 / 2) + ', "t": ' + str(float(i[0]) +
                                                                                                         0.05 / 2) + '}')
    count += 1
file_object.write('];')
file_object.close()
