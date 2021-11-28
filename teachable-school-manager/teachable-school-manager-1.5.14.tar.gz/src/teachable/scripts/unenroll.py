# coding: utf8
import argparse
import logging
import logging.config
import enlighten
import sys


import pyexcel as px

from ..api import Teachable
from ..course import Course
from ..user import User


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Mass unenroll users from Excel or CSV file from a specified course.\
                                        Alternatively unenroll all users that have been enrolled for a certain amount \
                                        of days specified with -d option''',
                                     epilog="""---""")
    parser.add_argument('-i', '--input_file', nargs=1,
                        help='[Optional] Excel or CSV file. The only needed columns are \'fullname\' and \'email\' ')
    parser.add_argument('-c', '--courseId', type=str, nargs=1, help='[Optional] The id of the course they should be enrolled in')
    parser.add_argument('-d', '--days', help='''[Optional] Specifies the number of days after which a user will be unenrolled.\
                                                For instance -d 365 will unenroll every user that has been enrolled \
                                                for 366 days or more.
                                                IMPORTANT: This action cannot be recovered. Use at your own risk.''')
    args = parser.parse_args()

    if not args.courseId and not args.input_file and not args.days:
        print('ERROR - Please specify at least an argument\n')
        parser.print_help()
        sys.exit(2)

    return args


def unenroll_app(args):
    api = Teachable()
    logger = logging.getLogger(__name__)
    if args.courseId and args.input_file:
        course_id = args.courseId[0]
        input_file = args.input_file[0]
        records = px.get_records(file_name=input_file)
        for user in records:
            # search if the user with the given email exists
            if user['email'] != '':
                u = User(api, user['email'])
                course = Course(api, course_id)
                if u.exists:
                    resp = u.unenroll(course)
                    if 'message' in resp.keys():
                        logger.info(resp['message'])
                    else:
                        logger.info(u.name + ' unenrolled')
    elif args.days:
        all_users = api.get_all_users()
        manager = enlighten.get_manager()
        pbar = manager.counter(total=len(all_users), desc='Users', unit='users')
        user_status = {}
        for i in all_users:
            reportcard = i.reportcard
            for cid in reportcard:
                if cid != 'meta':
                    days_enrolled = reportcard[cid]['days_enrolled']
                    if days_enrolled > int(args.days):
                        course = Course(api, cid)
                        logger.info('Unenrolling {} from course {} (enrolled for {} days)'.format(i.name, course.name, days_enrolled))
                        #i.unenroll(course)
                        ### TODO - send email when unenrolling ###
            pbar.update()




def main():
    args = parse_arguments()
    unenroll_app(args)


if __name__ == '__main__':
    main()
