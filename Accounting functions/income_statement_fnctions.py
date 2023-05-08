from utilities import *

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
