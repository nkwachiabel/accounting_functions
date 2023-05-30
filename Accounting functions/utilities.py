import pandas as pd
import numpy as np
import xlsxwriter
import tkinter as tk
from tkinter import filedialog

# Include utilities like save function, get file function, formatting functions, etc

def acct_summary(df, class_col, clas_item, ac_code, ac_cls, num_conv=1, rounding=0, positive=True, sort_order=False,
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
    money_formats = workbook.add_format({'num_format': '#,##_);(#,##)', 'align': 'vjustify', 'valign': 'right'})
    return money_formats

def create_percent_format(workbook):
    percent_formats = workbook.add_format({'num_format': '0%', 'align': 'vjustify', 'valign': 'right'})
    return percent_formats

def create_header_format(workbook):
    header_formats = workbook.add_format({'bold': True, 'valign': 'top', 'font_size': 14})
    return header_formats

def create_total_format(workbook):
    total_formats = workbook.add_format({'num_format': '#,##_);(#,##)', 'bold':True})
    return total_formats

def create_normal_format(workbook):
    normal_formats = workbook.add_format({'align': 'vjustify', 'valign': 'left'})
    return normal_formats


def save_file(dfs, default_name='output', sheet_name='Sheet1'):
    # create file dialog for saving file
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    file_name = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".xlsx",
                                             filetypes=[("Excel Workbook", "*.xlsx")])

    # check if user cancelled file dialog
    if file_name == "":
        return

    # Create an ExcelWriter object
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    workbook = writer.book

    money_format = create_money_format(workbook)
    percent_format = create_percent_format(workbook)
    header_format = create_header_format(workbook)
    total_format = create_total_format(workbook)
    normal_format = create_normal_format(workbook)

    # Initialize the starting row
    start_row = 4
    last_row_index = start_row - 1

    # Iterate over the DataFrames
    for i, df in enumerate(dfs):
        if df is not None:
            # Add the header of the numeric columns to the start of the first dataframe
            if i == 0:
                header_df = pd.DataFrame(columns=df.columns)
                header_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row - 1, header=True, index=False)

            # Write the DataFrame to the ExcelWriter
            df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, header=False, index=False)

            # Apply money format to the numeric columns
            for j, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col))
                writer.sheets[sheet_name].set_column(j, j, column_len + 2)

                if df[col].dtype == 'float64' or 'int':
                    writer.sheets[sheet_name].set_column(j, j, 21, money_format)

            # Apply header format to the header row
            writer.sheets[sheet_name].set_row(start_row - 1, None, header_format)

            # Get the last row index
            last_row_index = start_row + df.shape[0] - 1

            # Apply bold format to the last row
            writer.sheets[sheet_name].set_row(last_row_index, None, total_format)

            # Update the starting row for the next DataFrame
            start_row += df.shape[0] + 1

    col_format = writer.book.add_format({'align': 'vjustify', 'valign': 'left'})
    writer.sheets[sheet_name].set_column('A:A', 50, col_format)

    # Save the Excel file
    writer.save()

def append_sum_row(df, df2, ac_cls, tot_name=""):
    numeric_cols = df.select_dtypes(include=['number'])
    net_row = pd.concat([df.iloc[[-1]], df2.iloc[[-1]]], ignore_index=True)
    total_row = net_row.select_dtypes(include=['number']).sum()
    total_row[ac_cls] = tot_name
    net_row = pd.concat([df2, total_row.to_frame().T], ignore_index=True)
    net_row[numeric_cols.columns] = net_row[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    return net_row
