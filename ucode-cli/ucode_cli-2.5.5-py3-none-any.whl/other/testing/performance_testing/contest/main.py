import random
import time

from locust import HttpUser, task, between

from other.common.database.variable.ucode_student_user_token import UCODE_STUDENT_USER_TOKEN


class UcodeUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_ucode_vn(self):
        token = UCODE_STUDENT_USER_TOKEN[random.randint(0, len(UCODE_STUDENT_USER_TOKEN) - 1)]
        self.client.headers.update({'access-token': token})
        self.client.get('/api/problems?page=1&pageSize=12')
        # self.client.get('api/lesson-item/4107/question')
        # self.client.get('/api/home/footer')
        # time.sleep(1)

    # @task
    # def api_submit_question(self):
    #     quiz_id = 4680
    #     start_question = 47886
    #     num_of_question = 25
    #     try:
    #         token = UCODE_STUDENT_USER_TOKEN[random.randint(0, len(UCODE_STUDENT_USER_TOKEN) - 1)]
    #         self.client.headers.update({'access-token': token})
    #         for i in range(20):
    #             draft_response = self.client.post(f"/api/learning/lesson/{quiz_id}/submit-quiz",
    #                                               json={"list_answers": [], "draft": True},
    #                                               name='draft')
    #             time.sleep(1)
    #         submission_id = draft_response.json()['data']['submission_id']
    #         self.client.post(f"/api/learning/lesson/{quiz_id}/submit-quiz", json={
    #             "list_answers": [{"question_id": start_question + i, "user_answer": "0"}
    #                              for i in range(num_of_question)],
    #             "draft": False, "submission_id": submission_id}, name='submit')
    #     except Exception:
    #         print('error')
