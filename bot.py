import re

def get_dt_columns_info(df):
    # Get the column names and their value types
    column_types = df.dtypes
    # Convert the column_types Series to a list
    column_types_list = column_types.reset_index().values.tolist()
    infos = ""
    # Print the column names and their value types
    for column_name, column_type in column_types_list:
        infos += f"{column_name} ({column_type}), "
    return infos

def extract_code(response):
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        return matches[-1]
    else:
        return None

def filter_rows(text):
    # Split the input string into individual rows
    lines = text.split('\n')
    filtered_lines = [line for line in lines if "pd.read_csv" not in line and "pd.read_excel" not in line and ".show()" not in line]
    filtered_text = '\n'.join(filtered_lines)
    
    return filtered_text
