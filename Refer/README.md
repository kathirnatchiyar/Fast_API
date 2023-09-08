# service_deployer_api
This is the service deployer to install services wich ar requested by PMT through my API



# API to Submit a job
=========================

URL: http://<IP>:5001/firstsubmit
Input data: '{
                "customer_name": "text",
                "owner_id": "18",
                "lob": "GL",
                "required_services" : ["DB", "WF", "RATING", "UI/UX" ]
            }'

Response data: '{
                    "status": "Initializing / In-Progress / Completed / Failed",
                    "message": "Success or Error message if any"
                }'


# API to get an existing job status
===================================

URL: http://<IP>:5001/getstatus
Input data: '{
                "customer_name": "text",
                "owner_id": "18",
                "lob": "GL",
                "required_services" : ["DB", "WF", "RATING", "UI/UX" ]
            }'

Response data: '{
                    "status": "Initializing / In-Progress / Completed / Failed",
                    "message": "Success or Error message if any"
                    "progress": "10%"
                }'
