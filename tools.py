import pandas as pd


def run_excel_formula(formula_string:str, test_case_data:dict):
    try:

        data = test_case_data['data']

        if formula_string.startswith('='):
            formula_strin = formula_string[1:]
        
        for cell, value in data.items():
            if isinstance(value, str):
                formula_string = formula_string.replace(cell, f'{value}')
            else:
                formula_string = formula_string.replace(cell, f'{value}')
            
        formula_string = formula_string.replace('&', '+').replace('CONCATENATE(','(').replace('CONCAT(', '(')

        if 'CONCAT' in formula_string.upper():
            formula_string = ' + '.join(formula_string.strip('()').upper().replace('CONCAT','').split(','))
        
        result = pd.eval(formula_string)

        if str(result) == str(test_case_data['expected_output']):
            return {"correct": True, "output": f"Correct! The formula produced the expected result: {result}"}
        else:
            return {"correct": False, "output": f"Your formula produced '{result}', but the expected output was '{test_case['expected_output']}'."}

    except Exception as e:
        # Handle errors in formula execution
        return {"correct": False, "output": f"There was an error executing your formula: {e}"}
