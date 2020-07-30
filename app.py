import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import altair as alt

st.set_option('deprecation.showfileUploaderEncoding', False)

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


def cat_input(df,cat_cols):
    modes = df[cat_cols].mode().values[0]
    filter = dict(zip(cat_cols,modes))

    df = df.fillna(filter)
    return df

#histograma,barras,boxplot,scatterplot,correlação
def histogram(df,col,split=False):
    if split:
        fig = alt.Chart(df,width=600,height=400).mark_bar().encode(alt.X(col+':Q', bin=True,title=col),alt.Y('count()',title='Count'),color=split+':O',tooltip = ['count()',split]).interactive()
    else:
        fig = alt.Chart(df,width=600,height=400).mark_bar().encode(alt.X(col+':Q', bin=True,title=col),alt.Y('count()',title='Count'),tooltip = [col,'count()']).interactive()

    return fig

def bar(df,x_axis,y_axis,split=False):
    if split:
        fig = alt.Chart(df,width=400,height=200).mark_bar().encode(alt.X(x_axis+':O', title=x_axis),alt.Y(y_axis+':Q',title=y_axis),column = split+':O',tooltip = [x_axis,y_axis,split]).interactive()
    else:
        fig = alt.Chart(df,width=600,height=400).mark_bar().encode(alt.X(x_axis+':O', title=x_axis),alt.Y(y_axis+':Q',title=y_axis),tooltip = [x_axis,y_axis]).interactive()

    return fig

def boxplot(df,y_axis,x_axis=False):
    if x_axis:
        fig = alt.Chart(df,width=600,height=400).mark_boxplot().encode(alt.X(x_axis+':O', title=x_axis),alt.Y(y_axis+':Q',title=y_axis),tooltip = [y_axis]).interactive()
    else:
        fig = alt.Chart(df,width=600,height=400).mark_boxplot().encode(alt.Y(y_axis+':Q',title=y_axis),tooltip = [y_axis]).interactive()

    return fig

def scatter(df,x_axis,y_axis,split=False):
    if split:
        fig = alt.Chart(df,width=600,height=400).mark_circle().encode(alt.X(x_axis+':Q', title=x_axis),alt.Y(y_axis+':Q',title=y_axis),color=split,tooltip = [x_axis,y_axis,split]).interactive()
    else:
        fig = alt.Chart(df,width=600,height=400).mark_circle().encode(alt.X(x_axis+':Q', title=x_axis),alt.Y(y_axis+':Q',title=y_axis),tooltip = [x_axis,y_axis]).interactive()

    return fig

def corre(df):
    cor_data = (df.corr().stack().reset_index().rename(columns={0: 'correlation', 'level_0': 'X', 'level_1': 'Y'}))
    cor_data['correlation_label'] = cor_data['correlation'].map('{:.2f}'.format)
    base=alt.Chart(cor_data,width=600,height=400).encode(x='X:O',y='Y:O')
    
    text = base.mark_text().encode(text='correlation_label',color=alt.condition(alt.datum.correlation > 0.5, alt.value('white'),alt.value('black'))).interactive()
    cor_plot = base.mark_rect().encode(color='correlation:Q')

    return cor_plot + text



def main():
    st.image('media/eu.jpeg',width=300)
    st.header('Pré-processador do Tito')
    st.image('media/neo.gif')
    
    file = st.file_uploader('Manda o arquivo CSV',type='csv')
    if file is not None:
        df = pd.read_csv(file)
        st.markdown(f'**Shape do arquivo = {df.shape}**')

        slider = st.slider('Número de linhas',1,100)
        st.dataframe(df.head(slider))

        st.markdown('**Colunas**')
        df_cols = pd.DataFrame({'colunas':df.columns,'tipos':df.dtypes}).reset_index(drop=True)
        df_null_bolean = df.isnull()
        nulls_sum_cols = df_null_bolean.sum().values
        df_cols['Número de NULLS na coluna'] = nulls_sum_cols
        df_cols['Taxa de NULLS na coluna'] = nulls_sum_cols / df.shape[0]
        null_cols = df.columns[df_cols['Número de NULLS na coluna'] > 0]
        st.write(pd.DataFrame(df_cols))

        st.markdown('**Estatísticas Descritivas sobre os dados numéricos**')
        st.dataframe(df.describe())

        st.markdown('Amostras com nulos')
        df_nulos = df[df_null_bolean.any(axis=1)][null_cols]
        slider_1 = st.slider('Número de linhas ',1,100)
        st.dataframe(df_nulos.head(slider_1))

        st.markdown('**Preencher colunas que têm NULL**')
        cols_select = st.multiselect('Selecione as colunas a serem preenchidas', tuple(['Dropar linhas com NULL'] + list(null_cols)))
        st.markdown(f'Escolheu = {cols_select}')

        
        if cols_select == ['Dropar linhas com NULL']:
            df = df.dropna(axis=0,how='any')
            slider_7 = st.slider('Número de linhas  ',1,100)
            cols_select = None
            st.markdown('**Novo DataFrame**')
            st.markdown(f'**Shape do novo = {df.shape}**')
            st.dataframe(df.head(slider_7))
            # if st.button('Gerar link de download do dataframe'):
            #     tmp_download_link = download_link(df, 'data.csv', 'Download')
            #     st.markdown(tmp_download_link, unsafe_allow_html=True)

    
        
        #if st.button('Continuar'):
        if cols_select: 
            df_nulls = pd.DataFrame({'colunas':cols_select,'tipos':df[cols_select].dtypes})
            cat_cols = list(df_nulls[df_nulls['tipos'] == 'object'].index)

            cols_select = list(set(cols_select) - set(cat_cols)) 
            st.markdown('Preencher os nulos')
            opt = st.radio('Escolha um método de preenchimento(colunas categoricas serão preenchidas com a moda)', ('Dropar linhas com NULL','Zero','Media','Moda','Mediana','Interpolacao Linear'))
            
            
            if opt == 'Zero':
                df[cols_select]=df[cols_select].fillna(0)
                st.markdown('Colunas numéricas escolhidas foram preenchidas com 0')
                st.markdown('Novas colunas')
                df = cat_input(df,cat_cols)
                slider_2 = st.slider('Número de linhas  ',1,100)
                st.dataframe(df.loc[df_nulos.index,list(cols_select) + list(cat_cols)].head(slider_2))
            if opt == 'Media':
                df[cols_select]=df[cols_select].fillna(df[cols_select].mean())
                st.markdown('Colunas escolhidas foram preenchidas com a média de cada coluna')
                st.markdown('Novas colunas')
                df = cat_input(df,cat_cols)
                slider_3 = st.slider('Número de linhas  ',1,100)
                st.dataframe(df.loc[df_nulos.index,list(cols_select) + list(cat_cols)].head(slider_3))
            if opt == 'Moda':
                if len(cols_select) == 1: cols_select = cols_select[0]
                df[cols_select]=df[cols_select].fillna(df[cols_select].mode().values[0])
                st.markdown('Colunas escolhidas foram preenchidas com a moda de cada coluna')
                st.markdown('Novas colunas')
                df = cat_input(df,cat_cols)
                slider_4 = st.slider('Número de linhas  ',1,100)
                st.dataframe(df.loc[df_nulos.index,list([cols_select]) + list(cat_cols)].head(slider_4))
            if opt == 'Mediana':
                df[cols_select]=df[cols_select].fillna(df[cols_select].median())
                st.markdown('Colunas escolhidas foram preenchidas com a mediana de cada coluna')
                st.markdown('Novas colunas')
                df = cat_input(df,cat_cols)
                slider_5 = st.slider('Número de linhas  ',1,100)
                st.dataframe(df.loc[df_nulos.index,list(cols_select) + list(cat_cols)].head(slider_5))
            if opt == 'Interpolacao Linear':
                df[cols_select]=df[cols_select].interpolate(method='linear').astype('int64')
                st.markdown('Colunas escolhidas foram foram interpoladas')
                st.markdown('Novas colunas')
                df = cat_input(df,cat_cols)
                slider_6 = st.slider('Número de linhas  ',1,100)
                st.dataframe(df.loc[df_nulos.index,list(cols_select) + list(cat_cols)].head(slider_6))

        if st.button('Gerar link de download do dataframe'):
            tmp_download_link = download_link(df, 'data.csv', 'Download')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

        st.subheader('Visualização de Dados')
        st.image('media/Data.gif',width=300)

        num_cols_df = pd.DataFrame({'colunas':df.columns,'tipos':df.dtypes})
        num_cols = list(num_cols_df[num_cols_df['tipos'] != object].index)
        cat_cols = list(num_cols_df[num_cols_df['tipos'] == object].index)

        opt = st.radio('Selecione a visualização desejada', ('Histograma','Barras','Boxplot','Scatterplot','Correlação'))
        if opt == 'Histograma':
            col = st.selectbox('Selecione a coluna numérica desejada',tuple(num_cols))
            split = st.selectbox('Selecione o Hue desejado', tuple([None]+list(num_cols_df['colunas'].values)))
            if col:
                if split:
                    st.write(histogram(df,col,split))
                else:
                    st.write(histogram(df,col))
        if opt == 'Barras':
            y_axis = st.selectbox('Selecione a coluna numérica',tuple(num_cols))
            x_axis = st.selectbox('Selecione a coluna categórica',tuple(cat_cols))
            split = st.selectbox('Selecione o Hue desejado', tuple([None]+list(num_cols_df['colunas'].values)))
            #split = st.selectbox('Selecione o Hue desejado', tuple([None]+cat_cols))
            if x_axis and y_axis:
                if split:
                    st.write(bar(df,x_axis,y_axis,split))
                else:  
                    st.write(bar(df,x_axis,y_axis))
        if opt == 'Boxplot':
            y_axis = st.selectbox('Selecione a coluna numérica',tuple(num_cols))
            x_axis = st.selectbox('Selecione a coluna categórica',tuple([None] + list(cat_cols)))
            if y_axis:
                if x_axis:
                    st.write(boxplot(df,y_axis,x_axis))
                else:
                    st.write(boxplot(df,y_axis))
        if opt == 'Scatterplot':
            y_axis = st.selectbox('Selecione a coluna numérica do eixo y',tuple(num_cols))
            x_axis = st.selectbox('Selecione a coluna numérica do eixo x',tuple(num_cols))
            split = st.selectbox('Selecione o Hue desejado', tuple([None] + list(cat_cols)))

            if y_axis and x_axis:
                if split:
                    st.write(scatter(df,x_axis,y_axis,split))
                else:
                    st.write(scatter(df,x_axis,y_axis))

        if opt == 'Correlação':
           st.write(corre(df)) 


if __name__ == "__main__":
    main()