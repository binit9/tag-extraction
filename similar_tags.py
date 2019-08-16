from nltk.corpus import stopwords, wordnet
from nltk import pos_tag, word_tokenize, sent_tokenize
from collections import Counter
import string
import re
from celery.utils.log import get_task_logger
 
log = get_task_logger(__name__)

def replace_text(text):
    
    replacements = [(r"won\'t", "will not"), (r"can\'t", "can not"), (r"n\'t", " not"),
                (r"\'re", " are"), (r"\'s", " is"), (r"\'d", " would"),
                (r"\'ll", " will"), (r"\'t", " not"), (r"\'ve", " have"), (r"\'m", " am")]
    
    for old, new in replacements:
        text = re.sub(old, new, text)
    return text

def preprocess_text(text):
    stop = stopwords.words('english')
    no_punc = ''.join((char for char in text if char not in string.punctuation))
    word_list = no_punc.replace('\n',' ').strip().lower().split()
    word_list = [w for w in word_list if not w in stop]
    return word_list

def get_wordfreq(words):
    counts = Counter(words)
    top_20 = counts.most_common(20)
    return top_20

def select_tags(words):
    selected_tags = []
    counter=0
    for each in words:
        if counter==5:
            break
        if (pos_tag([each[0]])[0][1] in ['NN','NNS','VBG']):
            selected_tags.append(each[0])
            counter+=1
            
    return selected_tags    

def synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lm in syn.lemmas():
                 synonyms.append(lm.name())
    return list(set(synonyms))

def final_similartags(selected_tags):
    s_tags = []
    for each in selected_tags:
        syno = synonyms(each)
        s_tags.extend(syno)
    similar_tags = list(set(s_tags))
    
    return similar_tags

def extract_similartags(data):
    log.info("Similar Tags Extraction starts")
    clean_text = replace_text(data)
    clean_text = preprocess_text(clean_text)
    #log.info("Data Preprocessing is done")
    wordfreq = get_wordfreq(clean_text)
    tags = select_tags(wordfreq)
    final_tags = final_similartags(tags)
    log.info("Similar Tags: %s", final_tags)
    #print(len(final_tags),'similar tags found :', final_tags)
    return final_tags
    
    
    
    