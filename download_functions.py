import requests
import pandas as pd
import chardet

def download_LPG(first_month, first_year, last_month, last_year):

    years = range(first_year, last_year + 1)
    months = range(first_month, last_month + 1)

    df_lpg = pd.DataFrame()

    for year in years:
        for month in months:

            year_str = str(year)
            month_str = str(month)

            month_str = '0' + month_str if len(month_str) == 1 else month_str

            download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/precos-glp-{month_str}.csv"

            try:
                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')
            
            except Exception as e:

                download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/dados-abertos-precos-{year_str}-{month_str}-glp.csv"

                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

            print(f'LPG: Download - Ok - {year_str}/{month_str}')

            df_lpg = pd.concat([df_lpg, df_month_year])

    return df_lpg


def download_Gasoline_Ethanol(first_month, first_year, last_month, last_year):

    years = range(first_year, last_year + 1)
    months = range(first_month, last_month + 1)

    df_gasoline_ethanol = pd.DataFrame()

    for year in years:
        for month in months:

            year_str = str(year)
            month_str = str(month)

            month_str = '0' + month_str if len(month_str) == 1 else month_str

            download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/precos-gasolina-etanol-{month_str}.csv"
            
            try:
                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')
            
            except Exception as e:

                download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/dados-abertos-precos-{year_str}-{month_str}-gasolina-etanol.csv"

                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

            print(f'Gasoline and Ethanol: Download - Ok - {year_str}/{month_str}')

            df_gasoline_ethanol = pd.concat([df_gasoline_ethanol, df_month_year])

    return df_gasoline_ethanol


def download_Diesel_CNG(first_month, first_year, last_month, last_year):

    years = range(first_year, last_year + 1)
    months = range(first_month, last_month + 1)

    df_diesel_cng = pd.DataFrame()

    for year in years:
        for month in months:

            year_str = str(year)
            month_str = str(month)

            month_str = '0' + month_str if len(month_str) == 1 else month_str

            download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/precos-diesel-gnv-{month_str}.csv"

            try:
                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')
            
            except Exception as e:

                download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/dados-abertos-precos-{year_str}-{month_str}-diesel-gnv.csv"

                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

            print(f'LPG: Download - Ok - {year_str}/{month_str}')

            df_diesel_cng = pd.concat([df_diesel_cng, df_month_year])

    return df_diesel_cng