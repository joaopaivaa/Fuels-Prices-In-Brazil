import requests
import pandas as pd
import chardet

def download_LPG(new_months):

    df_lpg = pd.DataFrame()

    for month_year in new_months:
        month, year = month_year.split('/')

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

            try:
                        
                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

            except Exception as e:

                download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/{month_str}-dados-abertos-precos-glp.csv"
             
                try:
                        
                    response = requests.get(download_url)
                    encoding = chardet.detect(response.content)['encoding']

                    df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

                except Exception as e:

                    print(f'LPG: Download - Failed - {year_str}/{month_str}')
                    continue

        print(f'LPG: Download - Ok - {year_str}/{month_str}')

        df_lpg = pd.concat([df_lpg, df_month_year])

    return df_lpg


def download_Gasoline_Ethanol(new_months):

    df_gasoline_ethanol = pd.DataFrame()

    for month_year in new_months:
        month, year = month_year.split('/')

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

            try:

                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

            except Exception as e:

                download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/{month_str}-dados-abertos-precos-gasolina-etanol.csv"
                    
                try:
                        
                    response = requests.get(download_url)
                    encoding = chardet.detect(response.content)['encoding']

                    df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

                except Exception as e:

                    download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/{month_str}-cados-abertos-preco-gasolina-etanol.csv"
                    print(download_url)
                    try:
                            
                        response = requests.get(download_url)
                        encoding = chardet.detect(response.content)['encoding']

                        df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

                    except Exception as e:

                        print(f'Gasoline and Ethanol: Download - Failed - {year_str}/{month_str}')
                        continue
        
        print(f'Gasoline and Ethanol: Download - Ok - {year_str}/{month_str}')

        df_gasoline_ethanol = pd.concat([df_gasoline_ethanol, df_month_year])

    return df_gasoline_ethanol


def download_Diesel_CNG(new_months):

    df_diesel_cng = pd.DataFrame()

    for month_year in new_months:
        month, year = month_year.split('/')

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

            try:

                response = requests.get(download_url)
                encoding = chardet.detect(response.content)['encoding']

                df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

            except Exception as e:

                download_url = f"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsan/{year_str}/{month_str}-dados-abertos-precos-diesel-gnv.csv"
            
                try:
                        
                    response = requests.get(download_url)
                    encoding = chardet.detect(response.content)['encoding']

                    df_month_year = pd.read_csv(download_url, encoding=encoding, sep=';')

                except Exception as e:

                    print(f'Diesel and CNG: Download - Failed - {year_str}/{month_str}')
                    continue

        print(f'Diesel and CNG: Download - Ok - {year_str}/{month_str}')

        df_diesel_cng = pd.concat([df_diesel_cng, df_month_year])

    return df_diesel_cng