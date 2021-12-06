def checkOnly(str, flag):
    cnt = 0
    for s in str:
        if s=="_":
            cnt+=1
    if cnt==1: return True
    else: return False