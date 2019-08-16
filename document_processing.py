
import os
from tika import parser
import document_parser as dp
import tag_extraction as te
import json
import similar_tags as st

from celery.utils.log import get_task_logger
 
log = get_task_logger(__name__)

def extract_tags(req_json):
    #log.info("Tag Extraction Starts")
    if req_json:
        
        try:
            trxid = req_json['transaction_id']
        except:
            log.info("Transaction ID not found")
            resp_dict = {}
            resp_dict["source"] = "accentureai"
            resp_dict["transaction_id"] = None
            resp_dict["AI_Output"] = []
            return_dict = {}
            return_dict["Status"] = "KO"
            return_dict["Message"] = "No transaction_id found"
            return_dict["error_code"] = ""
            return_dict["respObj"] = resp_dict
            return return_dict
            
        try:
            filename = req_json['filename']
            log.info("Extracting tags from %s",filename.split('/')[-1])
        except:
            log.info("Filename not found")
            resp_dict = {}
            resp_dict["source"] = "accentureai"
            resp_dict["transaction_id"] = trxid
            resp_dict["AI_Output"] = []
            return_dict = {}
            return_dict["Status"] = "KO"
            return_dict["Message"] = "No filename found"
            return_dict["error_code"] = ""
            return_dict["respObj"] = resp_dict
            return return_dict
                 
        
        type_,content = dp.parse_data(filename)
    
        if type_ == "supported":
            
            text_,policy_content = dp.extract_policies(content)
            if text_ == "supported":
     
                section = dp.extract_sectionname(content)  
                log.info("Document parsing is done for %s document", section)
                policies_list = []
                count=0
                
                for pc in policy_content:
                    
                    policy = []
                    for text in pc:
                        policy.append(' '.join(st.preprocess_text(text)))
                        
                    
                    count=count+1
                    policy_dict = {}
                    rulename = dp.extract_rulename(pc)
                    log.info("Data preprocessing is done for policy: '%s'",rulename)
                    ruleno = dp.generate_ruleno(trxid,count)
                    #print(ruleno)
                    desc = ''
                    #policy = st.preprocess_text(' '.join(pc))
                    tags = te.final_extract(' '.join(pc))
                    similarTags = st.extract_similartags(' '.join([rulename,' '.join(policy)]))
                    log.info("Extraction of Tags and Similar tags is done")

                    policy_dict["Rule_Number"] = ruleno
                    policy_dict["Section"] = section
                    policy_dict["Rule_Name"] = rulename
                    policy_dict["Description"] = desc
                    policy_dict["Tags"] = tags
                    policy_dict["Similar_Tags"] = similarTags
                    #log.info(policy_dict)
                    policies_list.append(policy_dict)

                resp_dict = {}
                resp_dict["source"] = "accentureai"
                resp_dict["transaction_id"] = trxid
                resp_dict["AI_Output"] = policies_list
                return_dict = {}
                return_dict["Status"] = "OK"
                return_dict["Message"] = "Tag Extraction Successful"
                return_dict["error_code"] = ""
                return_dict["respObj"] = resp_dict
                return return_dict
                # return {"Status": "OK",
                #         "Message": "Tag Extraction Successful",
                #         "error_code": "",
                #         "respObj":{
                #             "source": "accentureai",
                #             "transaction_id": trxid,
                #             "AI_Output":policies_list
                #                 }}

            elif text_ == "unsupported":
                log.info("Text format is not supported")
                resp_dict = {}
                resp_dict["source"] = "accentureai"
                resp_dict["transaction_id"] = trxid
                resp_dict["AI_Output"] = []
                return_dict = {}
                return_dict["Status"] = "KO"
                return_dict["Message"] = "Unsupported Text Format"
                return_dict["error_code"] = ""
                return_dict["respObj"] = resp_dict
                return return_dict

                #return json.dumps({"Status": "KO",
                #        "Message": " Unsupported Text Format",
                #        "error code": "",
                #        "respObj":{
                #            "source": "accentureai",
                #            "transaction_id": trxid,
                #            "AI_Output":{"content":[]}
                #        }})

        elif type_ == "unsupported":
            log.info("Unsupported file extension")
            resp_dict = {}
            resp_dict["source"] = "accentureai"
            resp_dict["transaction_id"] = trxid
            resp_dict["AI_Output"] = []
            return_dict = {}
            return_dict["Status"] = "KO"
            return_dict["Message"] = "Unsupported File Extension"
            return_dict["error_code"] = ""
            return_dict["respObj"] = resp_dict
            return return_dict
            
            #return json.dumps({"Status": "KO",
            #        "Message": " Invalid File Extension",
            #       "error code": "",
            #        "respObj":{
            #            "source": "accentureai",
            #            "transaction_id": trxid,
            #            "AI_Output":{"content":[]}
            #        }})
        
    else:
        log.info("Empty Json")


    

