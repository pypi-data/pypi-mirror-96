import re
import pandas as pd
import numpy as np
import matplotlib, matplotlib.pyplot as plt
import seaborn as sns
import time

def df_convert_32(df):
    for c in df.columns:
        if df.dtypes[c]==np.int64: df.loc[:,c]=df[c].astype(np.int32)
        if df.dtypes[c]==np.float64: df.loc[:,c]=df[c].astype(np.float32)

def df_parse_date_from_int(df, c):
    df.loc[df[c].isna(),c] = 0
    df.loc[:,c] = df.loc[:,c].astype(int)
    df.loc[:,c] = df[c].apply(lambda n: f'{int(n/10000)}-{int(n%10000/100)}-{int(n%100)}')
    df.loc[:,c] = pd.to_datetime(df[c], format='%Y-%m-%d', errors='coerce')

def df_lookup(df,c,d,na_val='Desconhecido'):
    """Changes in-place columns c of dataframe df with lookup values defined on dictionary d and na_val if not found"""
    df.loc[df[c].isna(),c] = na_val
    df.loc[:,c] = df[c].apply(lambda v: d[v] if v in d else na_val)

def df_to_int(df, c, na_val=-1):
    """Changes float col to int replacing NA with na_val"""
    df.loc[:,c] = df[c].fillna(na_val)
    df.loc[:,c] = df.loc[:,c].astype(int)

def df_cats_to_str(df):
    """Converts all cat cols to str"""
    for c in df.select_dtypes(include=['category']).dtypes.index:
        df[c] = df[c].astype(str)

# Change to operate inplace
def df_reduce_cats(df, c, freq=10):
    """Keeps only the values of cat col that have more than freq occurrencies"""
    dfc = pd.DataFrame(df[c].value_counts()).reset_index()
    dfc.columns = ['__key', '__val']
    dfc = dfc[dfc['__val']>freq]
    dfc = dfc.set_index(['__key'])
    dfc['__val'] = dfc.index
    df = df.join(dfc, how='left', on=c)
    df = df.drop([c], axis=1)
    df = df.rename(columns={'__val': c})
    return df

def df_cut_numeric(df, c, bins, na_val=-1):
    bins = [na_val-1] + bins
    labels = ['NA'] + [str(e) for e in bins[1:-1]]
    df_to_int(df, c)
    df.loc[:,c+'_cat'] = pd.cut(df.loc[:,c], bins, labels=labels)
    df.loc[:,c+'_cat'] = df.loc[:,c+'_cat'].astype(str)

DATE_PARTS = ['Year', 'Month', 'Week', 'Day', 'Dayofweek', 'Dayofyear', 'Is_month_end', 'Is_month_start', 
        'Is_quarter_end', 'Is_quarter_start', 'Is_year_end', 'Is_year_start']

def datepart_cols(fldname):
    fldname2_pre = re.sub('[Dd]ate$', '', fldname)
    return [f'{fldname2_pre}_{e}' for e in DATE_PARTS] + [f'{fldname2_pre}_Elapsed']

def df_add_datepart(df, fldname, drop=True):
    fld = df[fldname]
    fld_dtype = fld.dtype
    if isinstance(fld_dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
        fld_dtype = np.datetime64
    if not np.issubdtype(fld_dtype, np.datetime64):
        df[fldname] = fld = pd.to_datetime(fld, infer_datetime_format=True)
    fldname2_pre = re.sub('[Dd]ate$', '', fldname)
    for e in DATE_PARTS:
        df[f'{fldname2_pre}_{e}'] = getattr(fld.dt,e.lower())
    df[f'{fldname2_pre}_Elapsed'] = fld.astype(np.int64) // 10**9
    if drop: df.drop(fldname, axis=1, inplace=True)
    return [fldname2_pre+'_'+e for e in DATE_PARTS]

def df_join_by_range_2(df, df_range, df_range_key, key_c, v_c, v1_c, v2_c, ignore_max=False):
    """ Joins dataframes with df_range based on secondary key_c and value range
        df is the original dataframe
        df_range is the lookup dataframe, with unique key df_range_key
        Both df and df_range have rows split in subsets defined by secondary key key_c
        Joins column v_c in df into range values in df_range v1_c, v2_c
        If ignore_max=True v2_c is ignored 
        Returns joined dataframe, and three dataframe with missed keys, missed by range min and max
    """
    
    # Reset Index of df if there is an index and index df_range by key_c if not yet done
    df['__idx__'] = df.index
    df.set_index(['__idx__'])
    if df_range.index.names != [key_c]:
        if df_range.index.names != [None]:
            df_range = df_range.reset_index()
        df_range = df_range.set_index([key_c])
        
    # Create two columns with the min and max values for every key_c subset in df_range
    df_limits = df_range[[v1_c, v2_c]].groupby(level=[key_c])\
        .agg({v1_c: 'min', v2_c: 'max'}) \
        .rename(columns={v1_c: '__min', v2_c: '__max'})
    df_range = df_range.join(df_limits)
    df2 = df.join(df_range[[df_range_key, v1_c, v2_c, '__min', '__max']], on=[key_c])
    df_miss = df[~df[key_c].isin(df_range.index)].drop(columns=['__idx__'])
    df_miss_min = df2[df2[v_c]<df2['__min']]
    df_miss_min = df_miss_min.drop_duplicates(subset=['__idx__']).drop(columns=['__idx__'])
    df_miss_max = df2[df2[v_c]>df2['__max']]
    df_miss_max = df_miss_max.drop_duplicates(subset=['__idx__']).drop(columns=['__idx__'])
    df = df2[(df2[v_c]>=df2[v1_c])&(df2[v_c]<=df2[v2_c])]
    if ignore_max: df = pd.concat([df, df_miss_max])
    df = df.drop(columns=['__idx__']).copy()
    df['key'] = df['key'].astype(int)
    return df, df_miss, df_miss_min, df_miss_max

def df_meta(df, order=False):
    data = []
    for c in df.columns:
        unq = len(df[c].cat.categories) if df[c].dtype.name == 'category' else len(df[c].unique())
        examples = '; '.join([str(e) for e in df[c].value_counts().index[:5]]) 
        data.append((c, df[c].dtypes, unq, unq/len(df), df[c].isna().sum(), df[c].isna().sum()/len(df), examples))
    df1 = pd.DataFrame(data, columns=['attr', 'type', 'uniques', 'uniques_p', 'nulls', 'nulls_p', 'examples'])
    if order: df1.sort_values(['uniques'], ascending=False, inplace=True)
    return df1

def df_meta_excel(df, fname):
    writer = pd.ExcelWriter(f'{fname}.xlsx', engine='xlsxwriter')
    df1 = df_meta(df, order=False)
    df1.to_excel(writer, 'Original order')
    df1 = df_meta(df, order=True)
    df1.to_excel(writer, 'Uniques order')
    writer.save()

def df_stats(df, c, max_rows=10):
    n = len(df)
    nna = len(df[df[c].isna()])
    nu = len(df[c].unique())
    print(f'\n\033[1mCol: {c}\033[0m')
    print(f'Total: {n:,}    NA: {nna:,} ({100*nna/n:.2f}%)'.replace(',', '.'))
    print(f'Uniques: {nu:,} ({100%nu/n:.2f}%)'.replace(',', '.'))
    s = df[c].value_counts()
    data = []
    n1, p1, p2 = 0, 0.0, 0.0
    for idx, t in s.head(max_rows).items():
        data.append([idx, t, 100*t/n, 100*t/(n-nna)])
        n1 += t
        p1 += t/n
        p2 += t/(n-nna)
    if (n-nna)-n1 > 0:
        data.append(['Etc', (n-nna)-n1, 100*(1-p1), 100*(1-p2)])
    cols = ['Value', '#', '%', '%2']
    df1 = pd.DataFrame(data, columns=cols)
    return df1

def format_chart(ax, title, ylabel, wtotal, max_x, w):
    xlabel = ''
    sns.set(font_scale=1)
    title = '' if title is None else title    
    xlabel = '' if xlabel is None else xlabel
    ylabel = '' if ylabel is None else ylabel
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(xlabel, fontsize=12, rotation='vertical')
    ax.set_ylabel(ylabel, fontsize=12, rotation='vertical')
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', '.')))
    for p in ax.patches:
        p.set_height(1)
        width = p.get_width()
        ax.text(width+max_x*0.02*(15/w), p.get_y()+p.get_height()*0.7, '{:1.2f}'.format(width/wtotal), ha='center')
    plt.subplots_adjust(hspace = 1.0)

def df_hist(df, col, n=None):
    """Calc hist with the n largest bins, or up to 99% of values if n is None"""
    x = df[col].value_counts().values
    y = list(df[col].value_counts().index.values)
    if n is None:
        total, t = sum(x), 0
        for k,e in enumerate(x):
            t += e
            if t>=total*0.99:
                break
        k += 1
        n = k if len(df[col].value_counts())>k else len(df[col].value_counts())
    if n<len(df[col].value_counts()):
        r = sum(x[n:])
        x, y = x[:n], y[:n]
        x, y = np.append(x, [r]), np.append(y, ['Etc'])
        n += 1
    return x, y, n


def df_plot(df, cols, n=None, grid_cols=2, w=15, as_cat=False, stats=False):
    if not isinstance(cols, list):
        cols, grid_cols = [cols], 1
        w = 8
    if stats:
        for col in cols:
            df1 = df_stats(df, col)
            display(df1)
    grid_rows = len(cols)//grid_cols
    nrows = []
    is_cat = df[col].dtype in ['object'] or as_cat or df[col].nunique()<10
    for i,col in enumerate(cols):
        if is_cat: _, _, n1 = df_hist(df, col, n)
        else: n1 = 10
        nrows.append(n1)
    n1 = 0
    ncols = len(cols)//2
    if ncols==0: ncols+=1
    for i in range(ncols): n1 += max(nrows[i], nrows[i]+1)
    h = (n1-1)*0.3 + 1.
    fig = plt.figure(figsize=(w, h))
    for i,col in enumerate(cols):
        ax = plt.subplot(grid_rows,grid_cols,i+1)
        if is_cat:
            x, y, _ = df_hist(df, col, n)
            ax = sns.barplot(y=y, x=x, orient='h')
            format_chart(ax, col, '#', float(len(df)), max(x)*grid_cols, w)
        else:
            bins, kde = 'auto', True
            if pd.api.types.is_integer_dtype(df[col]):
                nu = df[col].nunique()
                bins = nu if nu<20 else 20
                kde = False
            ax = sns.histplot(df[col], bins=bins, kde=kde)
        plt.gca().set_facecolor((1.0, 1.0, 1.0))
    plt.tight_layout()
    plt.show()
    plt.pause(.01)
    # plt.close('all')
