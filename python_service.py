from flask import Flask, jsonify, request
import document_processing as dproc
from flask_celery import make_celery
from celery.utils.log import get_task_logger
import os.path

log = get_task_logger(__name__)

app = Flask(__name__)
app.config['CELERY_BROKER_URL']='amqp://localhost//',
app.config['CELERY_RESULT_BACKEND']='amqp://localhost//'

celery = make_celery(app)

@celery.task(name='mytasks.tag_extraction_celery')
def tag_extraction_celery(req_json):
    log.info("Inside celery")
    return dproc.extract_tags(req_json)

@app.route("/receipt", methods = ['POST'])
def tag_extraction_service():
    log.info("service starts")
    req_json = request.get_json()
    task = tag_extraction_celery.delay(req_json)
    id = task.id
    if 'transaction_id' in req_json.keys():
        tr_id = req_json['transaction_id']
        #tr_path = ''.join(['C:/Users/tejaswini.buddha/Documents/Projects/WCPT_Policy/wcpt_policy/tasks/',tr_id,'.txt'])
        tr_path = ''.join(['/home/ubuntu/policy/AI-Policy/tasks/',tr_id,'.txt'])
        #print(tr_path)
        f = open(tr_path,'w')
        f.write(id)
        f.close()
        return jsonify({"message": "Your document is being processed. To check status use transaction id.", "transaction_id": tr_id})
    else:
        return jsonify("Unable to run as transaction_id is missing")


@app.route("/status", methods = ['POST'])
def status_result():
    status_json = request.get_json()
    if 'transaction_id' in status_json.keys():
        tr_id = status_json['transaction_id']
        #tr_path = ''.join(['C:/Users/tejaswini.buddha/Documents/Projects/WCPT_Policy/wcpt_policy/tasks/',transaction_id,'.txt'])
        tr_path = ''.join(['/home/ubuntu/policy/AI-Policy/tasks/',tr_id,'.txt'])
        print("Searching for status...")
        #print(tr_path)
        if os.path.exists(tr_path):
            f = open(tr_path,'r')
            id = f.read()
            result = celery.AsyncResult(id)
            return jsonify({"task_status": result.state, "result": result.get(),"transaction_id":tr_id})
        else:
            return jsonify({"message" : "Invalid transaction_id"})
    else:
        return jsonify({"message": "Unable to run as transaction_id is missing"})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8090)
