def check_quiet_print(quiet,msg,end='\n'):
    if not quiet:
        print(msg,end=end)