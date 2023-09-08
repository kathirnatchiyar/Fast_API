import flask
app = flask.Flask(__name__)

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

def verify_auth ():
    api_key = flask.request.headers.get("Authorization")
    if api_key not in auth_keys:
        return False
    else:
        return True

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')
    
        