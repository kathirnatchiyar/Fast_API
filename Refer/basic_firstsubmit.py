import flask
app = flask.Flask(__name__) 
@app.route("/firstsubmit", methods=["POST"])
def first_submit():
    data = flask.request.get_json()
    if ( "customer_name" not in data ) or ( data['customer_name'] == '' ):
        errmsg = "customer_name is not provided in input. check and try again"
        resp =  {
                    "status": "Failed",
                    "message": errmsg
                }
        
        return flask.jsonify(resp), 501
    
    if ( "owner_id" not in data ) or ( data['owner_id'] == '' ):
        errmsg = "owner_id is not provided in input. check and try again"
        resp =  {
                    "status": "Failed",
                    "message": errmsg
                }
        
        return flask.jsonify(resp), 501
    if ( "lob" not in data ) or ( data['lob'] == '' ):
        errmsg = "lob is not provided in input. check and try again"
        resp =  {
                    "status": "Failed",
                    "message": errmsg
                }
        
        return flask.jsonify(resp), 501

    if ( "required_services" not in data ) or ( data['required_services'] == '') or (type(data['required_services']) != list ) :
        errmsg = "required_services is not provided in input. check and try again"
        resp =  {
                    "status": "Failed",
                    "message": errmsg
                }
        
        return flask.jsonify(resp), 501
    else:
    successmsg = "Successfully Initialized for the customer {} with owner id {} ".format(data["customer_name"], data["owner_id"] )
    resp =  {
                    "status": "Initializing",
                    "message": successmsg
                }
    
    return flask.jsonify(resp), 200

# Here have to add the get status api


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port='5001')
    