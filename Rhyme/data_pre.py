def generate_de():
    with open('deuPD.txt', 'r', encoding='UTF-8') as f:
        w = f.readlines()
    dedict = {}
    for i in range(37, len(w)):
        word = w[i].split(' ')
        word[-1] = word[-1][:-1]
        dedict[word[0]] = word[1:]
    return dedict


def generate_en():
    with open('cmudict', 'r', encoding='ISO-8859-1') as f:
        w = f.readlines()
    endict = {}
    for i in range(126, len(w)):
        word = w[i].split(' ')
        word[-1] = word[-1][:-1]
        no_stress = []
        for ws in word:
            result = ''.join([j for j in ws if not j.isdigit()])
            no_stress.append(result)
        endict[no_stress[0]] = no_stress[2:]
    return endict


def lookup(word, dict):
    while word not in dict.keys():
        word = word[1:]
        if len(word) == 1:
            break
    if word not in dict.keys():
        return '<unk>'
    else:
        return dict[word]


def find_rhythm(file_poem, de_dict):
    with open(file_poem, 'r', encoding='UTF-8') as f_poem:
        poem = f_poem.readlines()
    last_words = []
    for i in range(len(poem)):
        line_words = poem[i].split(' ')
        last_words.append(line_words[-1][:-1].upper())
    sounds = []
    for word in last_words:
        sound = lookup(word, de_dict)
        sounds.append(sound[-1])
    print(sounds)
    sound_set = list(set(sounds))
    pos_dict = {}
    for sound in sound_set:
        if sounds.count(sound) > 1:
            index_list = []
            for (i, v) in enumerate(sounds):
                if v == sound:
                    index_list.append(i)
            pos_dict[sound] = index_list
    print(pos_dict)
    return poem, pos_dict


def retrieve(best_file, poem):
    with open(best_file, 'r', encoding='UTF-8') as t:
        translations = t.readlines()
    tr_sets = []
    clean_sets = []
    clean2tr = {}
    for line in poem:
        tr_line = []
        clean_line = []
        for ts in translations:
            if line[:-1] in ts:
                index = translations.index(ts)
                for raw in translations[index:index + 32]:
                    if raw[0] == 'H':
                        se = raw.split('\t')[2][:-1]
                        tr_line.append(se)
                        if '<unk>' not in se:
                            c_se = se
                            if se[-1] == ',' or se[-1] == '.':
                                c_se = se[:-2]
                            clean_line.append(c_se)
                            clean2tr[c_se] = se
        tr_sets.append(tr_line)
        clean_sets.append(clean_line)
    return tr_sets, clean_sets, clean2tr


def best_index(same_set, clean_list, ):
    sound_list = []
    for i in same_set:
        sound_candidate = []
        for line in clean_list[i]:
            # print(line)
            words = line.split(' ')
            last_sound = lookup(words[-1].upper(), en_dict)[-1]
            # print(last_sound)
            sound_candidate.append(last_sound)
        sound_list.append(sound_candidate)
    print(sound_list)
    total_set = set()
    for single_list in sound_list:
        single_set = list(set(single_list))
        total_set = total_set.union(single_set)

    sound_count = {}
    for single_sound in total_set:
        count = 0
        for single_list in sound_list:
            if single_sound in single_list:
                count += 1
        sound_count[single_sound] = count
    print(sound_count)
    ans = max(sound_count, key=lambda x: sound_count[x])
    print(ans)
    trans_index = []
    for single_list in sound_list:
        if ans not in single_list:
            single_index = 0
        else:
            single_index = single_list.index(ans)
        trans_index.append(single_index)
    print(trans_index)
    return trans_index


de_dict = generate_de()
en_dict = generate_en()

poem1, pos1 = find_rhythm('de_poem1', de_dict)
poem2, pos2 = find_rhythm('de_poem2', de_dict)
translation_list1, clean_list1, c2t = retrieve('poem-nbest-eval', poem1)
final_translation = {}
for p in pos1.values():
    translation_index = best_index(p, clean_list1)
    for i in range(len(p)):
        according_index = translation_index[i]
        ct = clean_list1[p[i]][according_index]
        final_translation[p[i]] = c2t[ct]
print(final_translation)

with open('translation', 'w', encoding='UTF-8') as f:
    for i in range(len(translation_list1)):
        if i in final_translation.keys():
            f.write(final_translation[i])
            f.write('\n')
        else:
            f.write(translation_list1[i][0])
            f.write('\n')

