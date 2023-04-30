# Accounting functions created by Nkwachi Abel
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from utilities import *


def inc_stmt(df, fs_class, p_and_l_items, ac_code, ac_cls, num_conv, rounding=0, positive=False, sum_r='Net Income'):
    """
        This function prepares a simple income statement from the trial balance. It receives the trial balance as a
        dataset and returns the income statement
        df: The trial balance dataset: dataframe
        fs_class: the name of the fs classifier column: string
        p_and_l_items: the income statement identifier in the fs_class column: string
        ac_code: the name of the account code column: string
        ac_cls: the name of the account class column: string
        num_conv: how should the figures be divided? thousands, millions? takes integer
        rounding: how many decimal place. If the rounding is zero, an integer is returned.
        positive: based on the class of account, should the data return a positive or negative number?
        """
    result = acct_summary(df, fs_class, p_and_l_items, ac_code, ac_cls, num_conv, rounding=rounding,
                          positive=positive, sort_order=True, sum_row=sum_r)
    return result

def det_inc_stmt(tb, ac_cls, revenue, cos_of_sale, fin_income, int_expense, income_tax, oci_rcls, oci_nrcl,
                 fs_class, p_and_l, ac_code, num_conv, rounding):
    grs_pro = get_gross_profit(tb, ac_cls, revenue, cos_of_sale, fs_class, p_and_l, ac_code, num_conv, rounding)
    opr_pr_los = get_oper_pr_loss(tb, ac_cls, revenue, cos_of_sale, fin_income, int_expense, income_tax,
                                  fs_class, p_and_l, ac_code, num_conv, rounding, grs_pro)
    pr_b4_tx = get_profit_before_tax(tb, ac_cls, fin_income, int_expense, fs_class, p_and_l,
                                     ac_code, num_conv, rounding, opr_pr_los)
    pr_af_tax = get_income_tax(tb, ac_cls, income_tax, fs_class, p_and_l, ac_code, num_conv, rounding, pr_b4_tx)
    oci_nrcl = get_oci_no_reclass(tb, ac_cls, fs_class, oci_nrcl, ac_code, num_conv, rounding, pr_af_tax, oci_rcls)
    oci_reclass = get_oci_reclass(tb, ac_cls, fs_class, oci_rcls, ac_code, num_conv, rounding, pr_af_tax, oci_nrcl)

    income_statement = create_income_statement(grs_pro, opr_pr_los, pr_b4_tx, pr_af_tax, oci_nrcl, oci_reclass)

    numeric_cols_2 = income_statement.select_dtypes(include=['number'])
    if rounding == 0:
        numeric_cols_2 = numeric_cols_2.fillna(0).replace([np.inf, -np.inf], 0).round(rounding).astype(int)
    else:
        numeric_cols_2 = numeric_cols_2.fillna(0).replace([np.inf, -np.inf], 0).round(rounding).astype(float)
    income_statement[numeric_cols_2.columns] = numeric_cols_2

    return income_statement

# def group_sum(df, ac_code, ac_cls, pri_yr, cur_yr, ascending_order=True):
#     """
#     Groups a dataframe by a specified column, calculates the sum of another specified column, and sorts by a third
#     specified column.
#     """
#     df = df.copy()
#     df.drop(ac_code, axis=1, inplace=True)
#     df = df.groupby(by=[ac_cls]).sum().sort_values(by=[cur_yr], ascending=ascending_order)
#     df[[pri_yr, cur_yr]] *= -1
#     df = pd.DataFrame(df.to_records())
#     return df

# def group_sum_bs(df, ac_code, ac_cls, cur_yr, ascending_order=False):
#     """
#     Groups a dataframe by a specified column, calculates the sum of another specified column, and sorts by a third
#     specified column.
#     """
#     df = df.copy()
#     df.drop(ac_code, axis=1, inplace=True)
#     df = df.groupby(by=[ac_cls]).sum().sort_values(by=[cur_yr], ascending=ascending_order)
#     df = pd.DataFrame(df.to_records())
#     return df

#
# def append_sum_row(df, df2, ac_cls, pri_yr, cur_yr, tot_name=""):
#     """Helper function to append a summary row to a DataFrame"""
#     row = {ac_cls: tot_name, pri_yr: df[pri_yr].sum(), cur_yr: df[cur_yr].sum()}
#     df2 = pd.concat([df2, pd.DataFrame([row])], ignore_index=True)
#     return df2
#
# def get_gross_profit(trial_bal, rev_frm_cus, cos_of_sale, ac_clss, ac_codes, pry_yr, curr_yr):
#     rev_frm_cus = trial_bal[trial_bal[ac_clss] == rev_frm_cus]
#     cos_of_sal = trial_bal[trial_bal[ac_clss] == cos_of_sale]
#     grs_pro = pd.concat([rev_frm_cus, cos_of_sal], ignore_index=True)
#     grs_pro = group_sum(grs_pro, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
#     grs_pro = append_sum_row(grs_pro, grs_pro, ac_clss, pry_yr, curr_yr, tot_name="Gross Profit")
#     return grs_pro

# def get_other_income_expenses(rev_name, ac_cls, ac_code, grs_pro, rev_frm_cus, cos_of_sale, fin_inc, int_exp,
#                               income_tax, pri_yr, cur_yr):
#     other_inc = rev_name[~rev_name[ac_cls].isin([rev_frm_cus, cos_of_sale, fin_inc, int_exp, income_tax])]
#     other_inc = group_sum(other_inc, ac_code, ac_cls, pri_yr, cur_yr, ascending_order=True)
#     opex2 = other_inc.copy()
#     opex2 = pd.concat([opex2, opex2.sum().to_frame().T], ignore_index=True)
#     net_opex = pd.concat([grs_pro.iloc[[-1]], opex2.iloc[[-1]]], ignore_index=True)
#     other_inc = append_sum_row(net_opex, other_inc, ac_cls, pri_yr, cur_yr, tot_name="Operating Profit/(loss)")
#     return other_inc
#
# def get_profit_before_tax(trial_bal, opr_pro, fin_inc, int_exp, ac_codes, ac_clss, pry_yr, curr_yr):
#     net_fin_inc = trial_bal[trial_bal[ac_clss].isin([fin_inc, int_exp])]
#     net_fin_inc = group_sum(net_fin_inc, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
#     net_fin_inc2 = net_fin_inc.copy()
#     net_fin_inc2 = pd.concat([net_fin_inc2, net_fin_inc2.sum().to_frame().T], ignore_index=True)
#     pbit_net = pd.concat([opr_pro.iloc[[-1]], net_fin_inc2.iloc[[-1]]], ignore_index=True)
#     net_fin_inc = append_sum_row(pbit_net, net_fin_inc, ac_clss, pry_yr, curr_yr,
#                                  tot_name="Profit/(loss) before tax")
#     return net_fin_inc
#
# def get_income_tax(trial_bal, net_fin_inc, inc_tax, ac_codes, ac_clss, pry_yr, curr_yr):
#     inc_tax = trial_bal[trial_bal[ac_clss].isin([inc_tax])]
#     inc_tax = group_sum(inc_tax, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
#
#     inc_tax2 = inc_tax.copy()
#     inc_tax2 = pd.concat([inc_tax2, inc_tax2.sum().to_frame().T], ignore_index=True)
#     pat_net = pd.concat([net_fin_inc.iloc[[-1]], inc_tax2.iloc[[-1]]], ignore_index=True)
#     inc_tax = append_sum_row(pat_net, inc_tax, ac_clss, pry_yr, curr_yr, tot_name="Profit/(loss) after tax")
#     return inc_tax


# def create_income_statement(grs_pro, opex, net_fin_inc, inc_tax, oci_2, oci_nrcl, ac_cls):
#     income_stmt = pd.concat([grs_pro, pd.DataFrame(index=range(1)), opex, pd.DataFrame(index=range(1)),
#                              net_fin_inc, pd.DataFrame(index=range(1)), inc_tax, pd.DataFrame(index=range(2)), oci_2,
#                              pd.DataFrame(index=range(2)), oci_nrcl], ignore_index=True)
#     income_stmt = income_stmt.rename(columns={ac_cls: 'Income Statement'})
#     return income_stmt

# def det_inc_stmt(trial_balance_2, fs_class="", p_and_l_items="", oci_items="", rev_frm_customer="", cos_of_sales="",
#                  fin_income="", int_expense="", income_tax="", oci_class_col=None, oci_class=None,
#                  ac_cls="", ac_code="", pri_yr="", cur_yr=""):
#     trial_balance_2.columns = trial_balance_2.columns.astype(str)
#     trial_balance = trial_balance_2[trial_balance_2[fs_class] == p_and_l_items]
#     trial_balance_3 = trial_balance_2[trial_balance_2[fs_class] == oci_items]
#
#     gross_profit = get_gross_profit(trial_balance, rev_frm_customer, cos_of_sales, ac_cls, ac_code, pri_yr, cur_yr)
#     oth_inc = get_other_income_expenses(trial_balance, ac_cls, ac_code, gross_profit, rev_frm_customer, cos_of_sales,
#                                         fin_income, int_expense, income_tax, pri_yr, cur_yr)
#     ebt = get_profit_before_tax(trial_balance, oth_inc, fin_income, int_expense, ac_code, ac_cls, pri_yr, cur_yr)
#     pat = get_income_tax(trial_balance, ebt, income_tax, ac_code, ac_cls, pri_yr, cur_yr)
#     oci_2 = get_oci_recls(trial_balance_3, oci_class_col, oci_class, ac_code, ac_cls, pri_yr, cur_yr)
#     oci_1 = get_oci(trial_balance_3, oci_2, pat, oci_class_col, oci_class, ac_code, ac_cls, pri_yr, cur_yr)
#     income_statement = create_income_statement(gross_profit, oth_inc, ebt, pat, oci_2, oci_1, ac_cls)
#
#     return income_statement

# def get_non_curr_asset(trial_bal, ac_type, non_curr_ass, ac_clss, ac_codes, pry_yr, curr_yr):
#     nca = trial_bal[trial_bal[ac_type] == non_curr_ass]
#     nca = group_sum_bs(nca, ac_codes, ac_clss, curr_yr, ascending_order=False)
#     nca = append_sum_row(nca, nca, ac_clss, pry_yr, curr_yr, tot_name="Total Non-current assets")
#     return nca

# def get_curr_asset(trial_bal, ac_type, nca, curr_ass, ac_clss, ac_codes, pry_yr, curr_yr):
#     cur_asst = trial_bal[trial_bal[ac_type] == curr_ass]
#     cur_asst = group_sum_bs(cur_asst, ac_codes, ac_clss, curr_yr, ascending_order=False)
#     cur_asst = append_sum_row(cur_asst, cur_asst, ac_clss, pry_yr, curr_yr, tot_name="Total Current assets")
#     tot_ass = pd.concat([nca.iloc[[-1]], cur_asst.iloc[[-1]]], ignore_index=True)
#     cur_asst = append_sum_row(tot_ass, cur_asst, ac_clss, pry_yr, curr_yr, tot_name="Total Assets")
#     return cur_asst

# def get_non_curr_liab(trial_bal, ac_type, non_curr_liab, ac_clss, ac_codes, pry_yr, curr_yr):
#     ncl = trial_bal[trial_bal[ac_type] == non_curr_liab]
#     ncl = group_sum(ncl, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
#     ncl = append_sum_row(ncl, ncl, ac_clss, pry_yr, curr_yr, tot_name="Total Non-current liabilities")
#     return ncl

# def get_curr_liab(trial_bal, ac_type, ncl, curr_liab, ac_clss, ac_codes, pry_yr, curr_yr):
#     cur_liabil = trial_bal[trial_bal[ac_type] == curr_liab]
#     cur_liabil = group_sum(cur_liabil, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
#     cur_liabil = append_sum_row(cur_liabil, cur_liabil, ac_clss, pry_yr, curr_yr,
#                                 tot_name="Total Current liabilities")
#     tot_liab = pd.concat([ncl.iloc[[-1]], cur_liabil.iloc[[-1]]], ignore_index=True)
#     cur_liabil = append_sum_row(tot_liab, cur_liabil, ac_clss, pry_yr, curr_yr, tot_name="Total Liabilities")
#     return cur_liabil


# def get_equity(trial_bal, ac_type, equity, tot_liab_row, ac_clss, fs_class, p_and_l_items, oci_items, oci_class,
#                oci_class_col, ac_codes, pry_yr, curr_yr, ret_earn, oci_res=None):
#
#     equi = trial_bal[trial_bal[ac_type] == equity]
#     equi = group_sum(equi, ac_codes, ac_clss, pry_yr, curr_yr, ascending_order=True)
#
#     net_inq = inc_stmt(trial_bal, fs_class, p_and_l_items, ac_codes, ac_clss, curr_yr, pry_yr)
#     oci_non_recl = oci_non_recls(trial_bal, fs_class, oci_items, oci_class_col, oci_class, ac_codes, ac_clss, curr_yr,
#                                  pry_yr)
#     oci_recl = oci_reclass(trial_bal, fs_class, oci_items, oci_class_col, oci_class, ac_codes, ac_clss, curr_yr,
#                            pry_yr)
#
#     pr_af_tx = net_inq.iloc[[-1]]
#     oci_nrecl = oci_non_recl.iloc[[-1]]
#     oci_reclass_2 = oci_recl.iloc[[-1]]
#
#     equi_2 = equi[equi[ac_clss] == ret_earn].index[0]
#     equi.at[equi_2, curr_yr] += pr_af_tx[curr_yr]
#     equi.at[equi_2, pry_yr] += pr_af_tx[pry_yr]
#
#     equi.at[equi_2, curr_yr] += oci_nrecl[curr_yr]
#     equi.at[equi_2, pry_yr] += oci_nrecl[pry_yr]
#
#     if oci_res is not None:
#         equi_3 = equi[equi[ac_clss] == oci_res].index[0]
#         equi.at[equi_3, curr_yr] += oci_reclass_2[curr_yr]
#         equi.at[equi_3, pry_yr] += oci_reclass_2[pry_yr]
#
#     equi = append_sum_row(equi, equi, ac_clss, pry_yr, curr_yr, tot_name="Total Equity")
#
#     tot_liab_equ = pd.concat([equi.iloc[[-1]], tot_liab_row.iloc[[-1]]], ignore_index=True)
#     equi = append_sum_row(tot_liab_equ, equi, ac_clss, pry_yr, curr_yr, tot_name="Total Liabilities and Equity")
#     return equi

# def create_bal_sheet(nca, cur_asst, ncl, cur_liabil, equi, ac_clss):
#     bal_sheet = pd.concat([nca, pd.DataFrame(index=range(1)), cur_asst, pd.DataFrame(index=range(1)),
#                            ncl, pd.DataFrame(index=range(1)), cur_liabil, pd.DataFrame(index=range(1)),
#                            equi], ignore_index=True)
#     bal_sheet = bal_sheet.rename(columns={ac_clss: 'Balance sheet'})
#     return bal_sheet


# def det_bal_sht(trial_balance_2, fs_class="", non_curr_ass="", non_curr_liab="",
#                 curr_liab="", curr_ass="", equity="", ac_clss="", ac_codes="", ac_type="", pry_yr="", curr_yr="",
#                 p_and_l_items="", oci_items="", oci_class='', oci_class_col='', ret_earn='', oci_res=''):
#     trial_balance_2.columns = trial_balance_2.columns.astype(str)
#     non_curr_a = get_non_curr_asset(trial_balance_2, ac_type, non_curr_ass, ac_clss, ac_codes, pry_yr, curr_yr)
#     curr_a = get_curr_asset(trial_balance_2, ac_type, non_curr_a, curr_ass, ac_clss, ac_codes, pry_yr, curr_yr)
#     non_curr_l = get_non_curr_liab(trial_balance_2, ac_type, non_curr_liab, ac_clss, ac_codes, pry_yr, curr_yr)
#     curr_l = get_curr_liab(trial_balance_2, ac_type, non_curr_l, curr_liab, ac_clss, ac_codes, pry_yr, curr_yr)
#     equiii = get_equity(trial_balance_2, ac_type, equity, curr_l, ac_clss, fs_class, p_and_l_items, oci_items, oci_class,
#                         oci_class_col, ac_codes, pry_yr, curr_yr, ret_earn, oci_res)
#
#     bal_shit = create_bal_sheet(non_curr_a, curr_a, non_curr_l, curr_l, equiii, ac_clss)
#
#     return bal_shit

# To do: Breakdown this functions to different python file. Separate the functions from the input, utilities from the main code
# Make the user to be able to choose how to round the figures i.e., million, thousand, etc.
# User should be able to decide the company name if exporting to excel
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
