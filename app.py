import os
import streamlit as st
import pandas as pd

from newsmonitor.blog import fetch_blog_posts, BlogPost
from newsmonitor.search import search_for_reposts
from newsmonitor.utils import estimate_reading_time


def main():
    st.set_page_config(page_title="Moja pretraživalica", layout="wide")

    st.title("Moja pretraživalica")
    st.write(
        "Alat za praćenje gdje se na webu pojavljuju tvoji članci. "
        "Rezultate možeš pregledati i izvesti u CSV."
    )

    with st.sidebar:
        st.header("Postavke")

        default_blog_url = "https://leonardasrdelic.github.io/hr/blog/"
        blog_index_url = st.text_input(
            "URL indeks stranice s blog objavama",
            value=default_blog_url,
        )

        manual_query = st.text_area(
            "Ručni upit (opcionalno)",
            value="",
            help="Upiši ključne riječi ili frazu za ručnu pretragu (npr. \"Leonarda Srdelić Institut za javne financije\"). "
                 "Ako ovo polje nije prazno, preskače se dohvat bloga.",
        )

        # Pokušaj prvo iz Streamlit secreta (cloud), pa iz env var
        api_key_env = st.secrets.get("SERPER_API_KEY", os.environ.get("SERPER_API_KEY", ""))
        api_key = st.text_input(
            "Serper API ključ (Google Search)",
            value=api_key_env,
            type="password",
            help="Ključ možeš upisati ovdje ili postaviti kao varijablu okruženja SERPER_API_KEY.",
        )

        similarity_threshold = st.slider(
            "Prag sličnosti",
            min_value=0.3,
            max_value=0.9,
            value=0.5,
            step=0.05,
            help="Što je prag viši, to su pronalasci sličniji izvornom članku.",
        )

        max_results_per_query = st.number_input(
            "Maksimalan broj rezultata po upitu",
            min_value=5,
            max_value=50,
            value=15,
            step=1,
        )

        run_button = st.button("Pokreni praćenje", type="primary")

    if not run_button:
        st.info("Postavi parametre sa strane i pritisni 'Pokreni praćenje'.")
        return

    if not api_key:
        st.error("Molim upiši Serper API ključ.")
        return

    # Ako korisnik unese ručni upit, preskačemo dohvat bloga
    if manual_query.strip():
        blog_posts = [BlogPost(title=manual_query.strip(), url=manual_query.strip(), text=manual_query.strip())]
        st.success("Koristim ručni upit za pretraživanje.")
        with st.expander("Pregled zadatih upita"):
            st.markdown(f"* {manual_query.strip()}")
    else:
        with st.spinner("Dohvaćam objave s bloga..."):
            blog_posts = fetch_blog_posts(blog_index_url)

        if not blog_posts:
            st.error("Nisam našla nijednu objavu. Provjeri URL ili strukturu bloga.")
            return

        st.success(f"Pronašla sam {len(blog_posts)} objava na blogu.")
        with st.expander("Pregled pronađenih objava"):
            for post in blog_posts:
                st.markdown(f"* [{post.title}]({post.url})  ({estimate_reading_time(post.text)} min čitanja)")

    with st.spinner("Pretražujem web i tražim moguće prenesene članke..."):
        findings = search_for_reposts(
            blog_posts=blog_posts,
            api_key=api_key,
            similarity_threshold=similarity_threshold,
            max_results_per_query=max_results_per_query,
            max_queries_per_post=30,
        )

    if not findings:
        st.warning("Trenutno nisam našla članke koji dovoljno sliče tvojima prema zadanim kriterijima.")
        return

    df = pd.DataFrame(findings)
    df_sorted = df.sort_values(by="similarity", ascending=False)

    st.subheader("Pronađene moguće objave koje prenose tvoj sadržaj")
    st.dataframe(
        df_sorted,
        use_container_width=True,
        hide_index=True,
    )

    csv = df_sorted.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "Preuzmi rezultate kao CSV",
        data=csv,
        file_name="moja_pretrazivalica_rezultati.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
