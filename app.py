import streamlit as st
from dotenv import dotenv_values
from openai import OpenAI
from PIL import Image
import base64
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

st.set_page_config(page_title="Opis Obrazów", layout="centered")
env = dotenv_values(".env")

EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072
QDRANT_COLLECTION_NAME = "image_descriptions"

def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])

@st.cache_resource
def get_qdrant_client():
    # Sprawdź, czy dane konfiguracyjne są w sesji
    # Teraz korzystaj z danych w sesji
    return QdrantClient(
        url=st.session_state["QDRANT_URL"],
        api_key=st.session_state["QDRANT_API_KEY"],
    )

def get_embedding(text):
    openai_client = get_openai_client()
    result = openai_client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL,
    )
    return result.data[0].embedding

# Funkcja do dodawania opisu do bazy
def add_description_to_db(description_text):
    qdrant_client = get_qdrant_client()
    points_count = qdrant_client.count(
        collection_name=QDRANT_COLLECTION_NAME,
        exact=True,
    )
    qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            PointStruct(
                id=points_count.count + 1,
                vector=get_embedding(text=description_text),
                payload={"text": description_text},
            )
        ]
    )

def assure_db_collection_exists():
    qdrant_client = get_qdrant_client()
    if not qdrant_client.collection_exists(QDRANT_COLLECTION_NAME):
        print("Tworzę kolekcję")
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
    else:
        print("Kolekcja już istnieje")

mode = st.radio(
     "Wybierz tryb Opisu:",
     ("Wybór opcji opisu obrazka przez OpenAI", "Wybór opcji opisu obrazka samodzielnie z klawiatury")
)

if mode == "Wybór opcji opisu obrazka przez OpenAI":

    def generate_description(image_bytes):
        openai_client = get_openai_client()
    # Kodujemy obraz do base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Opisz ten obraz."},
                {"role": "user", "content": f"Proszę opisać obraz o kodzie base64: {image_base64}"}
            
            ],
        # lub odpowiednia struktura, zależnie od API
        )
    # Odczytanie opisu z odpowiedzi
        description = response.choices[0].message.content
        return description
    

elif mode == "Wybór opcji opisu obrazka samodzielnie z klawiatury":

   def generate_description(image_bytes):
        return "Opis obrazu - Włąsny z klawiatury"

# Inicjalizacja kluczy w session_state
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = env.get("OPENAI_API_KEY", "")
    
if "QDRANT_URL" not in st.session_state:
    st.session_state["QDRANT_URL"] = env.get("QDRANT_URL", "")

if "QDRANT_API_KEY" not in st.session_state:
    st.session_state["QDRANT_API_KEY"] = env.get("QDRANT_API_KEY", "")


def add_description_to_db(description_text):
    qdrant_client = get_qdrant_client()
    points_count = qdrant_client.count(
        collection_name=QDRANT_COLLECTION_NAME,
        exact=True,
    )
    qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            PointStruct(
                id=points_count.count + 1,
                vector=get_embedding(text=description_text),
                payload={
                    "text": description_text,
                },
            )
        ]
    )

if not st.session_state.get("openai_api_key"):
    if "OPENAI_API_KEY" in env:
        st.session_state["openai_api_key"] = env["OPENAI_API_KEY"]
    else:
        st.info("Dodaj swój klucz API OpenAI aby móc korzystać z tej aplikacji")
        st.session_state["openai_api_key"] = st.text_input("Klucz API", type="password")
        if st.session_state["openai_api_key"]:
            st.rerun()

if not st.session_state.get("openai_api_key"):
    st.stop()

if not st.session_state.get("qdrant_url"):
    if "OPENAI_API_KEY" in env:
        st.session_state["qdrant_url"] = env["QDRANT_URL"]
    else:
        st.info("Dodaj swój adres QDRANT_URL aby móc korzystać z tej aplikacji")
        st.session_state["qdrant_url"] = st.text_input("Adres URL", type="default")
        if st.session_state["qdrant_url"]:
            st.rerun()

if not st.session_state.get("qdrant_url"):
    st.stop()

if not st.session_state.get("qdrant_api_key"):
    if "OPENAI_API_KEY" in env:
        st.session_state["qdrant_api_key"] = env["QDRANT_URL"]
    else:
        st.info("Dodaj swój klucz API QDRANT aby móc korzystać z tej aplikacji")
        st.session_state["qdrant_api_key"] = st.text_input("Klucz API", type="password")
        if st.session_state["qdrant_api_key"]:
            st.rerun()

if not st.session_state.get("qdrant_api_key"):
    st.stop()

def add_description_to_db(description_text):
    qdrant_client = get_qdrant_client()
    points_count = qdrant_client.count(
        collection_name=QDRANT_COLLECTION_NAME,
        exact=True,
    )
    qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            PointStruct(
                id=points_count.count + 1,
                vector=get_embedding(text=description_text),
                payload={"text": description_text},
            )
        ]
    )

# Session state initialization
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = None

if "description_text" not in st.session_state:
    st.session_state["description_text"] = ""

st.title("Opis Obrazów")
assure_db_collection_exists()

uploaded_file = st.file_uploader("Wybierz obraz", type=["PNG", "JPG", "JPEG"])

if uploaded_file is not None:
    st.session_state["image_bytes"] = uploaded_file.read()

    image_bytes = Image.open(uploaded_file)

    st.image(image_bytes, caption='Załadowany obraz', use_container_width=True)

    if st.button("Generuj opis"):
        st.session_state["description_text"] = generate_description(st.session_state["image_bytes"])
    
    if st.session_state["description_text"]:
        st.session_state["description_text"] = st.text_area("Edytuj opis", value=st.session_state["description_text"])

    if st.session_state["description_text"] and st.button("Zapisz opis", disabled=not st.session_state["description_text"]):
        add_description_to_db(description_text=st.session_state["description_text"])
        st.toast("Opis zapisany", icon="🎉")
    