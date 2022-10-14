import re
import argparse
import xmltodict
import pandas as pd


def clear(s: str):
    return re.sub('<a href="(.*)">(.*)</a>', r'\2: \1', s)


def process_testcase(testcase: dict, testcase_section: str):
    if testcase.get('status') is not None:
        v = testcase.get('status')
        if v == '2':
            v = 'Review'
        elif v == '6':
            v = 'Ready'
        else:
            v = 'Design'
        l_statuses.append(v)
    else:
        l_statuses.append('')

    if testcase.get('@name') is not None:
        l_name.append(testcase.get('@name'))
    else:
        l_name.append('')

    l_sections.append(testcase_section)

    precond_summ = ''
    if testcase.get('summary') is not None:
        precond_summ = testcase.get('summary')

    if testcase.get('preconditions') is not None:
        precond_summ = precond_summ + testcase.get('preconditions')
    l_section_desc_Precond_summarys.append(clear(precond_summ))

    if testcase.get('execution_type'):
        v = testcase.get('execution_type')
        if v == '1':
            v = 'Manual'
        else:
            v = 'Automatic'
        l_exc_type.append(v)
    else:
        l_exc_type.append('')

    if testcase.get('importance') is not None:
        v = testcase.get('importance')
        if v == '1':
            v = 'Low'
        elif v == '2':
            v = 'Medium'
        elif v == '3':
            v = 'High'
        l_importance.append(v)
    else:
        l_importance.append('')

    try:
        for c, i in enumerate(testcase.get('steps').get('step')):
            l_steps.append(i.get('actions'))
            l_expect_res.append(i.get('expectedresults'))
            if c > 0:
                l_name.append('')
                l_sections.append('')
                l_exc_type.append('')
                l_statuses.append('')
                l_importance.append('')
                l_section_desc_Precond_summarys.append('')
    except AttributeError:
        l_steps.append('')
        l_expect_res.append('')



def process_str(input_tests: dict, testcase_section: str):
    for k, tests in input_tests.items():
        if k in ['testsuite', 'testcase']:

            if type(tests) == list:
                for test in tests:
                    if test.get('testcase') is None and\
                            test.get('testsuite') is None:
                        process_testcase(test, testcase_section)
                    elif test.get('testcase'):
                        testcase_section = \
                            f"{testcase_section}>Sub section"
                        for testcase in test.get('testcase'):
                            if type(testcase) is str:
                                process_str(test, testcase_section)
                                break
                            else:
                                process_testcase(testcase, testcase_section)
                    else:
                        print(test.keys())
                        print('here')
                        exit(1)
                        # process_testsuite(test, testcase_section)
            else:
                if k == 'testcase':
                    process_testcase(tests, testcase_section)
                else:
                    if tests.get('testcase') is not None:
                        testcase_section = \
                            f"{testcase_section}>{tests.get('@name')}"

                        for test in tests.get('testcase'):
                            if type(test) is str:
                                process_str(tests, testcase_section)
                                break
                            else:
                                process_testcase(test, testcase_section)
                    if tests.get('testsuite') is not None:
                        for test in tests.get('testsuite'):
                            if type(test) is str:
                                process_str(tests, testcase_section)
                                break
                            else:
                                testcase_section = \
                                    f"{testcase_section}>{tests.get('@name')}"
                                process_testsuite(
                                        test, testcase_section)


def process_testsuite(
        rot_testsuite: dict, rot_testsuite_name: str):
    if rot_testsuite.get('testcase') is not None:
        for testcase in rot_testsuite.get('testcase'):
            if type(testcase) is str:
                process_str(rot_testsuite, rot_testsuite_name)
                break
            else:
                process_testcase(testcase, rot_testsuite_name)

    if rot_testsuite.get('testsuite') is not None:
        check = False
        for testsuite in rot_testsuite.get('testsuite'):
            if type(testsuite) is str:
                check = True
                break
            else:
                if testsuite.get('testcase') is not None:
                    for testcase_ in testsuite.get('testcase'):
                        testcase_section = \
                             f"{rot_testsuite_name}>{testsuite.get('@name')}"
                        if type(testcase_) == str:
                            process_str(testsuite, testcase_section)
                            break
                        else:
                            process_testcase(testcase_, testcase_section)

                if testsuite.get('testsuite') is not None:
                    for testsuite_ in testsuite.get('testsuite'):
                        if type(testsuite_) is dict:
                            testcase_section = \
                                f"{rot_testsuite_name}>"\
                                f"{testsuite.get('@name')}>"\
                                f"{testsuite_.get('@name')}"
                            process_testsuite(
                                    testsuite_, testcase_section)
                        elif type(testsuite_) is str:
                            testcase_section = \
                             f"{rot_testsuite_name}>{testsuite.get('@name')}"
                            process_str(testsuite, testcase_section)
                            break
        if check:
            process_str(rot_testsuite, rot_testsuite_name)


parser = argparse.ArgumentParser()
parser.add_argument(
        "-i", "--input", help="Export a file from testlink xml format")
args = parser.parse_args()

try:
    d_rot_testsuits = dict()
    with open(args.input, "r", encoding='utf-8') as xml_file:
        d_rot_testsuits = xmltodict.parse(xml_file.read()).get('testsuite')
    xml_file.close()

    if d_rot_testsuits.get('testcase'):
        l_name = []
        l_sections = []
        l_section_desc_Precond_summarys = []
        l_exc_type = []
        l_importance = []
        l_steps = []
        l_expect_res = []
        l_statuses = []
        for testcase in d_rot_testsuits.get('testcase'):
            if type(testcase) is str:
                process_str(d_rot_testsuits, d_rot_testsuits.get('@name'))
                break
            else:
                process_testcase(testcase, d_rot_testsuits.get('@name'))

        d = {
            'Automation Type': l_exc_type,
            'Preconditions': l_section_desc_Precond_summarys,
            'Priority': l_importance,
            'Section': l_sections,
            'Status': l_statuses,
            'Steps (Expected Result)': l_expect_res,
            'Steps (Step)': l_steps,
            'Title': l_name,
        }
        df = pd.DataFrame(d)

        df.to_csv('output_rot_testcases.csv', encoding='utf-8')
        print('output_rot_testcases.csv')

    if d_rot_testsuits.get('testsuite'):
        for rot_testsuite in d_rot_testsuits.get('testsuite'):
            l_name = []
            l_sections = []
            l_section_desc_Precond_summarys = []
            l_exc_type = []
            l_importance = []
            l_steps = []
            l_expect_res = []
            l_statuses = []

            if type(rot_testsuite) is str:
                process_str(d_rot_testsuits, d_rot_testsuits.get('@name'))
                break
            else:
                process_testsuite(rot_testsuite, rot_testsuite.get('@name'))
            d = {
                'Automation Type': l_exc_type,
                'Preconditions': l_section_desc_Precond_summarys,
                'Priority': l_importance,
                'Section': l_sections,
                'Status': l_statuses,
                'Steps (Expected Result)': l_expect_res,
                'Steps (Step)': l_steps,
                'Title': l_name,
            }
            df = pd.DataFrame(d)
            file_name = re.sub(' ', '_', f"{rot_testsuite.get('@name')}")
            df.to_csv(f'output_{file_name}.csv', encoding='utf-8')
            print(f'output_{file_name}.csv')

except FileNotFoundError:
    print(f'error: the specified file "{args.input}" does not exist.')
