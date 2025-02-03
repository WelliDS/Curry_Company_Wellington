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
import numpy as np
import plotly.graph_objects as go


st.set_page_config(
    page_title='Visão Restaurantes',
    page_icon="🍴", layout='wide'
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


def distancia(df1):
    
    ''' 
    Esta função realiza o cálculo da distância média e retorna no campo
    Crescimento dos Restaurantes '''
            
    df1['distance'] = (df1.loc[:, ['Restaurant_latitude',	'Restaurant_longitude',	
                        'Delivery_location_latitude', 'Delivery_location_longitude']]
                .apply(lambda x: geodesic((x['Restaurant_latitude'],	x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'],	x['Delivery_location_longitude'])).km, axis=1).round(2))
    mean_distance = df1['distance'].mean().round(2)
    return mean_distance

#------Nova Função -------


def avg_std_tempo_entrega(df1, festival, op):
    
    """Esta função calcula o tempo médio e o desvio padrão do tempo de entrega
    
    Parâmetros
    
    Input:
        * df: Dataframe com os dados necessários para o cálculo
        * festival: Avaliação se no periodo há ou não festival na cidade
            'Yes': confirma que há festival no período da entrega
            'No': Confirma que não há festival no período de entrega
            
        *op: Tipo de operação que precisa ser calculado
            'mean': Calcula o tempo médio de entrega
            'std': Calcula o desvio padraão do tempo de entrega
            
    Output:
        * df: Dataframe com 1 coluna e 1 linha representando o valor conforme a seleção efetivada"""
    
    if op =='mean':
        df_aux = df1.loc[df1["Festival"] == festival, ["Time_taken(min)"]].mean()[0].round(1)
    elif op == "std":
        df_aux = df1.loc[df1["Festival"] == festival, "Time_taken(min)"].std().round(1)
    else:
        raise ValueError("Operação inválida. Use 'mean' ou 'std'.")    

    return df_aux


#------Outra Função -------

def media_std_tempo_graph(df1):
    #Gráfico de barra com a distribuição do tempo por cidade (média e desvio padrão)
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']}).round(2)
    df_aux.columns = ['mean', 'std']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Control',
        x=df_aux['City'],
        y=df_aux['mean'],
        error_y=dict(type='data', array=df_aux['std']),
        marker_color=['#FFD700', '#A9A9A9', '#696969']  # Amarelo ouro e tons de cinza
    ))
    fig.update_layout(
        barmode='group',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        title_font=dict(color='white')
    )

    return fig

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
        🍴 Marketplace - Visão Restaurantes</h2>""",
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
        Crescimento dos Restaurantes
    </h2>""", unsafe_allow_html=True)
        
    col1, col2, col3, col4, col5, col6 = st.columns(6, gap='small')
    
    with col1:
        entregadores_unicos = df1.loc[:,'Delivery_person_ID'].nunique()
        col1.metric('Entregadores', entregadores_unicos )
    
    with col2:
        
        mean_distance = distancia(df1)
        col2.metric('Distância Média', mean_distance)
        
    
    with col3:
        
        df_aux = avg_std_tempo_entrega(df1, "Yes", "mean" )
        col3.metric('Entrega Festival', df_aux)
        

        
    with col4:
        df_aux = avg_std_tempo_entrega(df1, "Yes", "std" )
        col4.metric('Std c/ Festival', df_aux)
        
    with col5:
        df_aux = avg_std_tempo_entrega(df1, "No", "mean" )
        col5.metric('Entrega s/ Festival', df_aux)
          
    with col6:  
        df_aux = avg_std_tempo_entrega(df1, "No", "std" )
        col6.metric('Std s/ Festival', df_aux) 
             
    st.markdown( """---""" )    
    
    with st.container():
        st.title('Tempo médio de entrega por cidade')
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.markdown("""                
                        <h5 style='text-align: center; font-family: "Courier New", monospace; color: white;'>
                        Distribuição do tempo por Cidade
                        </h5>""", unsafe_allow_html=True)
            fig = media_std_tempo_graph(df1)
            #Gráfico de barra com a distribuição do tempo por cidade (média e desvio padrão)
            st.plotly_chart(fig, use_container_width=True)
            
            
            
            
        with col2:
            st.markdown("""                
                    <h5 style='text-align: center; font-family: "Courier New", monospace; color: white;'>
                    Tempo Médio por tipo de Entrega
                    </h5>""", unsafe_allow_html=True)
            df_aux = df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']}).round(2)
            df_aux.columns = ['tempo_medio', 'std']
            df_aux = df_aux.reset_index()
            
            st.dataframe(df_aux, use_container_width=True, hide_index=True)
            
        
        st.markdown( """---""" )
        
    with st.container():
        st.title('Distribuição do Tempo')
             
                
        col1, col2= st.columns(2, gap='large')
        with col1:
                     
            st.markdown("""                
                    <h5 style='text-align: center; font-family: "Courier New", monospace; color: white;'>
                    Distância Média dos restaurantes e Locais de Entrega
                    </h5>""", unsafe_allow_html=True)
            df1['distance'] = (df1.loc[:, ['Restaurant_latitude',	'Restaurant_longitude',	
                                    'Delivery_location_latitude', 'Delivery_location_longitude']]
                            .apply(lambda x: geodesic((x['Restaurant_latitude'],	x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'],	x['Delivery_location_longitude'])).km, axis=1).round(2))
            mean_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

            #gráfico
            fig = go.Figure(data=[go.Pie(labels=mean_distance['City'], values=mean_distance['distance'], pull=[0, 0.1, 0], 
            marker=dict(colors=['#025E73', '#038C8C', '#70BFBF']))])
            st.plotly_chart(fig, use_container_width = True) 



            
        with col2:
            
                       
            st.markdown("""                
                    <h5 style='text-align: center; font-family: "Courier New", monospace; color: white;'>
                    Tempo médio e o DP de entrega por Cidade e Tipo de Tráfego
                    </h5>""", unsafe_allow_html=True)
            # Gráfico sunburst

            df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']}).round(2)


            df_aux.columns = ['tempo_medio', 'std']


            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='tempo_medio',
                            color='std', color_continuous_scale= 'turbid',
                            color_continuous_midpoint=np.average(df_aux['std']))

            st.plotly_chart(fig, use_container_width = True)


    ### 'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
    ###        'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
    ###        'ylorrd','RdBu' ] ###
            
            
    st.markdown( """---""" ) 
        
    
                