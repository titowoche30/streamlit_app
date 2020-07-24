import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import base64
from os import listdir
from os.path import isfile, join
st.set_option('deprecation.showfileUploaderEncoding', False)

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def main():
    st.image('media/eu.jpeg',width=300)
    st.header('Claudemir Woche')
    st.title('Análise de Dados Meteorológicos da Austrália')
    st.image('media/rain_gif.gif')
    
    file_rain = st.file_uploader('Manda o arquivo de rain',type='csv')
    if file_rain is not None:
        df = pd.read_csv(file_rain,parse_dates=['date'])
        n_lin,n_col = df.shape[0],df.shape[1]
        st.markdown(f'**Numero de linhas do arquivo = {n_lin}**')
        st.markdown(f'**Numero de colunas do arquivo = {n_col}**')
        
        slider = st.slider('Número de linhas rain',1,100)
        st.dataframe(df.head(slider))

        st.markdown('**Colunas**')
        st.write(pd.DataFrame(df.columns,columns=['Colunas']))

        st.markdown('**Estatísticas Descritivas sobre os dados**')
        st.dataframe(df.describe())

        st.markdown('**Drop de colunas inconsistentes**')
        m_select = st.multiselect('Selecione as colunas a serem dropadas', ('amountOfRain','temp','humidity','precipitation3pm','precipitation9am'))
        st.markdown(f'Escolheu = {m_select}')
        botao = st.button('Dropar Colunas Selecionadas')
        if botao:
            df.drop(m_select+['modelo_vigente'],axis=1,inplace=True)
            st.markdown('Colunas escolhidas foram dropadas')

        st.markdown('**Construção da Wind Table**')
        botao_1 = st.checkbox('Construir Wind Table')
        wind_table = pd.DataFrame()
        #wind_columns = 0
        if botao_1:
            mypath = "./data/wind_tables"
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            wind_table = pd.DataFrame()
            for file in onlyfiles:
                path = mypath +'/'+ file
                df = pd.read_csv(path,parse_dates=['date'])
                wind_table = pd.concat([wind_table,df],axis=0,sort=True)

            wind_table.to_csv('./data/wind_table_completa.csv',index=False)
            st.markdown('Wind_table construída.')
            
            n_lin,n_col = wind_table.shape[0],wind_table.shape[1]

            st.markdown(f'**Numero de linhas da wind_table = {n_lin}**')
            st.markdown(f'**Numero de colunas da wind_table = {n_col}**')

            st.dataframe(wind_table.head())

            st.markdown('**Colunas**')
            st.write(pd.DataFrame(wind_table.columns,columns=['Colunas']))
            

        botao_2 = st.checkbox('Fazer correspondência entre Wind Table e Rain Data')
        if botao_2:
            wind_table = pd.read_csv('data/wind_table_completa.csv',parse_dates=['date'])
            wind_columns = wind_table.columns
            for col in wind_columns[2:]:
                df[col] = np.nan
            for col in wind_columns[2:5]:
                df[col]=df[col].astype('object')

            
            left = df.set_index(['date', 'location'])
            right = wind_table.set_index(['date', 'location'])

            df=left.join(right, lsuffix='_rain', rsuffix='_wind')
            df.drop(['winddir3pm_rain', 'winddir9am_rain', 'windgustdir_rain',
        'windgustspeed_rain', 'windspeed3pm_rain', 'windspeed9am_rain'],axis=1,inplace=True)

            st.markdown('**Rain Data Completo**')
            st.dataframe(df.head())
            st.markdown('*Colunas*')
            st.write(pd.DataFrame(df.columns,columns=['Colunas']))

        if st.button('Gerar link de download do rain data completo'):
            tmp_download_link = download_link(df, 'rain_data.csv', 'Download')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

        #st.subheader('Faça download do rain data completo abaixo : ')
        #st.markdown(get_table_download_link(df), unsafe_allow_html=True)



            

            

if __name__ == "__main__":
    main()


















