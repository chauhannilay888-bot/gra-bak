import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Qlevo Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Custom CSS
st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #f8fafc; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -1px; }
    .card {
        background: rgba(30, 41, 59, 0.85);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(99, 102, 241, 0.25);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card:hover {
        transform: translateY(-12px);
        box-shadow: 0 25px 50px -12px rgb(99 102 241 / 0.35);
        border-color: #6366f1;
    }
    .product-img {
        border-radius: 16px;
        transition: transform 0.7s ease;
        background: #1e2937;
    }
    .card:hover .product-img {
        transform: scale(1.06);
    }
    .btn-primary {
        background: linear-gradient(90deg, #6366f1, #818cf8);
        color: white;
        border: none;
        border-radius: 9999px;
        padding: 12px 32px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 3rem 0 2rem;">
    <h1 style="font-size: 3.8rem; background: linear-gradient(90deg, #6366f1, #c4d0ff); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Qlevo Store
    </h1>
    <p style="font-size: 1.35rem; color: #94a3b8; margin-top: -12px;">Premium Digital Collection</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Hero
st.markdown("""
<div style="background: linear-gradient(135deg, #1e2937 0%, #0f172a 100%); 
            padding: 90px 40px; border-radius: 28px; text-align: center; margin-bottom: 60px;">
    <h2 style="font-size: 3rem; line-height: 1.1;">Digital Excellence,<br>Delivered</h2>
    <p style="font-size: 1.35rem; color: #cbd5e1; max-width: 720px; margin: 24px auto;">
        Premium tools, masterful storytelling, and battle-tested coding resources.
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("NAVIGATION")
select = st.sidebar.radio("Go to:", ["Home", "Contact"])

if select == "Contact":
    st.title("📬 Contact & Support")
    st.markdown("[Email](mailto:chauhannilay888@gmail.com)")
    st.markdown("[Github](https://github.com/chauhannilay888-bot/graphico)")
    st.markdown("[Peerlist](https://peerlist.io/pandawizard)")
    st.markdown("[TwitterX](https://x.com/@PandaSWizard)")
    st.write("WhatsApp: +91 8576876419")

else:
    st.subheader("🛠️ Software & Tools")
    col = st.columns(3)
    with col[0]:
        if Path("graphico.png").exists():
            st.image("graphico.png", use_container_width=True)
        else:
            st.image("graphico.png", use_container_width=True)
        st.markdown("**Graphico Pro**")
        st.caption("Advanced data studio for seamless analytics and visualization.")
        st.link_button("Launch App →", "https://graphico.streamlit.app", use_container_width=True)

    # Books Section
    st.subheader("📖 Signature Editions")
    col1, col2 = st.columns(2)

    with col1:
        if Path("october_1.png").exists():
            st.image("october_1.png", use_container_width=True)
        else:
            st.image("https://picsum.photos/id/201/800/600", use_container_width=True)
        st.markdown("**The October Alibi (1st Edition)**")
        st.caption("A gripping tale of mystery and logic.")
        st.link_button("Amazon", "https://www.amazon.com/dp/B0GZ8WXSKR", use_container_width=True)
        st.link_button("Gumroad", "https://nelu17.gumroad.com/l/october_alibi_edition1", use_container_width=True)

    with col2:
        if Path("october_2.png").exists():
            st.image("october_2.png", use_container_width=True)
        else:
            st.image("https://picsum.photos/id/202/800/600", use_container_width=True)
        st.markdown("**The October Alibi (2nd Edition)**")
        st.caption("Expanded universe and deeper character arcs.")
        st.link_button("Amazon", "https://www.amazon.com/dp/B0H2CCRLW7", use_container_width=True)
        st.link_button("Gumroad", "https://nelu17.gumroad.com/l/october_alibi_edition2", use_container_width=True)

    # Coding Resources
    st.subheader("💻 Coding Mastery")
    col3, col4, col5 = st.columns(3)

    with col3:
        st.image("https://picsum.photos/id/237/800/500", use_container_width=True)  # Placeholder
        st.markdown("**Python 'for' Loop Mastery**")
        st.caption("Real-world challenges and deep insights.")
        st.link_button("Buy on Gumroad", "https://nelu17.gumroad.com/l/for-loop-problems", use_container_width=True)

    with col4:
        st.image("https://picsum.photos/id/180/800/500", use_container_width=True)  # Placeholder
        st.markdown("**Python 'while' Loop Deep Dive**")
        st.caption("Master conditional logic.")
        st.link_button("Buy on Gumroad", "https://nelu17.gumroad.com/l/while-loop-set", use_container_width=True)

    with col5:
        if Path("ink.png").exists():
            st.image("ink.png", use_container_width=True)
        else:
            st.image("https://picsum.photos/id/201/800/500", use_container_width=True)
        st.markdown("**Code In The Ink**")
        st.caption("Where narrative meets syntax.")
        st.link_button("Buy on Gumroad", "https://nelu17.gumroad.com/l/code_in_ink_full", use_container_width=True)


st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 40px 0; color: #64748b;">
    © 2026 Qlevo Store • Crafted with precision
</div>
""", unsafe_allow_html=True)