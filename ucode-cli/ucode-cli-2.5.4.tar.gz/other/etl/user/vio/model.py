class VioUser:
    # all
    vio_username: str = ''
    vio_password: str = ''
    full_name: str = ''
    ms_username: str = ''
    ms_password: str = ''
    gender: str = ''
    dob: str = ''
    address: str = ''
    # student
    student_class_name: str = ''
    student_code: str = ''
    parent_email: str = ''
    parent_phone_number: str = ''
    vio_parent_username: str = ''
    vio_parent_password: str = ''
    vio_parent_username_2: str = ''
    vio_parent_password_2: str = ''
    # teacher
    email: str = ''
    phone_number: str = ''
    identity_card_number: str = ''
    teacher_subject: str = ''
    teacher_class_name: str = ''
    # rank
    contest_count_wrong_answer: int = -1
    contest_count_correct_answer: int = -1
    contest_duration: int = -1
    contest_rank: int = -1
    # extra
    type: str = ''
    school_level: str = ''
    school_name: str = ''
    student_class: str = ''
    province_name: str = ''
    district_name: str = ''

    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def get_header_str(cls):
        #     return "'vio_username','vio_password','full_name','ms_username','ms_password','gender','dob','address','student_class_name','student_code','parent_email','parent_phone_number','vio_parent_username', 'vio_parent_password', 'vio_parent_username_2', 'vio_parent_password_2', 'email', 'phone_number', 'identity_card_number', 'teacher_subject', 'teacher_class_name', 'contest_count_wrong_answer', 'contest_count_correct_answer', 'contest_duration', 'contest_rank', 'type', 'school_level', 'school_name','student_class', 'province_name', 'district_name'"
        return "vio_username,vio_password,full_name,ms_username,ms_password,gender,dob,address,student_class_name,student_code,parent_email,parent_phone_number,vio_parent_username, vio_parent_password, vio_parent_username_2, vio_parent_password_2, email, phone_number, identity_card_number, teacher_subject, teacher_class_name, contest_count_wrong_answer, contest_count_correct_answer, contest_duration, contest_rank, type, school_level, school_name,student_class, province_name, district_name"

    def __str__(self):
        return f"`{self.vio_username}`,`{self.vio_password}`,`{self.full_name}`,`{self.ms_username}`,`{self.ms_password}`,`{self.gender}`,`{self.dob}`,`{self.address}`,`{self.student_class_name}`,`{self.student_code}`,`{self.parent_email}`,`{self.parent_phone_number}`,`{self.vio_parent_username}`,`{self.vio_parent_password}`,`{self.vio_parent_username_2}`,`{self.vio_parent_password_2}`,`{self.email}`,`{self.phone_number}`,`{self.identity_card_number}`,`{self.teacher_subject}`,`{self.teacher_class_name}`,{self.contest_count_wrong_answer},{self.contest_count_correct_answer},{self.contest_duration},{self.contest_rank},`{self.type}`,`{self.school_level}`,`{self.school_name}`,`{self.student_class}`,`{self.province_name}`,`{self.district_name}`"
        # return f"{self.vio_username},{self.vio_password},{self.full_name},{self.ms_username},{self.ms_password},{self.gender},{self.dob},{self.address},{self.student_class_name},{self.student_code},{self.parent_email},{self.parent_phone_number},{self.vio_parent_username},{self.vio_parent_password},{self.vio_parent_username_2},{self.vio_parent_password_2},{self.email},{self.phone_number},{self.identity_card_number},{self.teacher_subject},{self.teacher_class_name},{self.contest_count_wrong_answer},{self.contest_count_correct_answer},{self.contest_duration},{self.contest_rank},{self.type},{self.school_level},{self.school_name},{self.province_name},{self.district_name}"
