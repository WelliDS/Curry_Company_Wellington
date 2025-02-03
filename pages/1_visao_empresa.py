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
    page_title='Visão Empresa',
    page_icon="🏬", layout='wide'
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

def order_metric(df1):    
    df_aux = (df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date'])
                .count().rename(columns={'ID' : 'Qtde_Entregas'}).reset_index())
    # gráfico
    fig = px.bar( df_aux, x='Order_Date', y='Qtde_Entregas',  title='PEDIDOS POR DIA  📊', text_auto=True)
    fig.update_traces(textfont_size=60, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(title={'text' : 'PEDIDOS POR DIA  📊',
                            'x': 0.5, #centraliza o título 
                            'xanchor': 'center',
                            'yanchor': 'top'},
                    title_font=dict( family="Courier New, monospace", size=20))
        
    return fig

#--------- Nova Função -----------

def pedidos_por_trafego(df1):
    '''
    Esta função tem como objetivo auxiliar na plotagem do gráfico de pizza com a distribuição dos pedidos
    por tipo de tráfego
    
    Input: dataframe
    Output: Gráfico de pizza
    '''           
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    df_aux['percentual'] = (df_aux['ID']/ df_aux['ID'].sum()) * 100

    #Gráfico Pizza - Distribuição dos pedidos por tipo de tráfego.

    fig = px.pie(df_aux, values='percentual', names='Road_traffic_density', hole=.4)
    
    return fig


#------Nova Função

def pedido_por_cidade(df1):
    
    '''
    Esta função tem como objetivo auxiliar na plotagem do scatterplot (gráfico bolhas)
    com a distribuição dos pedidos por Cidade e tipo de tráfego

    Input: dataframe
    Output: Gráfico de bola
    '''            
    
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density', 'City']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City') 
    return fig  


#-------Nova Função ----------

def pedido_semana(df1):
    
    '''
    Esta função tem como objetivo auxiliar na plotagem do gráfico de linha
    com a quantidades de pedidos realizados por semana

    Input: dataframe
    Output: Gráfico de linha
    '''
    df_aux = (df1.loc[:, ['ID', 'Week_Year']].groupby(['Week_Year'])
                .count().rename(columns={'ID' : 'Qtde_Entregas'}).reset_index())


    # gráfico de linha
    fig = px.line( df_aux, x='Week_Year', y='Qtde_Entregas', markers=True )
    
    # Suaviza a linha
    fig.update_traces(line_shape='spline')
    
    # Adiciona os valores na parte superior da linha
    fig.update_traces(
        mode='lines+markers+text',  # Certifica que o texto será mostrado junto com a linha e os marcadores
        text=df_aux['Qtde_Entregas'],  # Valores a serem mostrados
        textposition='top center',  # Posiciona o texto acima dos pontos
        textfont=dict(size=14, color='white')  # Ajusta o tamanho e cor da fonte do texto
    )

    
    return fig

#-------Nova Função ----------

def pedido_por_semana_entregador(df1):
    
    '''
    Esta função tem como objetivo auxiliar na plotagem do gráfico de linha
    com a quantidades de pedidos realizados por entregador por semana

    Input: dataframe
    Output: Gráfico de linha (volume entregas entregadores por semana)
    '''
        
    df_aux_semana = df1.loc[:, ['ID', 'Week_Year']].groupby('Week_Year').count().reset_index()

    df_aux_entregador = df1.loc[:, ['Delivery_person_ID', 'Week_Year']].groupby('Week_Year').nunique().reset_index()

    df_aux = pd.merge(df_aux_semana, df_aux_entregador, how='inner')

    df_aux['order_by_deliver'] = (df_aux['ID'] / df_aux['Delivery_person_ID']).round(2)
  


    fig = px.line(
        df_aux,
        x='Week_Year',
        y='order_by_deliver',
        title='Pedidos por Entregador por Semana',
        labels={'Week_Year': 'Semana do Ano', 'order_by_deliver': 'Pedidos por Entregador'}, markers=True
       )
    
    # Suaviza a linha
    fig.update_traces(line_shape='spline')

    # Adiciona os valores na parte superior da linha
    fig.update_traces(
        mode='lines+markers+text',  # Certifica que o texto será mostrado junto com a linha e os marcadores
        text=df_aux['order_by_deliver'],  # Valores a serem mostrados
        textposition='top center',  # Posiciona o texto acima dos pontos
        textfont=dict(size=14, color='white')  # Ajusta o tamanho e cor da fonte do texto
    )
   
    return fig

#------Ultima função -------------

def mapa_paises(df1):
    
    
    '''
    Esta função tem como objetivo auxiliar na plotagem do mapa com as informações do local e dados sobre 
    o restaurante pesquisado

    Input: dataframe
    Output: Mapa com localização e dados dos restaurantes
    '''
    df_aux = (df1.loc[:, ['City','Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density'])
            .median().reset_index())


# Desenhar o mapa com localização dos restaurantes
    map2 = folium.Map(zoom_start=15, width=800, height=750)
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
                    icon=folium.Icon(color='darkblue', icon='utensils', prefix='fa'), 
                    #icon=folium.CustomIcon(icon_image='C:/Users/well_/Downloads/amazon-brands-solid.svg', icon_size=(30, 30)),
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to( map2)
    st_folium(map2, width=800, height=750)

    return None
   




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
# Barra lateral
# ==================================================

st.markdown("""
    <h2 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        🛒 Marketplace - Visão Cliente
    </h2>
    """,
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
st.sidebar.markdown( '#### Powered by Wellington Silva' ) 


#filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider 
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]



# ==================================================
# Layout do streamlit
# ==================================================

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])  

with tab1:
    with st.container():
        
        # Order Metric
        #Order_Metric - Gráfico de Barras (Pedidos por dia)
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width = True)
        
            
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            
            #Gráfico de pizza - Distribuição Pedidos por Tipo de Tráfego
            fig = pedidos_por_trafego(df1)
            st.markdown("""
        <h5 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
            Distribuição Pedidos por Tipo de Tráfego
        </h5>""", unsafe_allow_html=True)   
            st.plotly_chart(fig, use_container_width=True)  
            
            
                                           
            
        with col2:
            
            #Gráfico de bolhas - volume de pedidos por cidade e tipo de tráfego.
            fig = pedido_por_cidade(df1)
            st.markdown("""
    <h5 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
    Volume de pedidos por Cidade e Tipo de Tráfego
    </h5>""", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
                       
    
with tab2:
    with st.container(): 
        
        #Gráfico de linha com a qtde de pedidos por semana
        
        fig = pedido_semana(df1)
        st.markdown("""
        <h3 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Quantidade Pedidos por Semana 📉
        </h3>""", unsafe_allow_html=True)
        st.plotly_chart(fig,use_container_width=True) 

            
        
    with st.container():
        
        #Gráfico de linha com a qtde de pedidos por entregador por semana
        
        fig = pedido_por_semana_entregador(df1)
        st.markdown("""
        <h3 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Quantidade Pedidos por Entregador por Semana 📉
        </h3>""", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        
         
with tab3:
    
    # Desenha um mapa com os restaurantes, informando seu local e algumas informações
    
    
    st.markdown("""
    <h2 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
        Country Maps
    </h2>""", unsafe_allow_html=True)
    mapa_paises(df1)
    
    
    