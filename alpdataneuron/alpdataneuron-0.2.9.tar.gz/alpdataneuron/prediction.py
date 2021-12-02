import requests

class PredictIssue():
    def __init__(self):

        self.active_tasks = []
        
    def predict(self, practice_area, data):

        from alpdataneuron.config_variables import API_TOKEN

        try:
            response = (requests.post("http://20.43.152.82:4000/prediction_API", headers={"x-access-token": API_TOKEN}, json={"apiToken": API_TOKEN, "practiceArea": practice_area, "data": data})).text
            
            if response == "Error: Authorization failed":
                status = "FAILURE"
                message = "Authorization Failed"
                task_id = None
            
            else:
                status = "SUCCESS"
                message = "Task initiated"
                task_id = response
        
        except:
            status = "FAILURE"
            task_id = None
            message = "Failed to connect to the server"

        if status == "SUCCESS":
            self.active_tasks.append(task_id)
        
        return {"status": status, "response": message, "task_id": task_id}
    
    def get_active_tasks(self):

        return self.active_tasks

    def get_results(self, task_id):

        from alpdataneuron.config_variables import API_TOKEN

        if task_id not in self.active_tasks:
            status = "FAILURE"
            message = "Task id does not exist"
            predicted_issues = None

        else:
            try:
                task_status = (requests.get("http://20.43.152.82:4000/prediction_results/"+task_id, headers={"x-access-token": API_TOKEN})).json()
                status = task_status["state"]

                if status == "AUTHORIZATION FAILURE":
                    status = "FAILURE"
                    message = "Authorization Failed"
                    predicted_issues = None
                
                elif status == "FAILURE":
                    message = "Task failed, the practice area name entered may be incorrect"
                    predicted_issues = None
                    self.active_tasks.remove(task_id)
                
                elif status == "PENDING":
                    message = "Task in queue"
                    predicted_issues = None
                
                else:
                    try:
                        predicted_issues = task_status["predicted_issues"]
                        message = "Task completed"
                        self.active_tasks.remove(task_id)
                    
                    except:
                        predicted_issues = None
                        status = "PENDING"
                        message = "Task in queue"
                
            except:
                status = "FAILURE"
                message = "Failed to connect to the server"
                predicted_issues = None

        return {"status": status, "response": message, "predicted_issues": predicted_issues}

    def task_wait(self, task_id):

        while True and task_id in self.active_tasks:
            result_status = self.get_results(task_id)
            if result_status["status"] == "SUCCESS":
                return result_status

            elif result_status["status"] == "FAILURE":
                return result_status

        return {"status": "FAILURE", "response": "Task id does not exist", "predicted_issues": None}