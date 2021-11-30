def __init__(hub):
    # Provides the ctx argument to all execution modules
    # which will have profile info from the account module
    hub.exec.azure.ACCT = ["request", "azure"]
