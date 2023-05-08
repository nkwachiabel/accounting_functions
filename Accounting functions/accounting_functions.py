# Accounting functions created by Nkwachi Abel

from income_statement_fnctions import *
from balance_sheet_functions import *

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
    result = acct_summary(df, fs_class, p_and_l_items, ac_code, ac_cls, num_conv, rounding=rounding, positive=positive,
                          sort_order=True, sum_row=sum_r)
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

def det_bal_sheet(tb, account_type, current_asset, non_current_asset, current_liability, non_current_liability, equity,
                  account_code, account_class, number_converter, rounding, fs_classification, income_statement_items,
                  retained_earnings, oci_to_oci, oci_to_retained_earnings, oci_reserves, current_asset_order,
                  non_current_asset_order, current_liability_order, non_current_liability_order, equity_order):

    curr_asst = get_current_assets(tb, account_type, current_asset, account_code, account_class, number_converter,
                                   rounding, current_asset_order)
    non_curr_asst = get_non_current_assets(tb, account_type, non_current_asset, account_code, account_class,
                                           number_converter, rounding, non_current_asset_order)

    curr_liab = get_current_liabilities(tb, account_type, current_liability, account_code, account_class,
                                        number_converter, rounding, current_liability_order)

    non_curr_liab = get_non_current_liabilities(tb, account_type, non_current_liability, account_code, account_class,
                                                number_converter, rounding, non_current_liability_order)

    equity = get_equity(tb, account_type, equity, fs_classification, income_statement_items, account_code,
                        account_class, retained_earnings, number_converter, rounding, oci_to_oci,
                        oci_to_retained_earnings, oci_reserves, equity_order)

    balance_sheet = create_balance_sheet(non_curr_asst, curr_asst, non_curr_liab, curr_liab, equity, account_class)

    numeric_cols_2 = balance_sheet.select_dtypes(include=['number'])
    if rounding == 0:
        numeric_cols_2 = numeric_cols_2.fillna(0).replace([np.inf, -np.inf], 0).round(rounding).astype(int)
    else:
        numeric_cols_2 = numeric_cols_2.fillna(0).replace([np.inf, -np.inf], 0).round(rounding).astype(float)
    balance_sheet[numeric_cols_2.columns] = numeric_cols_2

    return balance_sheet
