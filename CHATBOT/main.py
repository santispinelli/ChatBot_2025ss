#Con este import llamamos a librerias. Las podemos descargar aparte pero algunas ya vienen directamente cunado instalamos python. En este caso hay q instalarla aparte. Esto en una API
import streamlit as st
import groq 

#CONSTANTES
MODELOS = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]

#VARIABLES
altura_contenedor_chat = 600

stream_status = True

#FUNCIONES

#Esta funcion utiliza streamlit para crear la interfaz de la pagina y ademas retorna el modelo elegido por el usuario
def configurar_pagina():

    st.set_page_config(page_title="SantinoSpinelli", page_icon= "👨‍💻")

    st.title("Chati")

    st.sidebar.title("Seleccion de modelos")

    elegirModelo = st.sidebar.selectbox("Elegí un modelo", options=MODELOS, index=0)

    return elegirModelo




def crear_usuario(): # Esta funcion llama a st.secrets para obtener la clave api de groq y crea un usuario
    clave_secreta = st.secrets["CLAVE_API"]
    return groq.Groq(api_key = clave_secreta)


#Esta funcion configura el modelo de lenguaje ara que procese el prompt del usuario
def configurar_modelo(cliente, modelo_elejido, prompt_usuario):
    return cliente.chat.completions.create(
        model = modelo_elejido,
        messages = [{"role" : "user", "content" : prompt_usuario}],
        stream = stream_status,
    )


#Creamos una sesion llamada mensajes que va a guardar lo que le escribimos al ChatBot
def inicializar_estado():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [] 


def actualizar_historial(rol, contenido, avatar):
    st.session_state.mensajes.append({"role" : rol, "content" : contenido, "avatar" : avatar})

def mostrar_historial ():
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar=mensaje["avatar"]):
            st.write(mensaje["content"])

#Aca definimos el contenedor en el que van a aparecer las preguntas y el historial
def area_chat():
    contenedor = st.container(height=altura_contenedor_chat, border=True)
    with contenedor:
        mostrar_historial()


def generar_respuesta(respuesta_completa_del_bot):
    respuesta_posta = ""
    for frase in respuesta_completa_del_bot:
        if frase.choices[0].delta.content:
            respuesta_posta += frase.choices[0].delta.content
            yield frase.choices[0].delta.content
    return respuesta_posta


#--------------------------IMPLEMENTACION----------------------------------------

def main():

    modelo_elegido_por_usuario = configurar_pagina()

    cliente_usuario = crear_usuario()

    inicializar_estado ()

    area_chat ()

    prompt_del_usuario = st.chat_input("¿En que puedo ayudarte?")

    if prompt_del_usuario:
        actualizar_historial("user", prompt_del_usuario, "🙋‍♂️")
        respuesta_del_bot = configurar_modelo(cliente_usuario, modelo_elegido_por_usuario, prompt_del_usuario)

        if respuesta_del_bot:
            with st.chat_message("assistant"):
                respuesta_posta = st.write_stream (generar_respuesta(respuesta_del_bot))
                actualizar_historial("assistant", respuesta_posta, "🤖")

            st.rerun()

if __name__ == "__main__":
    main()