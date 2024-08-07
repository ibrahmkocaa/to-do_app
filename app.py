import streamlit as st
from supabase import create_client, Client

# Supabase yapılandırması
SUPABASE_URL = 'https://ggpakaubpgghwsboiglb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdncGFrYXVicGdnaHdzYm9pZ2xiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI5MzgwMDEsImV4cCI6MjAzODUxNDAwMX0.HXBPLxmkY5vee65H76iSD08LM9BxQ3CCFFZXUFdauW8'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Kullanıcı Girişi
def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        st.error(f"Giriş hatası: {e}")
        return None

# Kullanıcı Kaydı
def signup(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return response
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")
        return None

# Görev Fonksiyonları
def get_tasks(user_id, category=None):
    if category:
        response = supabase.table('to-do').select('*').eq('user_id', user_id).eq('category', category).execute()
    else:
        response = supabase.table('to-do').select('*').eq('user_id', user_id).execute()
    return response.data

def add_task(user_id, task, category):
    supabase.table('to-do').insert({'user_id': user_id, 'task': task, 'category': category, 'completed': False}).execute()

def update_task(task_id, completed):
    supabase.table('to-do').update({'completed': completed}).eq('id', task_id).execute()

def delete_task(task_id):
    supabase.table('to-do').delete().eq('id', task_id).execute()

# Başlık
st.title("To-Do List Uygulaması")

# Giriş durumu için bir oturum durumu anahtarı kullanın
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Kullanıcı oturum açmamışsa giriş formunu gösterin
if not st.session_state['authenticated']:
    # Giriş/Kayıt Seçeneği
    auth_option = st.radio("Seçenek", ["Giriş Yap", "Kayıt Ol"])

    email = st.text_input("Email")
    password = st.text_input("Şifre", type="password")
    user = None

    if auth_option == "Giriş Yap":
        if st.button("Giriş Yap"):
            user = login(email, password)
            if user:
                st.success("Giriş başarılı!")
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                st.rerun()

    elif auth_option == "Kayıt Ol":
        if st.button("Kayıt Ol"):
            user = signup(email, password)
            if user:
                st.success("Kayıt başarılı!")
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                st.rerun()

# Kullanıcı oturum açmışsa uygulama içeriğini gösterin
if st.session_state['authenticated']:
    user = st.session_state['user']
    user_id = user.user.id

    st.write("Hoşgeldiniz, ", user.user.email)  # E-posta adresini göster

    # Kategori seçici
    categories = ["İş", "Kişisel", "Alışveriş", "Diğer"]
    category = st.selectbox("Kategori Seçin", categories)

    # Görev ekleme
    new_task = st.text_input("Yeni görev ekle:")
    if st.button("Görev Ekle"):
        add_task(user_id, new_task, category)
        st.success(f"'{new_task}' görevi eklendi!")

    # Kategorileri filtreleme
    selected_category = st.selectbox("Görevleri Görüntülemek İçin Kategori Seçin", ["Tümü"] + categories)
    tasks = get_tasks(user_id, None if selected_category == "Tümü" else selected_category)

    # Görevleri göster
    
    st.subheader("Görevler")
    for task in tasks:
        task_id = task['id']
        task_name = task['task']
        completed = task['completed']
        is_checked = st.checkbox(task_name, completed,key = task_id)
        if is_checked != completed:
            update_task(task_id, is_checked)

    # Tamamlanan görevleri sil
    if st.button("Tamamlanan Görevleri Sil"):
        completed_tasks = [task for task in tasks if task['completed']]
        for task in completed_tasks:
            delete_task(task['id'])
        st.success("Tamamlanan görevler silindi!")
        st.rerun()
        


    # Çıkış yap butonu
    if st.button("Çıkış Yap"):
        st.session_state['authenticated'] = False
        st.session_state['user'] = None
        st.rerun()