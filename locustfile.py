from locust import HttpLocust, TaskSet, task


class TalentMAPResearchTasks(TaskSet):
    @task(10)
    def list_all_positions(self):
        self.client.get("/api/v1/position/")

    @task(10)
    def search_position_grades(self):
        self.client.get("/api/v1/position/?grade__code__in=05,06", name="/api/v1/position/?grade__code__in=code,code")

    @task(10)
    def search_position_skills(self):
        self.client.get("/api/v1/position/?skill__code__in=05,06", name="/api/v1/position/?skill__code__in=code,code")

    @task(1)
    def search_free_text(self):
        self.client.get("/api/v1/position/?q=german", name="/api/v1/position/?q=fts")


class TalentMAPLocust(HttpLocust):
    task_set = TalentMAPResearchTasks
    min_wait = 5000
    max_wait = 15000
