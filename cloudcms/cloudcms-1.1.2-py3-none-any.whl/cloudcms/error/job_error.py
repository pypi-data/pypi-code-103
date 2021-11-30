class JobError(RuntimeError):
    
    def __init__(self, jobId):
        message = "Job Failed: " + jobId
        super(JobError, self).__init__(message)
