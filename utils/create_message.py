from typing import List
import json
import prettytable as pt
import pandas as pd
from jinja2 import Template
from datetime import datetime


def create_table(header: list, body: List):
    table_meteo = pt.PrettyTable(header)
    table_meteo.align = 'c'

    for row in body:
        table_meteo.add_row(row)

    return table_meteo


def create_pandas(body: dict):
    data = {'link': [], 'status': [], 'parent': []}
    for link in body:
        data['link'].append(link)
        data['status'].append(str(body[link]['status_cod']))
        data['parent'].append(body[link]['parent'])
    pd.options.display.max_colwidth = 200
    pd.options.display.max_rows = 1000
    pd.options.display.max_columns = 3
    pd.set_option("expand_frame_repr", False)
    df = pd.DataFrame(data=data)
    return df


def create_html_template(err_404, timeout_err, any_err):
    with open('template/mail_template.html') as html_f:
        html_template = html_f.read()

        # Словарь данных
        data_404 = err_404
        data_timeout = timeout_err
        data_any = any_err
        # Создание объекта шаблона
        template = Template(html_template)

        # Заполнение шаблона данными
        html_output = template.render(data_404=data_404, data_timeout=data_timeout, data_any=data_any)
        with open('template/test.html', 'w') as f:
            f.write(html_output)

        return html_output


def get_mess(err_links: dict):
    header = ['link', 'status', 'parent']
    rows = [[link, err_links[link]['status_cod'], err_links[link]['parent']] for link in err_links]
    table = create_table(header, rows)
    return table


if __name__ == "__main__":
    err_link = {
        'link1': {'status_cod': 404, 'parent': 'parent1'},
        'link2': {'status_cod': 404, 'parent': 'parent2'},
        'link3': {'status_cod': 404, 'parent': 'parent3'},
    }

    # with open('../test.json', 'r') as f:
    #     err_link = json.load(f)
    start = datetime.now()
    print(err_link)
    message = create_pandas(err_link)
    print(message)
    with open('../result_files/error_links.txt', 'w') as f:
        f.write(str(message))
    end = datetime.now()
    time = end - start
    print(str(time)[2:][:-7])