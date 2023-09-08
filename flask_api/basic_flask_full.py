import flask
import os
import subprocess

app = flask.Flask(__name__)

#return the path to the directory that contains the current Python script.
script_path = os.path.dirname(os.path.realpath(__file__)) 
#combine the value of the variable with the string
log_path = script_path + "/logs"
auth_keys = [ "yxjF0YGyuEORb2GjuknEGLOwvCHfdMJq", "DcIfPP9530lyNuS3hqgkmJcfXp09xf7P" ]

@app.route("/firstsubmit", methods=["POST"])
def first_submit():
    if not verify_auth():
        resp =  {
                        "status": "Failed",
                        "message": "401 Unauthorized. Invalid Authkey"
                    }
        return flask.jsonify(resp), 401
    data = flask.request.get_json()
    inputTypes = {"customer_name": "String", "owner_id": "Integer", "lob": "String", "required_services": "list" }

    for key in inputTypes.keys():
        if not verifyInput(data, key, inputTypes[key]):
            errmsg = "{} is not provided in input. check and try again".format(key)
            resp =  {
                        "status": "Failed",
                        "message": errmsg
                    }
            return flask.jsonify(resp), 501
    
    successmsg = "Successfully Initialized for the customer {} with owner id {} ".format(data["customer_name"], data["owner_id"] )
    resp =  {
                    "status": "Initializing",
                    "message": successmsg
                }
    # TODO: need to call the trigger_provisioner her 
    trigger_provisioner(data)
    
    return flask.jsonify(resp), 200

@app.route("/getstatus", methods=["POST"])
def getstatus():
    if not verify_auth():
        resp =  {
                        "status": "Failed",
                        "message": "401 Unauthorized. Invalid Authkey"
                    }
        return flask.jsonify(resp), 401
    data = flask.request.get_json()
    inputTypes = {"customer_name": "String", "owner_id": "Integer", "lob": "String", "required_services": "list" }

    for key in inputTypes.keys():
        if not verifyInput(data, key, inputTypes[key]):
            errmsg = "{} is not provided in input. check and try again".format(key)
            resp =  {
                        "status": "Unknown",
                        "message": errmsg
                    }
            return flask.jsonify(resp), 501
    
    # TODO : here need to get the status from tailedlog 
    
    current_status = getStatus(data)

    # successmsg = "Successfully Initialized for the customer {} with owner id {} ".format(data["customer_name"], data["owner_id"] )
    resp =  {
                    "status": current_status['status'],
                    "message": current_status['message'],
                    "progress": current_status['percentage']
                }
    print(resp)
    return flask.jsonify(resp), 200

def verifyInput(datain, keyin, itype):

    if itype == "list":
        if ( keyin not in datain ) or ( datain[keyin] == '') or (type(datain[keyin]) != list ) :
            return False
        else:
            return True
    elif ( keyin not in datain ) or ( datain[keyin] == ''):
        return False
    else:
        return True
    

def trigger_provisioner(datain):
    owner_id = datain['owner_id']
    customer_name = datain['customer_name']
    lob = datain['lob']
    # required_services will be a list
    required_services = datain['required_services']  
    service_name = required_services[0]
    provisioner_script_path = "/usr/local/service_deployer_api/test-db-provisioner.sh"
    log_file = log_path +"/tailedlog_"+owner_id+"_"+service_name
    
    os.system("mkdir -p {}".format(log_path))
    os.system("touch {}".format(log_file))
    
    os.system("bash {} > {} 2>&1 &".format(provisioner_script_path, log_file))
    # mypid = os.system("echo $!")

def getStatus(datain):
    owner_id = datain['owner_id']
    customer_name = datain['customer_name']
    lob = datain['lob']
    # required_services will be a list
    required_services = datain['required_services']  
    service_name = required_services[0]
    provisioner_script_path = "/usr/local/service_deployer_api/test-db-provisioner.sh"
    log_file = log_path +"/tailedlog_"+owner_id+"_"+service_name
    
    rs = os.system("ps -ef | grep 'bash {} > {}'".format(provisioner_script_path, log_file))
    percent_tmp1 = subprocess.check_output("tail -10000 {} | grep 'deployment progress -' | tail -1 | awk '{{print $4}}' ".format(log_file), shell=True)
    percent_tmp = percent_tmp1.decode().strip()
    if rs == 0:
        if percent_tmp != "":
            if percent_tmp == "100":
                return { "percentage": percent_tmp, "status": "Completed", "message": "Deployment Successfully completed" }
            else:
                return { "percentage": percent_tmp, "status": "in-Progress", "message": "Still deployment in progress" }
        else:
            return { "percentage": 0, "status": "Initializing" , "message": "Still deployment initializing" }
            
    else: 
        # percent_tmp = subprocess.check_output("tail -10000 {} | grep 'deployment completed -' | tail -1 | awk '{print $4}' ".format(log_file), shell=True)
        if percent_tmp != "":
            if percent_tmp == "100":
                return { "percentage": percent_tmp, "status": "Completed", "message": "Deployment Successfully completed" }
            else:
                return { "percentage": percent_tmp, "status": "Failed", "message": "Deployment Failed" }
        else:
            return { "percentage": 0, "status": "Failed", "message": "Deployment Failed" }



def verify_auth ():
    api_key = flask.request.headers.get("Authorization")
    if api_key not in auth_keys:
        return False
    else:
        return True



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')
    
        