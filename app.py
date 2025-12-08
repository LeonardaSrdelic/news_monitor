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

        source_doc_url = st.text_input(
            "URL izvornog rada (opcionalno, HTML ili PDF)",
            value="",
            help="Ako dodaš URL izvornog dokumenta (npr. PDF u repozitoriju), koristit će se kao polazni tekst umjesto blog indeksa.",
        )

        source_doc_title = st.text_input(
            "Naslov izvornog rada (opcionalno)",
            value="",
            help="Ako ostaviš prazno, kao naslov će se koristiti URL.",
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
            min_value=0.01,
            max_value=0.9,
            value=0.2,
            step=0.05,
            help="Što je prag viši, to su pronalasci sličniji izvornom članku. Niži prag hvata više rezultata.",
        )

        max_results_per_query = st.number_input(
            "Maksimalan broj rezultata po upitu",
            min_value=5,
            max_value=20,
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
    elif source_doc_url.strip():
        from newsmonitor.blog import extract_article_text

        with st.spinner("Dohvaćam izvorni dokument..."):
            doc_text = extract_article_text(source_doc_url.strip())

        if not doc_text or len(doc_text.split()) < 50:
            st.error("Nisam uspjela pročitati dovoljno teksta iz danog URL-a. Provjeri je li javno dostupan HTML/PDF.")
            return

        title_override = source_doc_title.strip() or source_doc_url.strip()
        blog_posts = [BlogPost(title=title_override, url=source_doc_url.strip(), text=doc_text)]
        st.success("Koristim uneseni URL izvornog rada kao polazni tekst.")
        with st.expander("Pregled izvornog teksta"):
            st.markdown(f"* [{blog_posts[0].title}]({blog_posts[0].url})  ({estimate_reading_time(blog_posts[0].text)} min čitanja)")
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
