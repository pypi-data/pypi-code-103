auth_success = 'OK\r\n'
auth_fail = 'ERROR 11 AUTHENTICATION FAILED\r\n'
auth_fail_version = 'ERROR 3 UNSUPPORTED INTERFACE VERSION\r\n'

getapinfo_unknown_point = 'ERROR 10 UNKNOWN ACCESS POINT\r\n'

setapinfo_success = 'OK\r\n'
setapinfo_incorrect_point_num = 'OK\r\n'
setapinfo_incorrect_state = 'ERROR 6 SYNTAX ERROR\r\n'

subscribe_success = 'OK\r\n'

event_ce_mask_elements = {'NORMAL': 30,
                           'LOCKED': 31,
                           'UNLOCKED': 32,
                           'EXTERNAL': 2,
                           'INTERNAL': 1}

# time, status, point_number
event_ce_point_status_response_mask = 'EVENT_CE "{}" {} {} 0 0 UNKNOWN\r\n'

# Time, side, wiegand, rfid_number
event_ce_rfid_read_response_mask = 'EVENT_CE "{}" 10 1 0 {} {} {}\r\n'

point_status_mask = 'APINFO ID {} NAME "GATE-EXIT" ZONEA 0 ZONEB 0 STATE {} OPENED\r\n'
