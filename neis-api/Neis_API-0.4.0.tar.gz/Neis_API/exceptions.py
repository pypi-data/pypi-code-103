def check_status_code(status_code):
    if status_code == "ERROR-300":
        raise Error300()
    elif status_code == "ERROR-290":
        raise Error290()
    elif status_code == "ERROR-333":
        raise Error333()
    elif status_code == "ERROR-336":
        raise Error336()
    elif status_code == "ERROR-337":
        raise Error337()
    elif status_code == "ERROR-500":
        raise Error500()
    elif status_code == "ERROR-600":
        raise Error600()
    elif status_code == "ERROR-601":
        raise Error601()
    elif status_code == "INFO-300":
        raise Info300()
    elif status_code == "INFO-200":
        raise Info200()
    return


class Error300(Exception):
    def __init__(self):
        super().__init__("필수 값이 누락되어 있습니다. 요청인자를 참고 하십시오.")
        return


class Error290(Exception):
    def __init__(self):
        super().__init__("인증키가 유효하지 않습니다. 인증키가 없는 경우, 홈페이지에서 인증키를 신청하십시오.")
        return


class Error333(Exception):
    def __init__(self):
        super().__init__("요청위치 값의 타입이 유효하지 않습니다.요청위치 값은 정수를 입력하세요.")
        return


class Error336(Exception):
    def __init__(self):
        super().__init__("데이터요청은 한번에 최대 1,000건을 넘을 수 없습니다.")
        return


class Error337(Exception):
    def __init__(self):
        super().__init__("일별 트래픽 제한을 넘은 호출입니다. 오늘은 더이상 호출할 수 없습니다.")
        return


class Error500(Exception):
    def __init__(self):
        super().__init__("서버 오류입니다. 지속적으로 발생시 홈페이지로 문의(Q&A) 바랍니다.")
        return


class Error600(Exception):
    def __init__(self):
        super().__init__("데이터베이스 연결 오류입니다. 지속적으로 발생시 홈페이지로 문의(Q&A) 바랍니다.")
        return


class Error601(Exception):
    def __init__(self):
        super().__init__("SQL 문장 오류 입니다. 지속적으로 발생시 홈페이지로 문의(Q&A) 바랍니다.")
        return


class Info300(Exception):
    def __init__(self):
        super().__init__("관리자에 의해 인증키 사용이 제한되었습니다.")
        return


class Info200(Exception):
    def __init__(self):
        super().__init__("해당하는 데이터가 없습니다.")
        return
