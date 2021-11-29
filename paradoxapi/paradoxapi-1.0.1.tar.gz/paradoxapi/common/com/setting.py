
def setting_try(p_d):
    #
    k = 'pld_master.com_djq%5cu#-jeq15abg$z9_i#_w=$o88m!*alpbedlbat8cr74sd'
    dec_str = ""
    for i, j in zip(p_d.split("_")[:-1], k):
        temp = chr(int(i) - ord(j))
        dec_str += temp
    return dec_str