import pandas as pd
import re
from word2number import w2n
import os
import glob

# file import path
path_ = r"C:\Manish Kr Mandal\sales_data\dataset"

datalist = []

# read all csv file 
for file in os.listdir(path_):

    if file.endswith('csv'):
        data_ = os.path.join(path_,file)
        dataset = pd.read_csv(
            data_,header=None
        )

        for index, row in dataset.iterrows():

            header = None

            if row.str.strip().str.lower().str.contains('order_date').any():
                header = index
                break

        remove_junk_header = dataset.iloc[header:]
        remove_junk_header.columns = remove_junk_header.iloc[0]
        sales_data = remove_junk_header.iloc[1:].reset_index(drop=True)
        datalist.append(sales_data)

# combine file  
df = pd.concat(
    datalist,ignore_index=True
)

# funtion for text column
def clean_data (col):
    if pd.isna(col):
        return pd.NA

    x = str(col)
    x = re.sub(r'\s+',' ',x).strip().lower()
    return x

# def funtion for numaric column
def number_clean(col):
    if pd.isna(col):
        return pd.NA

    x = str(col)
    try:
        x = str(w2n.word_to_num(x))
    except:
        pass
    x = re.sub(r'(?i)^rs\.?\s*','',x)
    x = re.sub(r'[^0-9.]','',x)
    return x

# def funtion apply
for col in df.columns:
    df[col] = df[col].astype('str').apply(clean_data)
    if col in ['quantity','unit_price','discount_pct']:
        df[col] = df[col].apply(number_clean)

# remove junk column where 50% data not avaiable
junk_col = df.isna().mean() * 100
col_ = junk_col[junk_col > 50].index
df = df.drop(columns=col_)

# remove record where 50% record are blank or null
junk_row = df.isna().mean(axis=1) * 100
record = junk_row[junk_row > 50].index
df = df.drop(index=record)

# clean city column miss match format
city_map = {
    'calcutta':'kolkata',
    'bombay':'mumbai',
    'delhi':'new delhi',
    'gurugram':'gurgaon'
}

df['city'] = df['city'].replace(city_map)

# handle missing data
num_col = ['quantity','unit_price','discount_pct']
for col in df.columns:

    if col not in num_col:
        df[col] = df[col].fillna('unknown')
    else:
        df[num_col] = df[num_col].fillna(0)

# datatype change

for namecol in df.columns:

    datecoll = pd.to_datetime(

        df[namecol],dayfirst=True,format='mixed',errors='coerce'
    )

    if datecoll.notna().all():
        df[namecol] = datecoll.astype('datetime64[ns]')

    else:

        numcol = pd.to_numeric(
            df[namecol],errors='coerce'
        )

        if numcol.notna().all():

            if (numcol % 1 == 0).all():
                df[namecol] = numcol.astype('Int64')
            else:
                df[namecol] = numcol.astype('float64')
        else:
            df[namecol] = df[namecol].astype('str')


print(df)

