# Accounting functions created by Nkwachi Abel
import pandas as pd
import tkinter as tk
from tkinter import filedialog


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
    # if formats is not None:
    #     format_excel_file(workbook, sheet_name, df)

    writer.save()


# General ledger continuity test also known as Journal Entry Completeness
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


def inc_stmt(trial_balance, fs_class, p_and_l_items, ac_code, ac_cls, divis):
    """
    This function prepares a simple income statement from the trial balance. It receives the trial balance as a dataset\
     and returns the income statement
    trial_bal: The trial balance dataset: dataframe
    fs_class: the name of the classifyer column, used to filter the rows for the income statement: string
    p_and_l_items: the income statement identifier in the fs_class column: string
    ac_code: the name of the account code column: string
    ac_cls: the name of the account class column: string
    divis: how should the figures be divided? thousands, millions? takes integer
    """
    trial_bal_2 = trial_balance.copy()
    trial_bal_2.columns = trial_bal_2.columns.astype(str)
    trial_bal_2.drop(ac_code, axis=1, inplace=True)
    trial_bal_2 = trial_bal_2[trial_bal_2[fs_class] == p_and_l_items]
    numeric_cols = trial_bal_2.select_dtypes(include=['number'])
    result = numeric_cols.groupby(trial_bal_2[ac_cls]).sum().sort_values(by=numeric_cols.columns[0])
    result *= -1
    result = pd.DataFrame(result.to_records())
    total_row = result.select_dtypes(include=['number']).sum()
    total_row[ac_cls] = 'Net Income'
    result = pd.concat([result, total_row.to_frame().T], ignore_index=True)
    result[numeric_cols.columns] = result[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')
    numeric_cols_2 = result.select_dtypes(include=['number'])
    result[numeric_cols_2.columns] = (numeric_cols_2 / divis).round().astype(int)
    return result


def summ_pl_li_item(trial_bal, ac_type_summary="", ac_type="", ac_code="", ac_cls="", cur_yr="", pr_yr="",
                    ascending=False):
    """
    This function returns a summary of an account class in the profit or loss item
    trial_bal: The trial balance dataset
    ac_type_summary: the account type you want to get the breakdown for (e.g., revenue, expenses, assets)
    ac_type: the name of the account type column, used to filter the rows for the account type
    ac_code: the name of the account code column
    ac_cls: the name of the account class column
    cur_yr: the name of the current year column
    pr_yr: the name of the prior year column
    ascending: how should the figures be sorted (ascending or descending)
    """
    rev_exp = trial_bal[trial_bal[ac_type] == ac_type_summary]
    rev_exp = rev_exp.copy()
    rev_exp.drop(ac_code, axis=1, inplace=True)
    rev_exp = rev_exp.groupby(by=[ac_cls]).sum().sort_values(by=[cur_yr], ascending=ascending)
    rev_exp[[pr_yr, cur_yr]] *= -1
    rev_exp = pd.DataFrame(rev_exp.to_records())
    total_rev_exp = {'Account Class': 'Total', pr_yr: rev_exp[pr_yr].sum(), cur_yr: rev_exp[cur_yr].sum()}
    rev_exp = pd.concat([rev_exp, pd.DataFrame([total_rev_exp])], ignore_index=True)
    rev_exp = rev_exp.rename(columns={ac_cls: ac_type_summary})
    return rev_exp


def group_sum(df, ac_code, ac_cls, pri_yr, cur_yr, ascending_order=True):
    """
    Groups a dataframe by a specified column, calculates the sum of another specified column, and sorts by a third
    specified column.
    """
    df = df.copy()
    df.drop(ac_code, axis=1, inplace=True)
    df = df.groupby(by=[ac_cls]).sum().sort_values(by=[cur_yr], ascending=ascending_order)
    df[[pri_yr, cur_yr]] *= -1
    df = pd.DataFrame(df.to_records())
    return df

def group_sum_bs(df, ac_code, ac_cls, cur_yr, ascending_order=False):
    """
    Groups a dataframe by a specified column, calculates the sum of another specified column, and sorts by a third
    specified column.
    """
    df = df.copy()
    df.drop(ac_code, axis=1, inplace=True)
    df = df.groupby(by=[ac_cls]).sum().sort_values(by=[cur_yr], ascending=ascending_order)
    df = pd.DataFrame(df.to_records())
    return df

def oci_reclass(trial_balance_2, fs_class="", oci_items="", oci_class_col="", oci_class="", ac_code="", ac_cls="", cur_yr="", pr_yr=""):

    trial_balance_2.columns = trial_balance_2.columns.astype(str)
    trial_balance = trial_balance_2[(trial_balance_2[fs_class] == oci_items) & ~(trial_balance_2[oci_class_col] == oci_class)]

    income_state = trial_balance.copy()
    income_state.drop(ac_code, axis=1, inplace=True)
    income_state = income_state.groupby(by=[ac_cls]).sum().sort_values(by=[cur_yr])
    income_state[[pr_yr, cur_yr]] *= -1
    income_state = pd.DataFrame(income_state.to_records())

    net_inc = {ac_cls: 'OCI_reclass', pr_yr: income_state[pr_yr].sum(), cur_yr: income_state[cur_yr].sum()}
    income_stmt = pd.concat([income_state, pd.DataFrame([net_inc])], ignore_index=True)
    return income_stmt

def oci_non_recls(trial_balance_2, fs_class, oci_items, oci_class_col, oci_class, ac_code, ac_cls, cur_yr, pr_yr):

    trial_balance_2.columns = trial_balance_2.columns.astype(str)
    trial_balance = trial_balance_2[(trial_balance_2[fs_class] == oci_items) & (trial_balance_2[oci_class_col] == oci_class)]

    income_state = trial_balance.copy()
    income_state.drop(ac_code, axis=1, inplace=True)
    income_state = income_state.groupby(by=[ac_cls]).sum().sort_values(by=[cur_yr])
    income_state[[pr_yr, cur_yr]] *= -1
    income_state = pd.DataFrame(income_state.to_records())

    net_inc = {ac_cls: 'OCI_non_reclass', pr_yr: income_state[pr_yr].sum(), cur_yr: income_state[cur_yr].sum()}
    income_stmt = pd.concat([income_state, pd.DataFrame([net_inc])], ignore_index=True)
    return income_stmt

def append_sum_row(df, df2, ac_cls, pri_yr, cur_yr, tot_name=""):
    """Helper function to append a summary row to a DataFrame"""
    row = {ac_cls: tot_name, pri_yr: df[pri_yr].sum(), cur_yr: df[cur_yr].sum()}
    df2 = pd.concat([df2, pd.DataFrame([row])], ignore_index=True)
    return df2

def get_gross_profit(trial_bal, rev_frm_cus, cos_of_sale, ac_clss, ac_codes, pry_yr, curr_yr):
    rev_frm_cus = trial_bal[trial_bal[ac_clss] == rev_frm_cus]
    cos_of_sal = trial_bal[trial_bal[ac_clss] == cos_of_sale]
    grs_pro = pd.concat([rev_frm_cus, cos_of_sal], ignore_index=True)
    grs_pro = group_sum(grs_pro, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
    grs_pro = append_sum_row(grs_pro, grs_pro, ac_clss, pry_yr, curr_yr, tot_name="Gross Profit")
    return grs_pro

def get_other_income_expenses(rev_name, ac_cls, ac_code, grs_pro, rev_frm_cus, cos_of_sale, fin_inc, int_exp,
                              income_tax, pri_yr, cur_yr):
    other_inc = rev_name[~rev_name[ac_cls].isin([rev_frm_cus, cos_of_sale, fin_inc, int_exp, income_tax])]
    other_inc = group_sum(other_inc, ac_code, ac_cls, pri_yr, cur_yr, ascending_order=True)
    opex2 = other_inc.copy()
    opex2 = pd.concat([opex2, opex2.sum().to_frame().T], ignore_index=True)
    net_opex = pd.concat([grs_pro.iloc[[-1]], opex2.iloc[[-1]]], ignore_index=True)
    other_inc = append_sum_row(net_opex, other_inc, ac_cls, pri_yr, cur_yr, tot_name="Operating Profit/(loss)")
    return other_inc

def get_profit_before_tax(trial_bal, opr_pro, fin_inc, int_exp, ac_codes, ac_clss, pry_yr, curr_yr):
    net_fin_inc = trial_bal[trial_bal[ac_clss].isin([fin_inc, int_exp])]
    net_fin_inc = group_sum(net_fin_inc, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
    net_fin_inc2 = net_fin_inc.copy()
    net_fin_inc2 = pd.concat([net_fin_inc2, net_fin_inc2.sum().to_frame().T], ignore_index=True)
    pbit_net = pd.concat([opr_pro.iloc[[-1]], net_fin_inc2.iloc[[-1]]], ignore_index=True)
    net_fin_inc = append_sum_row(pbit_net, net_fin_inc, ac_clss, pry_yr, curr_yr,
                                 tot_name="Profit/(loss) before tax")
    return net_fin_inc

def get_income_tax(trial_bal, net_fin_inc, inc_tax, ac_codes, ac_clss, pry_yr, curr_yr):
    inc_tax = trial_bal[trial_bal[ac_clss].isin([inc_tax])]
    inc_tax = group_sum(inc_tax, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)

    inc_tax2 = inc_tax.copy()
    inc_tax2 = pd.concat([inc_tax2, inc_tax2.sum().to_frame().T], ignore_index=True)
    pat_net = pd.concat([net_fin_inc.iloc[[-1]], inc_tax2.iloc[[-1]]], ignore_index=True)
    inc_tax = append_sum_row(pat_net, inc_tax, ac_clss, pry_yr, curr_yr, tot_name="Profit/(loss) after tax")
    return inc_tax

def get_oci_recls(trial_bal, oci_cls_col, oci_clss, ac_codes, ac_clss, pry_yr, curr_yr):
    oci_itms = trial_bal[~trial_bal[oci_cls_col].isin([oci_clss])]
    oci_itms = group_sum(oci_itms, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
    oci_itms = append_sum_row(oci_itms, oci_itms, ac_clss, pry_yr, curr_yr,
                              tot_name="")
    return oci_itms


def get_oci(trial_bal, oci_recls, pr_af_tx, oci_cls_col, oci_clss, ac_codes, ac_clss, pry_yr, curr_yr):
    oci_itms = trial_bal[trial_bal[oci_cls_col] == oci_clss]
    oci_itms = group_sum(oci_itms, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
    oci_itms_2 = oci_itms.copy()
    oci_itms_2 = pd.concat([oci_itms_2, oci_itms_2.sum().to_frame().T], ignore_index=True)
    net_oci = pd.concat([oci_recls.iloc[[-1]], oci_itms_2.iloc[[-1]]], ignore_index=True)
    oci_itms = append_sum_row(net_oci, oci_itms, ac_clss, pry_yr, curr_yr,
                              tot_name="Total other comprehensive income")
    tot_comp_inc = pd.concat([pr_af_tx.iloc[[-1]], oci_itms.iloc[[-1]]], ignore_index=True)
    tot_comp_inc = append_sum_row(tot_comp_inc, oci_itms, ac_clss, pry_yr, curr_yr,
                                  tot_name="Total comprehensive income")
    return tot_comp_inc

def create_income_statement(grs_pro, opex, net_fin_inc, inc_tax, oci_2, oci_nrcl, ac_cls):
    income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opex, pd.DataFrame(index=range(1)),
                             net_fin_inc, pd.DataFrame(index=range(1)), inc_tax, pd.DataFrame(index=range(2)), oci_2,
                             pd.DataFrame(index=range(2)), oci_nrcl], ignore_index=True)
    income_stmt = income_stmt.rename(columns={ac_cls: 'Income Statement'})
    return income_stmt

def det_inc_stmt(trial_balance_2, fs_class="", p_and_l_items="", oci_items="", rev_frm_customer="", cos_of_sales="",
                 fin_income="", int_expense="", income_tax="", oci_class_col=None, oci_class=None,
                 ac_cls="", ac_code="", pri_yr="", cur_yr=""):
    trial_balance_2.columns = trial_balance_2.columns.astype(str)
    trial_balance = trial_balance_2[trial_balance_2[fs_class] == p_and_l_items]
    trial_balance_3 = trial_balance_2[trial_balance_2[fs_class] == oci_items]

    gross_profit = get_gross_profit(trial_balance, rev_frm_customer, cos_of_sales, ac_cls, ac_code, pri_yr, cur_yr)
    oth_inc = get_other_income_expenses(trial_balance, ac_cls, ac_code, gross_profit, rev_frm_customer, cos_of_sales,
                                        fin_income, int_expense, income_tax, pri_yr, cur_yr)
    ebt = get_profit_before_tax(trial_balance, oth_inc, fin_income, int_expense, ac_code, ac_cls, pri_yr, cur_yr)
    pat = get_income_tax(trial_balance, ebt, income_tax, ac_code, ac_cls, pri_yr, cur_yr)
    oci_2 = get_oci_recls(trial_balance_3, oci_class_col, oci_class, ac_code, ac_cls, pri_yr, cur_yr)
    oci_1 = get_oci(trial_balance_3, oci_2, pat, oci_class_col, oci_class, ac_code, ac_cls, pri_yr, cur_yr)
    income_statement = create_income_statement(gross_profit, oth_inc, ebt, pat, oci_2, oci_1, ac_cls)

    return income_statement

def get_non_curr_asset(trial_bal, ac_type, non_curr_ass, ac_clss, ac_codes, pry_yr, curr_yr):
    nca = trial_bal[trial_bal[ac_type] == non_curr_ass]
    nca = group_sum_bs(nca, ac_codes, ac_clss, curr_yr, ascending_order=False)
    nca = append_sum_row(nca, nca, ac_clss, pry_yr, curr_yr, tot_name="Total Non-current assets")
    return nca

def get_curr_asset(trial_bal, ac_type, nca, curr_ass, ac_clss, ac_codes, pry_yr, curr_yr):
    cur_asst = trial_bal[trial_bal[ac_type] == curr_ass]
    cur_asst = group_sum_bs(cur_asst, ac_codes, ac_clss, curr_yr, ascending_order=False)
    cur_asst = append_sum_row(cur_asst, cur_asst, ac_clss, pry_yr, curr_yr, tot_name="Total Current assets")
    tot_ass = pd.concat([nca.iloc[[-1]], cur_asst.iloc[[-1]]], ignore_index=True)
    cur_asst = append_sum_row(tot_ass, cur_asst, ac_clss, pry_yr, curr_yr, tot_name="Total Assets")
    return cur_asst

def get_non_curr_liab(trial_bal, ac_type, non_curr_liab, ac_clss, ac_codes, pry_yr, curr_yr):
    ncl = trial_bal[trial_bal[ac_type] == non_curr_liab]
    ncl = group_sum(ncl, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
    ncl = append_sum_row(ncl, ncl, ac_clss, pry_yr, curr_yr, tot_name="Total Non-current liabilities")
    return ncl

def get_curr_liab(trial_bal, ac_type, ncl, curr_liab, ac_clss, ac_codes, pry_yr, curr_yr):
    cur_liabil = trial_bal[trial_bal[ac_type] == curr_liab]
    cur_liabil = group_sum(cur_liabil, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
    cur_liabil = append_sum_row(cur_liabil, cur_liabil, ac_clss, pry_yr, curr_yr,
                                tot_name="Total Current liabilities")
    tot_liab = pd.concat([ncl.iloc[[-1]], cur_liabil.iloc[[-1]]], ignore_index=True)
    cur_liabil = append_sum_row(tot_liab, cur_liabil, ac_clss, pry_yr, curr_yr, tot_name="Total Liabilities")
    return cur_liabil


def get_equity(trial_bal, ac_type, equity, tot_liab_row, ac_clss, fs_class, p_and_l_items, oci_items, oci_class,
               oci_class_col, ac_codes, pry_yr, curr_yr, ret_earn, oci_res=None):

    equi = trial_bal[trial_bal[ac_type] == equity]
    equi = group_sum(equi, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)

    net_inq = inc_stmt(trial_bal, fs_class, p_and_l_items, ac_codes, ac_clss, curr_yr, pry_yr)
    oci_non_recl = oci_non_recls(trial_bal, fs_class, oci_items, oci_class_col, oci_class, ac_codes, ac_clss, curr_yr,
                                 pry_yr)
    oci_recl = oci_reclass(trial_bal, fs_class, oci_items, oci_class_col, oci_class, ac_codes, ac_clss, curr_yr,
                           pry_yr)

    pr_af_tx = net_inq.iloc[[-1]]
    oci_nrecl = oci_non_recl.iloc[[-1]]
    oci_reclass_2 = oci_recl.iloc[[-1]]

    equi_2 = equi[equi[ac_clss] == ret_earn].index[0]
    equi.at[equi_2, curr_yr] += pr_af_tx[curr_yr]
    equi.at[equi_2, pry_yr] += pr_af_tx[pry_yr]

    equi.at[equi_2, curr_yr] += oci_nrecl[curr_yr]
    equi.at[equi_2, pry_yr] += oci_nrecl[pry_yr]

    if oci_res is not None:
        equi_3 = equi[equi[ac_clss] == oci_res].index[0]
        equi.at[equi_3, curr_yr] += oci_reclass_2[curr_yr]
        equi.at[equi_3, pry_yr] += oci_reclass_2[pry_yr]

    equi = append_sum_row(equi, equi, ac_clss, pry_yr, curr_yr, tot_name="Total Equity")

    tot_liab_equ = pd.concat([equi.iloc[[-1]], tot_liab_row.iloc[[-1]]], ignore_index=True)
    equi = append_sum_row(tot_liab_equ, equi, ac_clss, pry_yr, curr_yr, tot_name="Total Liabilities and Equity")
    return equi

def create_bal_sheet(nca, cur_asst, ncl, cur_liabil, equi, ac_clss):
    bal_sheet = pd.concat([nca, pd.DataFrame(index=range(1)), cur_asst, pd.DataFrame(index=range(1)),
                           ncl, pd.DataFrame(index=range(1)), cur_liabil, pd.DataFrame(index=range(1)),
                           equi], ignore_index=True)
    bal_sheet = bal_sheet.rename(columns={ac_clss: 'Balance sheet'})
    return bal_sheet


def det_bal_sht(trial_balance_2, fs_class="", non_curr_ass="", non_curr_liab="",
                curr_liab="", curr_ass="", equity="", ac_clss="", ac_codes="", ac_type="", pry_yr="", curr_yr="",
                p_and_l_items="", oci_items="", oci_class='', oci_class_col='', ret_earn='', oci_res=''):
    trial_balance_2.columns = trial_balance_2.columns.astype(str)
    non_curr_a = get_non_curr_asset(trial_balance_2, ac_type, non_curr_ass, ac_clss, ac_codes, pry_yr, curr_yr)
    curr_a = get_curr_asset(trial_balance_2, ac_type, non_curr_a, curr_ass, ac_clss, ac_codes, pry_yr, curr_yr)
    non_curr_l = get_non_curr_liab(trial_balance_2, ac_type, non_curr_liab, ac_clss, ac_codes, pry_yr, curr_yr)
    curr_l = get_curr_liab(trial_balance_2, ac_type, non_curr_l, curr_liab, ac_clss, ac_codes, pry_yr, curr_yr)
    equiii = get_equity(trial_balance_2, ac_type, equity, curr_l, ac_clss, fs_class, p_and_l_items, oci_items, oci_class,
                        oci_class_col, ac_codes, pry_yr, curr_yr, ret_earn, oci_res)

    bal_shit = create_bal_sheet(non_curr_a, curr_a, non_curr_l, curr_l, equiii, ac_clss)

    return bal_shit

# To do: Breakdown this functions to different python file. Separate the functions from the input, utilities from the main code
# Make the user to be able to choose how to round the figures i.e., million, thousand, etc.
# User should be able to decide the company name
# Remove the income statement from the save function
# User should only input all variables in the beginning. Therefore, create a separate python file to store variables
# User should be able to save all declared variables once and be able to make edits rather than inputting the variables always
# create a small database where the user can store different things like company name, how the balance sheet should be arranged (pd.categorical)
# Can you consider creating a user interface to collect all the information and store them?
# Use pd.categorical to arrange the line items
# How do we create the notes to the account? Knowing fully well that all notes can't come from the TB
# Save both Income statement and Balance sheet in one Excel file but different sheets
# Make the oci items optional. If there is a reclassification to retained earnings, only that should show and vice versa. if there are both, both should show
# Create a function for ratios... Profitability ratios, Solvency ratio, Leverage ratio, Efficiency ratio.
# Include a function for financial services ratio... Asset quality ratio, etc.
# Include a bespoke function for the users to calculate any ratio they deem fit.
# For the monthly financial statements, can a user upload the journal entries and get a dashboard that shows key metrics?
# Metrics like Monthly trend Revenue, Cost of sales, gross profit, net profit, etc.
# If there is data for a prior year, can the dashboard show the comparison of both years?
# IF there is data for more than one/two years, can I show as many years that's uploaded?
# Cash flow analysis - Get all journals posted to the cash and cash equivalent account codes, group all the postings by account code, try and group these postings into the various cash flow activities.
# This means that there will be only direct cash flow statement possible.
