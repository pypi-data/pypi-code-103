"""
Schedule DB SchedulerManager
실질적인 스캐줄 객체
"""
import functools
import logging

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


class MainScheduler:

    def __init__(self, name: str = "default"):
        # 스캐줄 생성
        self.name = name
        self.schedule = BackgroundScheduler()
        logger.info(f"{self.name} 스케줄러 Manager init")

    def create_job(self, func, trigger: str = "cron", schedule_id: str = None, **schedule_time):
        """
        반복적으로 실행할 작업 생성
        :param func: 실행할 함수
        :param trigger: 스케줄러 트리거 (cron, interval)
        :param schedule_id: str
        :param schedule_time: dict 형식의 시간 인자 - cron 참고
        :return:
        """
        # id 미기입시
        if schedule_id is None:
            id = f"{func.__module__}_{func.__name__}"
            self.schedule.add_job(func, trigger, id=id, **schedule_time)
            logger.info(f"{self.name} 스케줄러 create_job : {id} - {trigger}({schedule_time})")
        else:
            self.schedule.add_job(func, trigger, id=schedule_id, **schedule_time)
            logger.info(f"{self.name} 스케줄러 create_job : {schedule_id} - {trigger}({schedule_time})")

    def delete_job(self, schedule_id: str):
        """
        스케줄에 등록되어 있는 작업을 제거
        :param schedule_id: 스케줄 id
        :return:
        """
        self.schedule.resume_job(schedule_id)
        logger.info(f"{self.name} 스케줄러 delete_job: {schedule_id}")

    def run(self):
        self.schedule.start()
        logger.info(f"{self.name} 스케줄러 Run")
#
#
# # args 사용 불가 - 중요!
# def add_schedule(func=None, **decorator_base_kwargs):
#     # 속성을 미기입 - > decorator 호출
#     if func:
#         print(f"add_schedule func - {type(func)}", flush=True)
#         return ScheduleDecorators(func, **decorator_base_kwargs)
#     # 속성을 기입 - > wrapper 로 감싼후 decorator 호출
#     else:
#         # 아무 인자도 들어오지 않음
#         def base_wrapper(function):
#             # 이중 Decorator 해결
#             wrapped = ScheduleDecorators(function, **decorator_base_kwargs)()
#             return wrapped
#
#         return base_wrapper
#
#
# # 실행 시 에만 동작
# class ScheduleDecorators(object):
#     scheduler = MainScheduler('decorators scheduler')
#
#     # Decorator 생성
#     # args 사용 금지 - 불가능
#     def __init__(self, func, **init_kwargs):
#         self.func = func
#         self.args = init_kwargs
#
#     # Decorator 호출
#     def __call__(self):
#         decorator_self = self
#         logger.info(f"scheduler({self.scheduler.name}) add job {self.func.__name__} - {self.args}")
#
#         # 스캐줄러 등록
#         self.scheduler.create_job(self.func, **self.args)
#
#         # 함수 Decorator 실행
#         def wrapper(*args, **kwargs):
#             function = self.func(*args, **kwargs)
#             return function
#
#         return wrapper

#
# # 실행 시 에만 동작
# class ScheduleDecorators(object):
#     scheduler = MainScheduler('decorators scheduler')
#
#     # Decorator 생성
#     # args 사용 금지 - 불가능
#     def __init__(self, **init_kwargs):
#         self.kargs = init_kwargs
#         # self.scheduler.create_job()
#
#     def __call__(self, fn):
#         @functools.wraps(fn)
#         def decorated(*args, **kwargs):
#             print()
#             print("In my decorator before call, with arg %s" % self.arg)
#             result = fn(*args, **kwargs)
#             print("In my decorator after call, with arg %s" % self.arg)
#             return result
#
#         return decorated
#
#     # # Decorator 호출
#     # def __call__(self):
#     #     logger.debug(f"scheduler({self.scheduler.name}) add job {self.func.__name__} - {self.args}")
#     #
#     #     # 스캐줄러 등록
#     #     # self.scheduler.create_job_method(self.func, self.func.__name__, self.scheduler, **self.args)
#     #
#     #     # 함수 Decorator 실행
#     #     def wrapper(*args, **kwargs):
#     #         function = self.func(*args, **kwargs)
#     #         return function
#     #
#     #     return wrapper
#
#
# class MyDecorator(object):
#     def __init__(self, **kwargs):
#         self.kwargs = kwargs
#         print(kwargs)
#
#     def __call__(self, fn):
#         @functools.wraps(fn)
#         def decorated(*args, **kwargs):
#             print()
#             print("In my decorator before call, with arg %s" % self.arg)
#             result = fn(*args, **kwargs)
#             print("In my decorator after call, with arg %s" % self.arg)
#             return result
#
#         return decorated
# #
# # # 모듈 수준의 스캐줄러 생성
# # module_scheduler = MainScheduler('module_scheduler')
# #
# #
# # def schedule_start():
# #     module_scheduler.run()
# #
# #
# # # args 사용 불가 - 중요!
# # def add_schedule(func=None, **decorator_base_kwargs):
# #     # 속성을 미기입 - > decorator 호출
# #     if func:
# #         print(f"add_schedule func - {type(func)}", flush=True)
# #         return schedule_decorators(func, **decorator_base_kwargs)
# #     # 속성을 기입 - > wrapper 로 감싼후 decorator 호출
# #     else:
# #         # 아무 인자도 들어오지 않음
# #         def base_wrapper(function):
# #             # 이중 Decorator 해결
# #             wrapped = schedule_decorators(function, **decorator_base_kwargs)()
# #             return wrapped
# #
# #         return base_wrapper
# #
