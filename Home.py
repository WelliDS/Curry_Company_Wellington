import streamlit as st
from PIL import Image
import base64

st.set_page_config(
    page_title='Home',
    page_icon="🏠"
)

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



st.markdown("""
<h2 style='text-align: left; font-family: "Courier New", monospace; color: white;'>
Curry Company Growth Dashboard
</h2>""", unsafe_allow_html=True)

st.markdown("""<div style="text-align: left; font-size: 18px;">
                        <p>Growth Dashboard foi construído para acompanhar as métricas de crescimento dos 
                        Entregadores e Restaurantes</p> 
                        <h3>Como utilizar esse Growth Dashboard?</h3>
                        <ul style="padding-left: 20px;">
        ✔️ Visão Empresa:
            <ul style="padding-left: 25px;">
                <li style="padding-left: 20px;">Visão Gerencial: Métricas gerais de comportamento.</li>
                <li style="padding-left: 20px;">Visão Tática: Indicadores semanais de crescimento.</li>
                <li style="padding-left: 20px;">Visão Geográfica: Insights de geolocalização.</li><br>
            </ul>
        </li>
        ✔️ Visão Entregador:
            <ul style="padding-left: 25px;">
                <li style="padding-left: 20px;">Acompanhamento dos indicadores semanais de crescimento.</li><br>
            </ul>
        </li>
        ✔️ Visão Restaurante:
            <ul style="padding-left: 25px;">
                <li style="padding-left: 20;">Indicadores semanais de crescimentos dos restaurantes</li><br>
            </ul>
        </li>
    </ul>
    <br><br>
                        <h6>Precisa de Ajuda?</h6>
                        <p>Time de Data Science no Discord<br>
                            - @wellingtons</p>
                        </div>                        
                    """, unsafe_allow_html=True)