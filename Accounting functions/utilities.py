import pandas as pd
import tkinter as tk
from tkinter import filedialog
# Include utilities like save function, get file function, formatting functions, etc

def acct_summary(df, class_col, clas_item, ac_code, ac_cls, num_conv, rounding=0, positive=True, sort_order=False,
                 sum_row='Total'):
    """
    This function provides a summary of an item. It receives the trial balance as a dataset based on specification
    trial_bal: The trial balance dataset: dataframe
    class_col: the name of the column you want to group by : string
    clas_item: the item in you want to group: string
    ac_code: the name of the account code column: string
    ac_cls: the name of the account class column: string
    num_conv: how should the figures be divided? thousands, millions? takes integer
    rounding: how many decimal place
    positive: based on the class of account, should the data return a positive or negative number?
    """
    df_2 = df.copy()
    df_2.columns = df_2.columns.astype(str)
    df_2.drop(ac_code, axis=1, inplace=True)
    df_2 = df_2[df_2[class_col] == clas_item]
    numeric_cols = df_2.select_dtypes(include=['number'])
    result = numeric_cols.groupby(df_2[ac_cls]).sum().sort_values(by=numeric_cols.columns[0], ascending=sort_order)
    if positive is not True:
        result *= -1
    result = pd.DataFrame(result.to_records())
    total_row = result.select_dtypes(include=['number']).sum()
    total_row[ac_cls] = sum_row
    result = pd.concat([result, total_row.to_frame().T], ignore_index=True)
    result[numeric_cols.columns] = result[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    numeric_cols_2 = result.select_dtypes(include=['number'])
    if rounding == 0:
        result[numeric_cols_2.columns] = (numeric_cols_2 / num_conv).round(rounding).astype(int)
    else:
        result[numeric_cols_2.columns] = (numeric_cols_2 / num_conv).round(rounding).astype(float)
    return result

def get_file(title=""):
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    root.lift()
    file_path = filedialog.askopenfilename(title=title, filetypes=[("Excel files", "*.xlsx;*.xls")])
    root.destroy()
    req_file = pd.read_excel(file_path)
    return req_file


def format_excel_file(workbook, sheet_name, df):
    # create the format objects
    money_formats = workbook.add_format(
        {'num_format': '#,##0.00_);[Red](#,##0.00)', 'align': 'vjustify', 'valign': 'right'})
    header_formats = workbook.add_format({'bold': True, 'valign': 'top', 'font_size': 14})
    total_formats = workbook.add_format({'bold': True, 'num_format': '#,##0.00_);[Red](#,##0.00)'})

    worksheet = workbook.get_worksheet_by_name(sheet_name)
    start_row = 3
    last_row = df.shape[0] + start_row

    worksheet.write(0, 0, 'ABC LIMITED', header_formats)
    worksheet.write(1, 0, 'INCOME STATEMENT FOR THE YEAR ENDED 20X1', header_formats)
    worksheet.set_row(last_row, None, total_formats)
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:C', 21, money_formats)
    worksheet.set_zoom(110)


def create_money_format(workbook):
    money_formats = workbook.add_format(
        {'num_format': '#,##0.00_);[Red](#,##0.00)', 'align': 'vjustify', 'valign': 'right'})
    return money_formats


def create_percent_format(workbook):
    percent_formats = workbook.add_format({'num_format': '0%', 'align': 'vjustify', 'valign': 'right'})
    return percent_formats


def create_header_format(workbook):
    header_formats = workbook.add_format({'bold': True, 'valign': 'top', 'font_size': 14})
    return header_formats


def create_total_format(workbook):
    total_formats = workbook.add_format({'bold': True, 'num_format': '#,##0.00_);[Red](#,##0.00)'})
    return total_formats


def create_normal_format(workbook):
    normal_formats = workbook.add_format({'align': 'left', 'valign': 'vjustify'})
    return normal_formats


def save_file(df, default_name='output', sheet_name='Sheet1'):  # formats=None):
    # create file dialog for saving file
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    file_name = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".xlsx",
                                             filetypes=[("Excel Workbook", "*.xlsx")])
    # check if user cancelled file dialog
    if file_name == "":
        return

    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    start_row = 3
    last_row = df.shape[0] + start_row
    df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)
    workbook = writer.book

    money_format = create_money_format(workbook)
    percent_format = create_percent_format(workbook)
    header_format = create_header_format(workbook)
    total_format = create_total_format(workbook)
    normal_format = create_normal_format(workbook)

    worksheet = writer.sheets[sheet_name]
    worksheet.write(0, 0, 'ABC LIMITED', header_format)
    worksheet.write(1, 0, 'INCOME STATEMENT FOR THE YEAR ENDED 20X1', header_format)
    worksheet.set_row(last_row, None, total_format)
    worksheet.set_zoom(100)

    for i, col in enumerate(df.columns):
        column_len = max(df[col].astype(str).map(len).max(), len(col))
        worksheet.set_column(i, i, column_len + 2)

        if df[col].dtype == 'float64' or 'int':
            worksheet.set_column(i, i, 21, money_format)
        elif col == 'Percentage':
            worksheet.set_column(i, i, None, percent_format)
        else:
            worksheet.set_column(i, i, 50, normal_format)

    worksheet.set_column('A:A', 50, normal_format)
    writer.save()



def je_completeness(journal_entries, trial_balance, je_gl_code="", tb_gl_code="", tb_pr_yr="", tb_cur_yr="",
                    funct_amount=""):
    """
    This function tests if journal entries are complete. It requires two datasets: the total journal /n
    entries passed in the financial year and the trial balance. The trial balance should contain opening
    balance and closing balance figures for each account code. The function takes the opening balance
    of all account code, add all the journal entries passed into each journal code and compares the
    calculated closing balance with the closing balance in the TB.
    journal_entries: all journal entries dataset for the year,
    trial_balance: the trial balance containing the opening and closing balance,
    je_gl_code='the GL or Account code column in the journal entry',
    tb_gl_code='the GL or Account code column in the trial balance',
    tb_opening_bal='opening balance column in the trial balance',
    tb_closing_bal='closing balance column in the trial balance',
    funct_amount='amount column in the journal entry',
    """

    pivot_journals = journal_entries.pivot_table(index=je_gl_code, values=funct_amount, aggfunc=sum)
    pivot_journals = pd.DataFrame(pivot_journals.to_records())

    tb = trial_balance
    tb = tb.merge(pivot_journals, how="left", left_on=tb_gl_code, right_on=je_gl_code) \
        .drop(je_gl_code, axis=1).fillna(0)
    tb['Calculated Closing Balance'] = tb[tb_pr_yr] + tb[funct_amount]
    tb['Difference'] = round((tb[tb_cur_yr] - tb['Calculated Closing Balance']), 2)
    tb_diff = tb.loc[tb['Difference'] != 0]
    return tb_diff