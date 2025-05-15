import os
import pandas as pd
import streamlit as st
from PIL import Image

# Путь к папке с изображениями
IMAGES_DIR = "images"
DESCRIPTION_FILE = "description.pq"
COLUMNS = 5
IMAGE_HEIGHT = 250


# Загрузка данных
@st.cache_data
def load_data():
    return pd.read_parquet(DESCRIPTION_FILE)


# Пример данных: словарь, где ключ - название кластера, значение - список nmid
clusters = {
    "Cluster 1": f"{IMAGES_DIR}/cluster1",
    "Cluster 2": f"{IMAGES_DIR}/cluster2",
}


def main():
    st.set_page_config(layout="wide")
    st.title("Просмотр изображений по кластерам")

    df = load_data()

    # Выбор кластера
    selected_cluster = st.selectbox("Выберите кластер", list(clusters.keys()))

    # Получаем список nmid для выбранного кластера
    nmids_imgs = os.listdir(clusters[selected_cluster])
    nmids = [int(nmid.split(".")[0]) for nmid in nmids_imgs]

    st.header(f"Изображения для кластера '{selected_cluster}'")

    cluster_df = df[df.index.isin(nmids)]

    # Рассчитываем количество строк
    rows = [nmids_imgs[i:i + COLUMNS] for i in range(0, len(nmids_imgs), COLUMNS)]

    for row in rows:
        # Создаем контейнеры для колонок
        cols = st.columns(COLUMNS)

        for idx, nmid_img in enumerate(row):
            nmid = int(nmid_img.split(".")[0])

            with cols[idx]:
                # Получаем информацию о товаре
                if nmid in cluster_df.index:
                    item_info = cluster_df.loc[nmid]
                    title = item_info.get('title', 'Нет названия')
                    subject = item_info.get('subject', 'Нет категории')
                else:
                    title = "Нет данных"
                    subject = "Нет данных"

                # Поиск изображения
                image_path = os.path.join(clusters[selected_cluster], f"{nmid_img}")

                # Контейнер для карточки товара
                with st.container():
                    if image_path:
                        try:
                            image = Image.open(image_path)
                            # Масштабируем изображение к фиксированной высоте
                            width, height = image.size
                            new_width = int(width * (IMAGE_HEIGHT / height))
                            resized_image = image.resize((new_width, IMAGE_HEIGHT))
                            st.image(resized_image)

                            st.markdown(f"""
                            <div style='margin-top: 10px; line-height: 1.4;'>
                                <strong>{title}</strong><br>
                                <small>Категория: {subject}</small><br>
                                <small>ID: {nmid}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error("Ошибка загрузки")
                            st.image(Image.new('RGB', (150, IMAGE_HEIGHT), color='gray'))

                    else:
                        st.image(Image.new('RGB', (150, IMAGE_HEIGHT), color='gray'))

                        # Текстовая информация с фиксированным форматированием
                        st.markdown(f"""
                        <div style='margin-top: 10px; line-height: 1.4;'>
                            <strong>{title}</strong><br>
                            <small>Категория: {subject}</small><br>
                            <small>ID: {nmid_img}</small>
                        </div>
                        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
