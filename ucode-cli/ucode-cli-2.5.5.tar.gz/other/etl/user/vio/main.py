import re

import pandas as pd
from pandas import DataFrame

from other.common import write_file
from other.common.file.list import get_files_in_folder, get_all_folders_in_folder
from other.etl import VioUser

rank_cacher = {}
regex_pattern = '24_01_2021\/(.*?)\/(.*?)\/(.+)\/'
input_folder = 'etl/user/vio/input_data/24_01_2021'
teacher_output = 'etl/user/vio/output_data/teacher.csv'
student_output = 'etl/user/vio/output_data/student.csv'
split_by_school = True


def create_student_from_df_row(df: DataFrame, row_num: int, file_name: str):
    student = VioUser()
    student.type = 'Student'
    student.province_name = 'Hà Nội'
    file_name = file_name.replace('\\', '/')
    regex_rs = re.findall(regex_pattern + '.+Khối([1-9])?', file_name)
    if regex_rs:
        regex_rs = regex_rs[0]
        student.district_name = regex_rs[0]
        student.school_level = regex_rs[1]
        student.school_name = regex_rs[2]
        student.student_class = regex_rs[3]

    student.vio_username = df['Tên đăng nhập'].tolist()[row_num]
    student.vio_password = df['Mật khẩu'].tolist()[row_num]
    student.full_name = df['Họ tên'].tolist()[row_num]
    student.ms_username = df['Tài khoản MS Teams'].tolist()[row_num]
    student.ms_password = df['Mật khẩu MS Teams'].tolist()[row_num]
    student.gender = df['Giới tính'].tolist()[row_num]
    student.dob = df['Ngày sinh'].tolist()[row_num]
    student.address = df['Địa chỉ'].tolist()[row_num]
    student.student_class_name = df['Lớp'].tolist()[row_num]
    student.student_code = df['Mã học sinh'].tolist()[row_num]
    student.parent_email = df['Email phụ huynh'].tolist()[row_num]
    student.parent_phone_number = df['Số điện thoại phụ huynh'].tolist()[row_num]
    student.vio_parent_username = df['Tài khoản phụ huynh thứ 1'].tolist()[row_num]
    student.vio_parent_password = df['Mật khẩu của tài khoản phụ huynh thứ 1'].tolist()[row_num]
    student.vio_parent_username_2 = df['Tài khoản phụ huynh thứ 2'].tolist()[row_num]
    student.vio_parent_password_2 = df['Mật khẩu của tài khoản phụ huynh thứ 2'].tolist()[row_num]
    if student.vio_username in rank_cacher.keys():
        contest = rank_cacher[student.vio_username]
        student.contest_count_correct_answer = contest['contest_count_correct_answer']
        student.contest_count_wrong_answer = contest['contest_count_wrong_answer']
        student.contest_duration = contest['contest_duration']
        student.contest_rank = contest['contest_rank']
        del rank_cacher[student.vio_username]
    return student


def create_teacher_from_df_row(df: DataFrame, row_num: int, file_name: str):
    teacher = VioUser()
    teacher.type = 'Teacher'
    teacher.province_name = 'Hà Nội'
    file_name = file_name.replace('\\', '/')
    regex_rs = re.findall(regex_pattern, file_name)
    if regex_rs:
        regex_rs = regex_rs[0]
        teacher.district_name = regex_rs[0]
        teacher.school_level = regex_rs[1]
        teacher.school_name = regex_rs[2]

    teacher.vio_username = df['Tên đăng nhập'].tolist()[row_num]
    teacher.vio_password = df['Mật khẩu'].tolist()[row_num]
    teacher.full_name = df['Họ tên'].tolist()[row_num]
    teacher.ms_username = df['Tên đăng nhập MS Teams'].tolist()[row_num]
    teacher.ms_password = df['Mật khẩu Ms Teams'].tolist()[row_num]
    teacher.gender = df['Giới tính'].tolist()[row_num]
    teacher.dob = df['Ngày sinh'].tolist()[row_num]
    teacher.address = df['Địa chỉ'].tolist()[row_num]
    teacher.email = df['Email'].tolist()[row_num]
    teacher.phone_number = df['Số điện thoại'].tolist()[row_num]
    teacher.identity_card_number = df['Số CMNTD'].tolist()[row_num]
    teacher.teacher_subject = str(df['Môn'].tolist()[row_num]).replace(',', '-')
    teacher.teacher_class_name = str(df['Lớp'].tolist()[row_num]).replace(',', '-')
    return teacher


def _load_df_from_xlsx_file(file_name: str):
    xls = pd.ExcelFile(file_name)
    df = xls.parse(0)  # first sheet
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def _insert_to_cache_from_rank_df(df: DataFrame, file_name: str):
    total_row = len(df)
    for row_num in range(total_row):
        rank_cacher.update({
            df['Tên đăng nhập'].tolist()[row_num]: {
                'contest_count_wrong_answer': df['Số câu sai'].tolist()[row_num],
                'contest_count_correct_answer': df['Số câu đúng'].tolist()[row_num],
                'contest_duration': df['Tổng số giây suy nghĩ'].tolist()[row_num],
                'contest_rank': df['Thứ hạng'].tolist()[row_num],
            }
        })


def _load_student_from_df(df: DataFrame, file_name: str):
    total_row = len(df)
    list_student = []
    for row_num in range(total_row):
        student = create_student_from_df_row(df=df, row_num=row_num, file_name=file_name)
        list_student.append(student)
    return list_student


def _load_teacher_from_df(df: DataFrame, file_name: str):
    total_row = len(df)
    list_teacher = []
    for row_num in range(total_row):
        teacher = create_teacher_from_df_row(df=df, row_num=row_num, file_name=file_name)
        list_teacher.append(teacher)
    return list_teacher


def _process_tecacher_xlsx_in_partition(partition_path: str):
    teacher_xlsx_files = get_files_in_folder(root_folder=partition_path)

    if split_by_school:
        teacher_output_by_parttion = teacher_output.replace('.csv',
                                                            partition_path
                                                            .replace(input_folder, '-')
                                                            .replace('/', '-')
                                                            + '.csv')
        write_file(file_path=teacher_output_by_parttion, content=VioUser.get_header_str() + '\n')
    for teacher_xlsx_file in teacher_xlsx_files:
        if any(e in teacher_xlsx_file for e in ['xếp', 'học']):
            continue
        print(teacher_xlsx_file)
        df = _load_df_from_xlsx_file(file_name=teacher_xlsx_file)
        list_teacher = _load_teacher_from_df(df=df, file_name=teacher_xlsx_file)
        write_file(file_path=teacher_output_by_parttion if split_by_school else teacher_output,
                   write_mode='a',
                   content=list_teacher,
                   is_list=True)


def _process_student_xlsx_in_partition(partition_path: str):
    student_xlsx_files = get_files_in_folder(root_folder=partition_path)
    rank_xlsx_files = get_files_in_folder(root_folder=partition_path)
    for rank_xlsx_file in rank_xlsx_files:
        if any(e in rank_xlsx_file for e in ['học', 'giáo', 'giao']):
            continue
        rank_df = _load_df_from_xlsx_file(file_name=rank_xlsx_file)
        _insert_to_cache_from_rank_df(df=rank_df, file_name=rank_xlsx_file)

    if split_by_school:
        student_output_by_parttion = student_output.replace('.csv',
                                                            partition_path
                                                            .replace(input_folder, '-')
                                                            .replace('/', '-')
                                                            + '.csv')
        write_file(file_path=student_output_by_parttion, content=VioUser.get_header_str() + '\n')
    for student_xlsx_file in student_xlsx_files:
        if any(e in student_xlsx_file for e in ['xếp', 'giáo', 'giao']):
            continue
        print(student_xlsx_file)
        df = _load_df_from_xlsx_file(file_name=student_xlsx_file)
        list_student = _load_student_from_df(df=df, file_name=student_xlsx_file)
        write_file(file_path=student_output_by_parttion if split_by_school else student_output,
                   write_mode='a',
                   content=list_student,
                   is_list=True)


def _process_partition(partition_path: str):
    _process_tecacher_xlsx_in_partition(partition_path=partition_path)
    _process_student_xlsx_in_partition(partition_path=partition_path)


def process():
    list_partition_path = get_all_folders_in_folder(root_folder=input_folder)
    if not split_by_school:
        write_file(file_path=teacher_output, content=VioUser.get_header_str() + '\n')
        write_file(file_path=student_output, content=VioUser.get_header_str() + '\n')
    for partition_path in list_partition_path:
        _process_partition(partition_path)


process()
