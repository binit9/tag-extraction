import os
import re
from tika import parser
from celery.utils.log import get_task_logger
 
log = get_task_logger(__name__)

def parse_data(path):
    
    content = []
    log.info("Document parsing starts")
    if path.endswith(('.pdf','.doc','.docx')):
        filetype = "supported"
        # Parse data from file
        file_data = parser.from_file(path)
        # Get files text content
        #text = re.sub(r'http[s]*:.*','',file_data['content'])
        text = file_data['content']
        indexes = [i for i,x in enumerate(text.split('\n')) if x.strip() == '###']
        content.append((indexes,text.split('\n')))
    elif path.endswith('.txt'):
        filetype = "supported"
        file_data = parser.from_file(path)
        text = file_data['content']
        indexes = [i for i,x in enumerate(text.replace('\r','').split('\n')) if x == '###']
        content.append((indexes,text.replace('\r','').split('\n')))
    else:
        filetype = "unsupported"
        content =[]
    
    return filetype,content
    
def extract_policies(content_docs):
        
        lst = []
        for doc in content_docs:
            indexes= doc[0]
            #print(indexes)
            policies_list = []
            if len(indexes) != 0:
                for i in range(len(indexes)):
                    if i == len(indexes)-1:
                        policies_list.append(doc[1][indexes[i]+1:])
                    else:
                        policies_list.append(doc[1][indexes[i]+1:indexes[i+1]])
                lst = policies_list
                text_format = "supported"
            else:
                lst = []
                text_format = "unsupported"
                
        return text_format,lst
    
def extract_rulename(doc):
    
    header = None
    
    for val in range(len(doc)):
        if len(doc[val]) > 1:
            if not doc[val].startswith('http'):
                header = doc[val]
                break           
    return header.strip()

def extract_sectionname(doc):
    
    for val in doc:
        for string in val[1]:
            if string:
                return string.strip()

def generate_ruleno(trnxid,policy_no):
    
    ruleid = '_'.join([trnxid,str(policy_no)])
    return ruleid

    
