import pandas as pd
from nltk import pos_tag, pos_tag_sents, sent_tokenize
from rake_nltk import Rake
import nltk
from nltk.corpus import stopwords 
import re
from celery.utils.log import get_task_logger
import similar_tags as st
import string

log = get_task_logger(__name__)

import pandas as pd
#exclude_keys = pd.read_table(r'C:\Users\tejaswini.buddha\Desktop\Projects\WCPT_Policy\Policy_Modules\exclude.txt',header = None)
exclude_keys = pd.read_table(r'/home/ubuntu/policy/AI-Policy/models/exclude.txt',header = None)
exclude_keys = list(set(list(exclude_keys[0])))
max_length = 4

def tags_final(kw_list):
    tags_ = []
    for t in list(set(kw_list)):
        #print(t)
        if '_' not in t:
            string_ = '_'.join(st.preprocess_text(t))
        else:
            #print(t)
            str_ = [''.join(st.preprocess_text(txt)) for txt in t.split('_')]
            #print(str_)
            stg_ = []
            for s in str_:
                #print(s)
                if s.isalpha():
                    stg_.append(s)
            string_ = '_'.join(stg_)
        #print(string_)
        if len(string_) > 1:
            tags_.append(string_)
            
    return tags_

def extract_tags(text):
    log.info("Tag_Extraction starts")
    r = Rake()
    kw = r.extract_keywords_from_text(text)
    phrases = r.get_ranked_phrases()
    
    kw_list = []
    for each in phrases:
        pos_list = pos_tag(each.split())
        #print(pos_list)
        if len(pos_list)>1:
            for i in range(1,len(pos_list)):
                if pos_list[i][1] in ['NN', 'NNP', 'NNS', 'NNPS']:
                    if pos_list[i-1][1] in ['NN', 'NNP', 'NNS', 'NNPS','PRP','JJ','VBP','VBG']:
                        kw_list.append(pos_list[i-1][0]+'_'+pos_list[i][0])
        else:
            if pos_list[0][1] in ['NN', 'NNP', 'NNS', 'NNPS']:
                if pos_list[0][0] not in exclude_keys:
                    kw_list.append(pos_list[0][0])
                    
    tags__ = tags_final(kw_list)
                
    log.info("Extracted tags: %s", tags__ )
    
    return tags__

def other_imp_tags(text, max_len):
    #word_list = word_tokenize(text)
    clean_text = re.sub(r"[^A-Za-z0-9 -.()\[\]]", ' ', text)
    print(clean_text)
    word_list = clean_text.split()
    stop_words = stopwords.words('english')
    temp_list = []
    for word in word_list:
        if word.isupper(): 
            word1 = re.sub(r"[^A-Z]",'',word)
            if len(word1)>1:
                temp_list.append(word1)

        ind = word_list.index(word)
        if word_list[ind][0] in ['(', '[']:
            temp_kw = ''
            for i in range(ind,ind+max_len):
                temp_kw+=' '+word_list[i]
                if word_list[i][-1] in [')', ']']:
                    break
            if temp_kw[-1] in [')', ']']:
                print('\n\n',temp_kw)
                if len(temp_kw.split())>1:
                    temp_list.append(temp_kw.strip())
                elif len(temp_kw.strip()[1:-1])>1:
                    temp_list.append(temp_kw.strip()[1:-1])
    
    return list(set(temp_list))

def final_extract(text):
    tags = extract_tags(text)
    imp_tags = other_imp_tags(text,max_length)
    
    for t in imp_tags:
        if t.islower():
            if len(t.split()) == 1 and t in exclude_keys:
                imp_tags.remove(t)
    
    uncommon = [tag for tag in tags if tag.upper() not in imp_tags]
    final_tags = [*uncommon,*imp_tags]
    
    return final_tags
    