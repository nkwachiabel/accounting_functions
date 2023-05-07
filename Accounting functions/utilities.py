import pandas as pd
import numpy as np
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

def append_sum_row(df, df2, ac_cls, tot_name=""):
    numeric_cols = df.select_dtypes(include=['number'])
    net_row = pd.concat([df.iloc[[-1]], df2.iloc[[-1]]], ignore_index=True)
    total_row = net_row.select_dtypes(include=['number']).sum()
    total_row[ac_cls] = tot_name
    net_row = pd.concat([df2, total_row.to_frame().T], ignore_index=True)
    net_row[numeric_cols.columns] = net_row[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    return net_row

def get_gross_profit(tb, ac_cls, revenue, cos_of_sale, fs_class, p_and_l, ac_code, num_conv, rounding):
    grs_pro = tb.copy()
    grs_pro = grs_pro[grs_pro[ac_cls].isin([revenue, cos_of_sale])]
    grs_pro = acct_summary(grs_pro, fs_class, p_and_l, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                           sort_order=True, sum_row='Gross Profit')
    return grs_pro

def get_oper_pr_loss(tb, ac_cls, revenue, cos_of_sale, fin_income, int_expense, income_tax, fs_class, p_and_l,
                     ac_code, num_conv, rounding, grs_pro):
    other_inc = tb.copy()
    other_inc = other_inc[~other_inc[ac_cls].isin([revenue, cos_of_sale, fin_income, int_expense, income_tax])]
    other_inc = acct_summary(other_inc, fs_class, p_and_l, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                             sort_order=True, sum_row='')
    numeric_cols = other_inc.select_dtypes(include=['number'])
    other_inc = append_sum_row(grs_pro, other_inc, ac_cls, tot_name="Operating Profit/(loss)")
    other_inc[numeric_cols.columns] = other_inc[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    return other_inc

def get_profit_before_tax(tb, ac_cls, fin_income, int_expense, fs_class, p_and_l, ac_code, num_conv, rounding, opr_pr_los):
    pbt = tb.copy()
    pbt = pbt[pbt[ac_cls].isin([fin_income, int_expense])]
    pbt = acct_summary(pbt, fs_class, p_and_l, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                       sort_order=True, sum_row='Net interest income/(cost)')
    numeric_cols = pbt.select_dtypes(include=['number'])
    pbt = append_sum_row(opr_pr_los, pbt, ac_cls, tot_name="Profit before tax")
    pbt[numeric_cols.columns] = pbt[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    return pbt

def get_income_tax(tb, ac_cls, income_tax, fs_class, p_and_l, ac_code, num_conv, rounding, pr_b4_tx):
    inc_tax = tb.copy()
    inc_tax = inc_tax[inc_tax[ac_cls].isin([income_tax])]
    inc_tax = acct_summary(inc_tax, fs_class, p_and_l, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                           sort_order=True, sum_row='Tax (expense)/income')
    inc_tax = inc_tax.iloc[:-1]
    numeric_cols = inc_tax.select_dtypes(include=['number'])
    inc_tax = append_sum_row(pr_b4_tx, inc_tax, ac_cls, tot_name="Profit for the year")
    inc_tax[numeric_cols.columns] = inc_tax[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    return inc_tax


def get_oci_no_reclass(tb, ac_cls, fs_class, oci_no_rcls, ac_code, num_conv, rounding, pr_af_tax, oci_rcls):
    if oci_no_rcls is None:
        oci = None

    elif oci_rcls is not None:
        oci = tb.copy()
        oci = oci[oci[fs_class].isin([oci_no_rcls])]
        oci = acct_summary(oci, fs_class, oci_no_rcls, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                           sort_order=True, sum_row='Items that will not be reclassified')
        numeric_cols = oci.select_dtypes(include=['number'])
        oci = append_sum_row(pr_af_tax, oci, ac_cls, tot_name="Total comprehensive income")
        oci[numeric_cols.columns] = oci[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
        oci = oci.iloc[:-1, :]
    else:
        oci = tb.copy()
        oci = oci[oci[fs_class].isin([oci_no_rcls])]
        oci = acct_summary(oci, fs_class, oci_no_rcls, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                           sort_order=True, sum_row='Items that will not be reclassified')
        numeric_cols = oci.select_dtypes(include=['number'])
        oci = append_sum_row(pr_af_tax, oci, ac_cls, tot_name="Total comprehensive income")
        oci[numeric_cols.columns] = oci[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    return oci


def get_oci_reclass(tb, ac_cls, fs_class, oci_rcls, ac_code, num_conv, rounding, pr_af_tax, oci_no_rcls):
    if oci_rcls is None:
        oci = None

    elif oci_rcls is not None and oci_no_rcls is not None:
        oci = tb.copy()
        oci = acct_summary(oci, fs_class, oci_rcls, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                           sort_order=True, sum_row='Items that may be reclassified')
        numeric_cols = oci.select_dtypes(include=['number'])
        oci = append_sum_row(oci_no_rcls, oci, ac_cls, tot_name="Total other comprehensive income")
        oci[numeric_cols.columns] = oci[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
        oci = append_sum_row(pr_af_tax, oci, ac_cls, tot_name="Total comprehensive income")
        oci[numeric_cols.columns] = oci[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')

    else:
        oci = tb.copy()
        oci = oci[oci[fs_class].isin([oci_rcls])]
        oci = acct_summary(oci, fs_class, oci_rcls, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                           sort_order=True, sum_row='Other Comprehensive Income')
        numeric_cols = oci.select_dtypes(include=['number'])
        oci = append_sum_row(pr_af_tax, oci, ac_cls, tot_name="Total comprehensive income")
        oci[numeric_cols.columns] = oci[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    return oci


def create_income_statement(grs_pro, opr_pr_los, pr_b4_tx, pr_af_tax, oci_reclass=None, oci_nrcl=None):
    if oci_reclass is not None and oci_nrcl is not None:
        income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
                                 pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax, pd.DataFrame(index=range(1)),
                                 oci_reclass,
                                 pd.DataFrame(index=range(1)), oci_nrcl], ignore_index=True)

    elif oci_reclass is not None:
        income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
                                 pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax, pd.DataFrame(index=range(1)),
                                 oci_reclass], ignore_index=True)

    elif oci_nrcl is not None:
        income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
                                 pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax, pd.DataFrame(index=range(1)),
                                 oci_nrcl], ignore_index=True)
    else:
        income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
                                 pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax], ignore_index=True)
    return income_stmt


# def create_income_statement(grs_pro, opr_pr_los, pr_b4_tx, pr_af_tax, oci_reclass=None, oci_nrcl=None):
#     if oci_reclass and oci_nrcl is not None:
#         income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
#                                  pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax, pd.DataFrame(index=range(1)),
#                                  oci_reclass,
#                                  pd.DataFrame(index=range(2)), oci_nrcl], ignore_index=True)
#
#     elif oci_reclass is not None:
#         income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
#                                  pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax, pd.DataFrame(index=range(1)),
#                                  oci_reclass], ignore_index=True)
#
#     elif oci_nrcl is not None:
#         income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
#                                  pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax, pd.DataFrame(index=range(1)),
#                                  oci_nrcl], ignore_index=True)
#     else:
#         income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opr_pr_los, pd.DataFrame(index=range(1)),
#                                  pr_b4_tx, pd.DataFrame(index=range(1)), pr_af_tax], ignore_index=True)
#     return income_stmt


# def je_completeness(journal_entries, trial_balance, je_gl_code="", tb_gl_code="", tb_pr_yr="", tb_cur_yr="",
#                     funct_amount=""):
#     """
#     This function tests if journal entries are complete. It requires two datasets: the total journal /n
#     entries passed in the financial year and the trial balance. The trial balance should contain opening
#     balance and closing balance figures for each account code. The function takes the opening balance
#     of all account code, add all the journal entries passed into each journal code and compares the
#     calculated closing balance with the closing balance in the TB.
#     journal_entries: all journal entries dataset for the year,
#     trial_balance: the trial balance containing the opening and closing balance,
#     je_gl_code='the GL or Account code column in the journal entry',
#     tb_gl_code='the GL or Account code column in the trial balance',
#     tb_opening_bal='opening balance column in the trial balance',
#     tb_closing_bal='closing balance column in the trial balance',
#     funct_amount='amount column in the journal entry',
#     """
#
#     pivot_journals = journal_entries.pivot_table(index=je_gl_code, values=funct_amount, aggfunc=sum)
#     pivot_journals = pd.DataFrame(pivot_journals.to_records())
#
#     tb = trial_balance
#     tb = tb.merge(pivot_journals, how="left", left_on=tb_gl_code, right_on=je_gl_code) \
#         .drop(je_gl_code, axis=1).fillna(0)
#     tb['Calculated Closing Balance'] = tb[tb_pr_yr] + tb[funct_amount]
#     tb['Difference'] = round((tb[tb_cur_yr] - tb['Calculated Closing Balance']), 2)
#     tb_diff = tb.loc[tb['Difference'] != 0]
#     return tb_diff
