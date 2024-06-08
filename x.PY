import requests
import pandas as pd
from zipfile import ZipFile
from io import BytesIO

# Function to download and extract the CSV files from the link
def download_and_extract_csv(download_link):
    response = requests.get(download_link)
    if response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zipfile:
            csv_files = [zipfile.open(name) for name in zipfile.namelist() if name.endswith('.csv')]
            return csv_files
    else:
        raise Exception(f"Failed to download the file: {response.status_code}")

# Function to process the CSV files and select specific columns
def process_csv_files(csv_files):
    columns_of_interest = ["ANO / MÊS", "UF", "NOME AÇÃO", "VALOR TRANSFERIDO"]
    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, sep=';', encoding='latin1')  # Adjust separator and encoding as needed
            selected_columns = df[columns_of_interest]
            df_list.append(selected_columns)
        except Exception as e:
            print(f"Error processing file {file}: {e}")
    return pd.concat(df_list, ignore_index=True)

# Function to display total entries for each UF
def UFTotal(df):
    print(df['UF'].value_counts())

# Function to display available options for "NOME AÇÃO" and select types
def select_nome_acao_types(df, num_types=20):
    nome_acao_options = df['NOME AÇÃO'].unique()
    print(f"Available options for 'NOME AÇÃO' ({len(nome_acao_options)} in total):")
    for i, option in enumerate(nome_acao_options[:num_types], start=1):
        print(f"{i}. {option}")
    start_index = num_types
    while True:
        more_options = input("Do you want to see more options? (yes/no): ").lower()
        if more_options == 'yes':
            end_index = min(len(nome_acao_options), start_index + num_types)
            for i, option in enumerate(nome_acao_options[start_index:end_index], start=start_index+1):
                print(f"{i}. {option}")
            start_index = end_index
        elif more_options == 'no':
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

# Function to select "NOME AÇÃO" and "UF" and display information
def select_nome_acao_and_uf(df):
    while True:
        try:
            nome_acao_input = int(input("Select the 'NOME AÇÃO' option by number: "))
            uf_input = input("Digite a UF desejada (ex: BA): ").upper()
            nome_acao_options = df['NOME AÇÃO'].unique()
            selected_nome_acao = nome_acao_options[nome_acao_input - 1]
            filtered_df = df[(df['NOME AÇÃO'] == selected_nome_acao) & (df['UF'] == uf_input)]
            
            # Display the first batch of rows
            start_index = 0
            end_index = min(len(filtered_df), start_index + 50)
            print(filtered_df.iloc[start_index:end_index])

            # Ask if the user wants to see more results
            while end_index < len(filtered_df):
                more_results = input("Do you want to see more results? (yes/no): ").lower()
                if more_results == 'yes':
                    start_index = end_index
                    end_index = min(len(filtered_df), start_index + 50)
                    print(filtered_df.iloc[start_index:end_index])
                elif more_results == 'no':
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
            
            # Ask if the user wants to see results for another specification
            more_specification = input("Do you want to see results for another specification? (yes/no): ").lower()
            if more_specification == 'no':
                break
        except ValueError:
            print("Invalid input. Please enter a valid number for 'NOME AÇÃO'.")
        except KeyError:
            print("Invalid UF or 'NOME AÇÃO' option.")

def main():
    # Direct download link for the zip file
    ano_mes = input("Digite o ano e mês desejado [Formato: AAAAMM]: ")
    download_link = f'https://portaldatransparencia.gov.br/download-de-dados/transferencias/{ano_mes}'

    try:
        csv_files = download_and_extract_csv(download_link)
        df = process_csv_files(csv_files)
        UFTotal(df)
        
        # Display available options for "NOME AÇÃO" and select types
        select_nome_acao_types(df)
        
        # Select "NOME AÇÃO" and "UF" and display information
        select_nome_acao_and_uf(df)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()