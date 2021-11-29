import sys

import streamlit as st
import os
from api.generator import API


def display_result(api_instance, syntax):
    """ display & save the python syntax results
     :return True if the file saved"""
    if syntax is not None:
        st.code(syntax, language='python')
        save_python_code = st.checkbox(label='Save Result')
        if save_python_code:
            current_selection = st.radio('Folder location: ', ('Default (Project Folder)', 'User Path'))
            st.write(f'You selected {current_selection}.')
            if 'User Path' in current_selection:
                path = st.text_input(label='Path')
                file_name = st.text_input(label='Name')
                path.replace('\\', '/')
                save = st.checkbox(label='Save Python Syntax')
                if save:
                    with open(f'{path}/{file_name}.py', 'w') as locust_file:
                        locust_file.write(str(syntax))
                        locust_file.close()
                        st.write(f'Folder Location: {path}/{file_name}.py')

            else:
                save = st.checkbox(label='Save Python Syntax')
                if save:
                    if api_instance[0].performance:
                        path = f'{api_instance[2]}\\locust_run.py'
                    else:
                        path = f'{api_instance[2]}\\api_run.py'

                    with open(path, 'w') as locust_file:
                        locust_file.write(str(syntax))
                        locust_file.close()
                        st.write(path)
                        return True


def pre_conditions(main_path):
    """ get basic rules from the user
     :return api instance, count of services and main folder path"""
    st.set_page_config(layout="wide")
    st.title("Performance Testing App")
    # side bar options
    services = st.sidebar.number_input(label='Count of Services', step=1)
    generate_type = st.sidebar.radio(label='Generate Type', options=('Performance', 'Rest-API'))
    st.sidebar.markdown(f'You Selected {generate_type}.')

    # initiate the API object by user generator selection
    if 'Performance' in generate_type:
        return API(performance=True), services, main_path
    else:
        return API(), services, main_path


def set_port(domain):
    """ :return the default port by url type """
    if 'http' not in domain:
        st.error("Please put a full url that include http:// or https://")
        return
    port = 'Port: '
    if 'https' in domain:
        return st.text_input(port, 443)
    elif 'http' in domain:
        return st.text_input(port, 80)
    else:
        return st.text_input(port, 8080)


def prepare_data(api_instance):
    # TODO: add description
    domain = st.text_input(label='Domain / Host:')
    st.container()
    if len(domain) > 0:
        port = set_port(domain=domain)
    else:
        port = ''
    params = None
    headers = None
    body = None
    expected_status_code = None
    count = 1
    services_data = []
    """ start to create html containers """
    while count <= api_instance[1]:
        with st.expander(f'Service {count}'):
            """ set api method """
            method = st.selectbox(label=F'Request Type Service ({count})',
                                  options=('GET', 'POST', 'PUT', 'DELETE', 'PATCH'))

            """ set api resource """
            resource = st.text_input(f'Resource / Route service ({count}) ')

            """ set api parameters """
            params_cb = st.checkbox(label=f'Params service ({count}): ')
            if params_cb:
                st.markdown('Params valid example: ')
                st.json(api_instance[0].get_params_example)
                params = st.text_input(f'Set your params service ({count}): ')
                if len(params) > 0:
                    st.write('Your params object is: ')
                    st.json(params)

            """ set api headers """
            headers_cb = st.checkbox(label=f'Headers service ({count}): ')
            if headers_cb:
                st.markdown('Headers valid example: ')
                st.json(api_instance[0].get_headers_example)
                headers = st.text_input(f'Set your headers service ({count}): ')
                if len(headers) > 0:
                    st.write('Your headers object is: ')
                    st.json(headers)

            """ set api body """
            body_cb = st.checkbox(label=f'Body service ({count}): ')
            if body_cb:
                st.markdown('Body valid example: ')
                st.json(api_instance[0].get_body_example)
                body = st.text_input(f'Set your body service ({count}): ')
                if len(body) > 0:
                    st.write('Your body object is: ')
                    st.json(body)
            """ add results the services data list """

            if not api_instance[0].performance:
                expected_status_code = st.text_input(f'Expected Status Code service ({count}):')
                if len(expected_status_code) <= 2:
                    st.error(f'Please add expected status code in service ({count})')
            services_data.insert(count - 1, (method, resource, params, headers, body, count, expected_status_code))
        count += 1

    code = show_syntax(api_instance, domain, port, services_data)
    saved = display_result(api_instance, code)
    return saved, domain, port


def show_syntax(api_instance, domain, port, services_data):
    # TODO: add description
    show_python_syntax = st.checkbox(label=f'Show Python Syntax')
    if show_python_syntax and len(services_data) > 0:
        if len(domain) == 0:
            st.error(f'Domain field cannot be null {domain} ')
        code = api_instance[0].get_start_class
        for service in services_data:
            if len(service[1]) == 0:
                st.error(f'Resource field cannot be null {service[1]} ({service[5]})')

            else:
                method = service[0].lower()
                name = f"{method}{service[1].replace('.', '_').replace('/', '_').replace('-', '_')}"
                code += api_instance[0].set_method(method=method, resource=service[1],
                                                   params=service[2],
                                                   headers=service[3],
                                                   body=service[4], name=name, domain=f"{domain}:{port}",
                                                   expected_status_code=service[6])
        if not api_instance[0].performance:
            return f"{code}{api_instance[0].expected_status_code_method}"

        else:
            return code


def run_script(res_obj, api_instance):
    # TODO: add description
    if res_obj[0]:
        run_time = st.text_input(label="Run Time in Seconds (use only in command-line mode)")
        run_web_ui = st.button('Run Script in Web-UI')
        run_headless = st.button('Run Script in Command Line')
        if run_web_ui:
            if api_instance[0].performance:
                """ create locust performance ui """
                host = res_obj[1]
                if len(res_obj) > 0:
                    host += f":{res_obj[2]}"
                st.write("Your App start, click on the link below")
                st.markdown(""" http://localhost:8089 """)
                os.system(f'locust -f locust_run.py --config master.conf --host={host}')

            else:
                """ create api requests and present the results with allure report """
                st.markdown("1. Running...")
                os.system(f'py.test api_run.py --alluredir=tmp/allure_results')
                st.markdown("2. Finish with success...")
                os.system(f'allure serve tmp/allure_results')
                os.system(f'close')

        elif run_headless:
            if api_instance[0].performance:
                """ create locust performance ui """
                host = res_obj[1]
                if len(res_obj) > 0:
                    host += f":{res_obj[2]}"
                    st.write("Your App start, Look at your command-line")
                    os.system(f'locust -f locust_run.py --headless --host={host} -t {run_time}')


def run_app(main_path):
    api = pre_conditions(main_path=main_path)
    res = prepare_data(api_instance=api)
    run_script(res, api)
