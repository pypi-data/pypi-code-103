import allure


def teststep_allure_step(step_desc, request_dict, response_dict, validate_list, extract_mapping, setup_hook_list, teardown_hook_list):
    @allure.step
    def hook_detail(**kv):
        pass

    def setup_hook(func_desc, parsed_func):
        @allure.step(func_desc)
        def assert_step():
            hook_detail(**parsed_func)

        return assert_step

    @allure.step
    def request_data(**kv):
        pass

    @allure.step
    def response_data(**kv):
        pass

    def validate_allure_step(valiate_desc, validator_dict):
        @allure.step
        def validate_detail(**kv):
            pass

        @allure.step(valiate_desc)
        def assert_step():
            validate_detail(**validator_dict)

        return assert_step

    @allure.step
    def extract_values(**kv):
        pass

    def teardown_hook(func_desc, parsed_func):
        @allure.step(func_desc)
        def assert_step():
            hook_detail(**parsed_func)

        return assert_step

    @allure.step(step_desc)
    def step_function():
        with allure.step("setup_hooks"):
            for hook_dict in setup_hook_list:
                func_desc, parsed_func = list(hook_dict.items())[0]
                setup_hook(func_desc, parsed_func)()
        request_data(**request_dict)
        response_data(**response_dict)
        with allure.step("validate_list"):
            for desc, detail, test_result in validate_list:
                if "{" in desc:
                    desc = desc.replace("{", "<")
                    desc = desc.replace("}", ">")
                validate_allure_step(desc, detail)()
        extract_values(**extract_mapping)
        with allure.step("teardown_hooks"):
            for hook_dict in teardown_hook_list:
                func_desc, parsed_func = list(hook_dict.items())[0]
                teardown_hook(parsed_func.get("func_name"), parsed_func)()

    step_function()

