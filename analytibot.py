from cat.mad_hatter.decorators import hook, tool
from cat.utils import get_static_url
from .parser import DataSetParser
from .bot import get_dt_columns_info, extract_code, filter_rows
import pandas as pd
import matplotlib.pyplot as plt
import chardet
import base64
import json

df = None

def interpret_code(response):
    if "```" in response:
        just_code = extract_code(response)
        if just_code.startswith("python"):
            just_code = just_code[len("python"):]
        just_code = filter_rows(just_code)
        exec(just_code)
        return True
    else:
        return False

@tool(return_direct=True)
def analyze_dataset(request, cat):
    """
    A plugin used to analyze a dataset when requested.
    The input is the data analysis phrase to perform for a desired dataset, it should start with something like 'Analyze the dataset for ...'
    """

    if df is None:
        return cat.llm("""Tell the user that no dataframe has been uploaded, so you can't make the visualization he's asking. 
            Ask him to please upload you csv/xlsx dataset file to begin""")

    response = cat.llm(f"""You are a great assistant at python data visualization creation.
        You should create: the code for the data visualization in python using pandas and matplotlib of a dataframe called "df".
        Besides, here are some requirements:
        1. The pandas dataframe is already loaded in the variable "df".
        2. Assert that the "df" variable is already loaded in the globals().
        3. YOU MUST NOT load the dataframe in the generated code!
        4. The code has to save the figure of the visualization in the path "cat/static/analytibot_plot.png" do not do the plot.show().
        5. Give the explainations along the code on how important is the visualization and what insights can we get
        6. If the user asks for suggestions of analysis just provide the possible analysis without the code.
        7. For any visualizations write only one block of code wrapped inside 3 of ` at start and 3 at end of the code.
        8. The available fields in the dataset "df" and their types are: {get_dt_columns_info(df)}
        
        Perform this analysis:
        {request}""")

    has_code = interpret_code(response)

    final_message = ""

    if has_code:
        final_message = f'<img alt="{request}" src="{get_static_url()}analytibot_plot.png" />{response.split("```")[-1]}'
    else:
        final_message = response

    return final_message

@hook
def before_rabbithole_splits_text(text: list, cat):
    
    is_dataset = text[0].metadata["source"] == "analytibot"

    global df

    if is_dataset:
        content = json.loads(text[0].page_content)
        df = pd.DataFrame(content)
        name = text[0].metadata["name"]
        cat.send_ws_message(f"""Dataset `{name}` uploaded correctly!
                It contains {df.shape[0]} Rows and {df.shape[1]} Columns where each column type are:
                [{get_dt_columns_info(df)}]""", "chat")

    return text[1:] if is_dataset else text

@hook
def rabbithole_instantiates_parsers(file_handlers: dict, cat) -> dict:
    new_file_handlers = file_handlers

    new_file_handlers["text/csv"] = DataSetParser()
    new_file_handlers["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"] = DataSetParser()

    return new_file_handlers
