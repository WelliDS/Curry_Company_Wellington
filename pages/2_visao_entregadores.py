#Import Libraries

import pandas as pd
import plotly_express as px
import folium

from streamlit_folium import folium_static
from streamlit_folium import st_folium
from geopy.distance import geodesic
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
import base64


st.set_page_config(
    page_title='Visão Entregadores',
    page_icon="🏍️", layout='wide'
)

# ============================================
# Funções]
# ============================================



def limpeza_dados(df1):
    
    ''' 
    Esta função realiza a limpeza do dataframe
    Tipos de Limpeza:
    1. Excluir de linhas Vazias
    2.Alteração do time de coluna de dados
    3.Remoção dos espaços das variáveis de texto
    4.Criação das features (colunas) Year_month e week
    5.Limpeza da coluna de Tempo (remoção do texto da variável numérica)
    
    Input: Dataframe
    Output: Dataframe
    '''
    
    # Excluir as linhas com a idade dos entregadores vazia
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']
    df1 = df1[df1['City'] != 'NaN ']
    df1 = df1[df1['Road_traffic_density'] != 'NaN ']


    # Excluir as linhas NaN das condições climáticas (são 91 que corresponde a 0.0020805231029515994% do dataframe )
    df1 = df1[df1['Weatherconditions'] != 'conditions NaN']


    #Alterando os tipos das colunas
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y')


    #Criando uma nova coluna (Year_Month)

    df1['Year_Month'] = df1['Order_Date'].dt.strftime('%Y-%m')


    #Criando uma nova coluna (Week)
    df1['Week_Year'] = df1['Order_Date'].dt.strftime('%U')


    #retirando espaços:

    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()

    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()

    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()

    df1['Type_of_order'] = df1['Type_of_order'].str.strip()

    df1['Festival'] = df1['Festival'].str.strip()

    df1['City'] = df1['City'].str.strip()

    df1['ID'] = df1['ID'].str.strip()



    # Retirada do Nan

    df1 = df1[df1['Festival'] != 'NaN']


    #df1 = df1[df1['Delivery_person_ID'] != 'NaN ']


    # retirar o texto min() da coluna Time_taken(min)
    
    df1['Time_taken(min)']= df1['Time_taken(min)'].str.replace(r'\(min\)\s*', '', regex=True).str.strip()

    df1['Time_taken(min)'] = pd.to_numeric(df1['Time_taken(min)'])

    return df1

#---------Nova Função ------------

def top_entregadores(df1,top_asc):
    
    ''' Esta função realiza a consulta gerando duas tabelas 
    com os top 10 entregadores  (mais lentos e mais rápidos))
    
    input: dataframe
    output: Tabelas'''
    
    
    result = (df1.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
    .groupby(['City', 'Delivery_person_ID']).min().sort_values(['City','Time_taken(min)'], ascending=top_asc).reset_index())

    if top_asc:
# Obter os 10 menores tempos de entrega para cada cidade
        top_10_per_city = result.groupby('City').apply(lambda x: x.nsmallest(10, 'Time_taken(min)')).reset_index(drop=True)
    
    else:
# Obter os 10 maiores tempos de entrega para cada cidade
        top_10_per_city = result.groupby('City').apply(lambda x: x.nlargest(10, 'Time_taken(min)')).reset_index(drop=True)
    return   top_10_per_city 

# --------------------------- Inicio da Estrutura Lógica do Código -----------------------------------------
#import dataset
df = pd.read_csv('train.csv')

# ============================================
# Realizando uma cópia do Dataframe
# ============================================

df1 = df.copy()


# ============================================
# Fazendo limpeza dos dados:
# ============================================

df1 = limpeza_dados (df)



# ==================================================
# Barra Lateral
# ==================================================

st.markdown("""
    <h2 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        🏍️ Marketplace - Visão Entregadores</h2>""",
    unsafe_allow_html=True)


image_path=('curry.png')
image = Image.open( image_path )


# Converter a imagem em base64
with open(image_path, "rb") as img_file:
    encoded_image = base64.b64encode(img_file.read()).decode()

# Centralizar a imagem com HTML
st.sidebar.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{encoded_image}" width="80"/>
    </div>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown("""<div style="text-align: center;">
                        <h1>Cury Company</h1> 
                        <h3>The Fastest delivery in Town</h3>
                        </div> 
                    """, unsafe_allow_html=True)

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider('Informe a data',
                  value= datetime(2022, 3, 11),
                  min_value= datetime(2022, 2, 11),
                  max_value=datetime(2022, 4, 6),
                  format='DD-MM-YYYY')



st.sidebar.markdown( """---""" )


st.sidebar.markdown('### Selecione a condição de trânsito')
traffic_options = st.sidebar.multiselect ('Quais as condições de trânsito',
                                          ['Low', 'Medium', 'High', 'Jam'],
                                          default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """---""" )


st.sidebar.markdown('### Selecione a condição climática')
weather_options = st.sidebar.multiselect ('Quais as condições de trânsito',
                                          ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy',
                                           'conditions Sunny', 'conditions Windy'],
                                          default= ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy',
                                           'conditions Sunny', 'conditions Windy'])


                  

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '#### Powered by Wellington Silva' ) 


#filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider 
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#filtro de condição climática
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]


# ==================================================
# Layout do streamlit
# ==================================================

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', '-', '-']) 

with tab1:
    with st.container():
        st.markdown("""                
                    <h2 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Métricas Gerais
    </h2>""", unsafe_allow_html=True)
        
        
        
        col1, col2, col3, col4 = st.columns(4, gap='small')
        
        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade, delta_color='normal')
            
        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
            
        with col3:
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric('Melhor Condição Veículos', melhor_condicao, delta=2)
            
        with col4:
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior Condição Veículos', pior_condicao,  delta=-2)
            
    with st.container():
        
        st.markdown("""---""")
        st.markdown("""                
                    <h2 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Avaliações
    </h2>""", unsafe_allow_html=True)
        
        
        col1, col2 = st.columns(2, gap='medium')
        
        with col1:
            st.markdown("""                
                    <h6 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Avaliações Médias por entregador
    </h6>""", unsafe_allow_html=True)
            
            df = df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']].groupby(['Delivery_person_ID']).mean().round(2).reset_index()
            st.dataframe (df, use_container_width=True, hide_index=True)
            
        with col2:
            st.markdown( """                
                    <h6 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Avaliação Média por Trânsito
    </h6>""", unsafe_allow_html=True)
            
            df_avg_rating_by_traffic = (df1.loc[:,['Road_traffic_density', 'Delivery_person_Ratings']]
                               .groupby(['Road_traffic_density'])
                               .agg({'Delivery_person_Ratings' :['mean', 'std']}).round(2))
                            
            df_avg_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df = df_avg_rating_by_traffic.reset_index()
            
            st.dataframe (df, use_container_width=True, hide_index=True)
            
            st.markdown("""                
                    <h6 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Avaliação Média por Clima
    </h6>""", unsafe_allow_html=True)
            
            df_avg_rating_by_weather = (df1.loc[:,['Weatherconditions', 'Delivery_person_Ratings']]
                               .groupby(['Weatherconditions'])
                               .agg({'Delivery_person_Ratings' :['mean', 'std']}).round(2))             
            df_avg_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg_rating_by_weather.reset_index()
            
            st.dataframe (df_avg_rating_by_weather, use_container_width=True)
            
with st.container():
    st.markdown("""---""")
    st.markdown("""                
                    <h2 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Velocidade de Entrega
    </h2>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap='medium')
    
    with col1:
        st.markdown ("""                
                    <h5 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Top Entregadores Mais Rápidos
    </h5>""", unsafe_allow_html=True)
        top_10_per_city = top_entregadores(df1, top_asc=True)
        st.dataframe (top_10_per_city, use_container_width=True, hide_index=True)
                         
            
            
            
    with col2:
        st.markdown ("""                
                    <h5 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Top Entregadores Mais Lentos
    </h5>""", unsafe_allow_html=True)
        top_10_per_city = top_entregadores(df1, top_asc=False)
        st.dataframe (top_10_per_city, use_container_width=True, hide_index=True)
        
        
        
    