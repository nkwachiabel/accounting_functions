from utilities import *


def get_current_assets(tb, ac_type, curr_assets, ac_code, ac_cls, num_conv, rounding, curr_asset_order=None):
    if curr_assets is None:
        current_assets = None
    else:
        current_assets = tb.copy()
        current_assets = acct_summary(current_assets, ac_type, curr_assets, ac_code, ac_cls, num_conv, rounding=rounding,
                                      positive=True, sum_row='Total current assets')
        if curr_asset_order is not None:
            if len(curr_asset_order) != len(current_assets[ac_cls]):
                print("Error: Current Assets list length does not match the number of Current Assets")
            else:
                current_assets[ac_cls] = pd.Categorical(current_assets[ac_cls], categories=curr_asset_order,
                                                        ordered=True)
                current_assets = current_assets.sort_values(ac_cls, ignore_index=True)
        else:
            print("Error: Current Assets Ordering is not specified")
    return current_assets


def get_non_current_assets(tb, ac_type, non_curr_assets, ac_code, ac_cls, num_conv, rounding,
                           non_curr_asset_order=None):
    if non_curr_assets is None:
        non_current_assets = None

    else:
        non_current_assets = tb.copy()
        non_current_assets = acct_summary(non_current_assets, ac_type, non_curr_assets, ac_code, ac_cls, num_conv,
                                          rounding=rounding, positive=True, sum_row='Total non-current assets')

        if non_curr_asset_order is not None:
            if len(non_curr_asset_order) != len(non_current_assets[ac_cls]):
                print("Error: Non-Current Asset list length does not match the number of Non-Current assets")
            else:
                non_current_assets[ac_cls] = pd.Categorical(non_current_assets[ac_cls], categories=non_curr_asset_order,
                                                            ordered=True)
                non_current_assets = non_current_assets.sort_values(ac_cls, ignore_index=True)
        else:
            print("Error: Non-Current Asset ordering is not specified")

    return non_current_assets


def get_current_liabilities(tb, ac_type, curr_liab, ac_code, ac_cls, num_conv, rounding, curr_liabilities_order=None):
    if curr_liab is None:
        current_liabilities = None
    else:
        current_liabilities = tb.copy()
        current_liabilities = acct_summary(current_liabilities, ac_type, curr_liab, ac_code, ac_cls, num_conv,
                                           rounding=rounding, positive=False, sum_row='Total current liabilities')
        if curr_liabilities_order is not None:
            if len(curr_liabilities_order) != len(current_liabilities[ac_cls]):
                print("Error: Current Liabilities list length does not match the number of Current Liabilities")
            else:
                current_liabilities[ac_cls] = pd.Categorical(current_liabilities[ac_cls],
                                                             categories=curr_liabilities_order, ordered=True)
                current_liabilities = current_liabilities.sort_values(ac_cls, ignore_index=True)
        else:
            print("Error: Current Liabilities ordering is not specified")

    return current_liabilities


def get_non_current_liabilities(tb, ac_type, non_curr_liab, ac_code, ac_cls, num_conv, rounding,
                                non_curr_liabilities_order=None):
    if non_curr_liab is None:
        non_current_liabilities = None

    else:
        non_current_liabilities = tb.copy()
        non_current_liabilities = acct_summary(non_current_liabilities, ac_type, non_curr_liab, ac_code, ac_cls,
                                               num_conv, rounding=rounding, positive=False, sum_row='Total non-current liabilities')
        if non_curr_liabilities_order is not None:
            if len(non_curr_liabilities_order) != len(non_current_liabilities[ac_cls]):
                print("Error: Non-Current Liabilities list length does not match the number of Non-Current Liabilities")
            else:
                non_current_liabilities[ac_cls] = pd.Categorical(non_current_liabilities[ac_cls],
                                                                 categories=non_curr_liabilities_order, ordered=True)
                non_current_liabilities = non_current_liabilities.sort_values(ac_cls, ignore_index=True)
        else:
            print("Error: Non-Current Liabilities order is not specified")

    return non_current_liabilities

def get_equity(tb, ac_type, equi, fin_stat_class, inco_stmt, ac_code, ac_cls, ret_earning,
               num_conv, rounding, oci_to_oci=None, oci_to_ret_earn=None, oci_reserves=None, equi_order=None):
    if equi is None:
        equities = None

    else:
        equities = tb.copy()
        equities = acct_summary(equities, ac_type, equi, ac_code, ac_cls, num_conv, rounding=rounding, positive=False,
                                sum_row='Total Equity')

        if equi_order is not None:
            if len(equi_order) != len(equities[ac_cls]):
                # equities
                print("Error: Equities list length does not match 'Account Class' column length")
            else:
                equities[ac_cls] = pd.Categorical(equities[ac_cls], categories=equi_order, ordered=True)
                equities = equities.sort_values(ac_cls, ignore_index=True)
        else:
            print("Error: Equities order is not specified")
            # equities

    net_income = acct_summary(tb, fin_stat_class, inco_stmt, ac_code, ac_cls, num_conv, rounding=rounding,
                              positive=False, sort_order=True)
    net_income = net_income.select_dtypes(include=['number']).iloc[-1]

    # Get the index of the Retained earnings row
    equi_2 = equities[equities[ac_cls] == ret_earning].index[0]

    # Update only the numeric columns of the Retained earnings row
    equities.loc[equi_2, equities.select_dtypes(include=['number']).columns] += net_income

    # Update the retained earnings with oci items that will not be reclassified to retained earnings
    if oci_to_ret_earn is not None:
        oci_2_ret_ear = acct_summary(tb, fin_stat_class, oci_to_ret_earn, ac_code, ac_cls, num_conv, rounding=rounding,
                                     positive=False)
        oci_2_ret_ear = oci_2_ret_ear.select_dtypes(include=['number']).iloc[-1]
        equities.loc[equi_2, equities.select_dtypes(include=['number']).columns] += oci_2_ret_ear

    # Update the oci reserves with items that may be reclassified to retained earnings
    if oci_to_oci is not None:
        oci_2 = equities[equities[ac_cls] == oci_reserves].index[0]
        oci_2_oci = acct_summary(tb, fin_stat_class, oci_to_oci, ac_code, ac_cls, num_conv, rounding=rounding,
                                 positive=False)
        oci_2_oci = oci_2_oci.select_dtypes(include=['number']).iloc[-1]
        equities.loc[oci_2, equities.select_dtypes(include=['number']).columns] += oci_2_oci

    # Get the total equity after including the retained earnings
    new_equity = equities.iloc[:-1]
    numeric_cols = new_equity.select_dtypes(include=['number'])
    total_row = new_equity.select_dtypes(include=['number']).sum()
    total_row[ac_cls] = 'Total equity'
    new_equity = pd.concat([new_equity, total_row.to_frame().T], ignore_index=True)
    new_equity[numeric_cols.columns] = new_equity[numeric_cols.columns].apply(pd.to_numeric, errors='coerce')

    return new_equity

def create_balance_sheet(non_current_asset, current_asset, non_current_liabilities, current_liabilities, equities, ac_cls):
    total_assets = append_sum_row(non_current_asset, current_asset, ac_cls, tot_name="Total assets")
    total_liabilities = append_sum_row(non_current_liabilities, current_liabilities, ac_cls, tot_name="Total liabilities")
    total_liabilities_and_equity = append_sum_row(total_liabilities, equities, ac_cls, tot_name="Total liabilities and equity")

    balance_sheet = pd.concat([non_current_asset, pd.DataFrame(index=range(1)), total_assets, pd.DataFrame(index=range(1)),
                               non_current_liabilities, pd.DataFrame(index=range(1)), total_liabilities,
                               pd.DataFrame(index=range(1)), total_liabilities_and_equity], ignore_index=True)
    return balance_sheet
