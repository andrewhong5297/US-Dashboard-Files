# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 08:45:24 2020

@author: Andrew
"""
import pandas as pd
import numpy as np
import plotly.express as px

# from cartoframes.auth import set_default_credentials
# set_default_credentials('f2ff22edcd5c21c983f9b952a04044653074796e')
# from cartoframes.data.observatory import Dataset
# dataset = Dataset.get('acs_sociodemogr_b758e778')
# variables_df = dataset.variables.to_dataframe()
'''beige book'''

'''fips dict'''
fips = pd.read_excel(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\FIPS codes.xlsx')

fipsConverter = dict(zip(fips["Name"]+" "+fips["State"],fips["FIPS"])) 

'''demo and income county pickle'''
demog_df = pd.read_excel(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\countyUsPop2018.xlsx')



#will need to pivot county by race (sum) and then by income 2018 (mean), then fipsConvert into names.

'''unemp county pickle (not adjusted)'''
bls_id_df = pd.read_excel(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\US BLS Codes.xlsx')
bls_id_df = bls_id_df[bls_id_df["area_type_code"] == "F"]
bls_id_conv = dict(zip(bls_id_df["area_code"],bls_id_df["area_text"].apply(lambda x: x.strip())))

col_names_conv = {  '03': 'Unemployment Rate',
                    '04':	'Unemployment',
                    '05':	'Employment',
                    '06':	'Labor Force'}

unemp_county = pd.read_excel(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\County Unemployment.xlsx')
unemp_county["Series ID"] = unemp_county["Series ID"].replace("LAU","",regex=True)

#conv ID to column names
unemp_county["Data Type"] = unemp_county["Series ID"].apply(lambda x: x[-2:])
unemp_county["Data Type"] = unemp_county["Data Type"].apply(lambda x: col_names_conv[x])

#conv ID to county names
unemp_county["County Name"] = unemp_county["Series ID"].apply(lambda x: x[:-2])
unemp_county["County Name"] = unemp_county["County Name"].apply(lambda x: bls_id_conv[x])

#conv ID to fips code
unemp_county["fips"] = unemp_county["Series ID"].apply(lambda x: x[2:7])

CountyFipsConverter = dict(zip(unemp_county["County Name"],unemp_county["fips"])) 
FipsCountyConverter = dict(zip(unemp_county["fips"],unemp_county["County Name"])) 

new = unemp_county["County Name"].str.split(", ", n = 1,expand=True)

unemp_county["County"] = new[0]
unemp_county["State"] = new[1]
# unemp_county.drop(columns =["County Name"], inplace = True) 

unemp_county.to_csv('unemp_county_small.csv')

# with pd.ExcelWriter(
#     r"unemp_county_small.xlsx"
# ) as writer:
#     unemp_county.to_excel(writer, sheet_name="Headlines")

# unemp_county.set_index(["Series ID","Data Type","County Name","fips"],inplace=True)  

# unemp_county = unemp_county.stack()
# unemp_county = unemp_county.reset_index()

# unemp_county.columns = ["Series ID","Data Type","County Name","fips", "Date", "Value"]
# unemp_county["Date"] = pd.to_datetime(unemp_county["Date"])


# unemp_county.drop(columns =["County Name"], inplace = True) 

# unemp_county["Month"] = unemp_county["Date"].dt.month
# unemp_county["Year"] = unemp_county["Date"].dt.year

# unemp_county.iloc[:700000,:].to_csv('unemp_county_1.csv')
# unemp_county.iloc[700000:,:].to_csv('unemp_county_2.csv')

# with pd.ExcelWriter(
#     r"unemp_county_1.xlsx"
# ) as writer:
#     unemp_county.iloc[:700000,:].to_excel(writer, sheet_name="Headlines")
    
# with pd.ExcelWriter(
#     r"unemp_county_2.xlsx"
# ) as writer:
#     unemp_county.iloc[700000:,:].to_excel(writer, sheet_name="Headlines")

# unemp_county.iloc[:700000,:].to_pickle(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\county_unemp_1.pkl')
# unemp_county.iloc[700000:,:].to_pickle(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\county_unemp_2.pkl')


'''unemp_county by industry'''
met_area_industry = pd.read_excel(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\BLS Met Area Industry Employment Data.xlsx')
met_area_industry.set_index(["Met Area","State","Industry"],inplace=True)

met_area_industry = met_area_industry.replace(",","",regex=True)
met_area_industry = met_area_industry.astype(float)
# met_area_industry = met_area_industry.pct_change(axis=1)*100 

met_area_industry = met_area_industry.stack()
met_area_industry = met_area_industry.reset_index()

met_area_industry.columns = ["Met Area", "State", "Industry", "Date", "Employment"]
met_area_industry["Date"] = pd.to_datetime(met_area_industry["Date"])

#map county to met area
fips_to_cbsa = pd.read_excel(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\FIPS to CBSA.xlsx')

NametoCbsaConverter = dict(zip(fips_to_cbsa["CBSA NAME"],fips_to_cbsa["CBSA"])) 
FipstoCbsaConverter = dict(zip(fips_to_cbsa["FIPS"],fips_to_cbsa["CBSA"])) 

met_area_industry["Month"] = met_area_industry["Date"].dt.month
met_area_industry["Year"] = met_area_industry["Date"].dt.year

#creating CBSA values 
met_area_industry["CBSA"] = met_area_industry["Met Area"].apply(lambda x: NametoCbsaConverter[x])
met_area_industry.to_pickle(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\met_area_unemp.pkl')

#drop 0's that don't exist for some reason

# import json
# with open(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\cbsa.tiger2013.json') as json_file:
#     MSA_json = json.load(json_file)
# #map county to fips

'''state unemp'''
df = pd.read_excel(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\BLS Met Area State Industry Employment Data.xlsx')
df.set_index(["State","Met Area","Industry"],inplace=True)

#getting rid of commas
df = df.replace(",","",regex=True)
df = df.astype(float)
df = df.pct_change(axis=1)*100 

df = df.stack()
df = df.reset_index()

df.columns = ["State","Met Area","Industry", "Date", "Employment"]
df["Date"] = pd.to_datetime(df["Date"])

df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year

df.to_pickle(r'C:\Users\Andrew\Documents\PythonScripts\github repos\US Dashboard Files\US-Dashboard-Files\state_unemp_notional.pkl')

temp_df = df[df["Industry"]=='Leisure  Hospitality']
temp_df = temp_df[temp_df["Date"] == "2020-04-01"]
