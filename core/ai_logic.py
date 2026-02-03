import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Case, When
from .models import Product

# Preuzimanje potrebnih resursa (samo pri prvom pokretanju)
nltk.download('wordnet')
nltk.download('stopwords')

def preprocess_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english')) # Možeš dodati i hrvatske ako nađeš listu
    
    # Mala mapa sinonima za tvoj shop
    synonyms = {
        'sport': 'trening trčanje teretana fitness',
        'tehnologija': 'gadget elektronika računalo gaming',
        'romantika': 'djevojka dečko godišnjica ljubav'
    }
    
    words = text.lower().split()
    processed_words = []
    
    for word in words:
        # Dodaj sinonime ako riječ postoji u mapi
        if word in synonyms:
            processed_words.append(synonyms[word])
        
        # Lemmatizacija (svođenje na korijen)
        if word not in stop_words:
            processed_words.append(lemmatizer.lemmatize(word))
            
    return " ".join(processed_words)

def get_local_recommendations(user_prefs):
    # 1. Budžet filtriranje
    products = Product.objects.filter(price__lte=user_prefs['budget'])
    if not products.exists():
        return []

    data = []
    for p in products:
        # Preprosiramo tekst svakog proizvoda
        combined = f"{p.name} {p.description} {p.interests} {p.occasion}"
        data.append({
            'id': p.id, 
            'features': preprocess_text(combined)
        })
    
    df = pd.DataFrame(data)

    # 2. Vektorizacija
    tfidf = TfidfVectorizer(ngram_range=(1, 2)) # Gleda i parove riječi (npr. "bežične slušalice")
    tfidf_matrix = tfidf.fit_transform(df['features'])

    # 3. Korisnički unos
    user_query = f"{user_prefs['interests']} {user_prefs['occasion']} {user_prefs['relationship']}"
    user_vector = tfidf.transform([preprocess_text(user_query)])

    # 4. Izračun sličnosti
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()
    df['score'] = similarity_scores
    
    # Filtriramo samo one koji imaju bar neki score > 0
    df = df[df['score'] > 0]
    
    recommended_ids = df.sort_values(by='score', ascending=False).head(4)['id'].tolist()

    if not recommended_ids:
        return Product.objects.none()

    # 5. Očuvanje redoslijeda (najbolji rezultat prvi)
    preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
    return Product.objects.filter(id__in=recommended_ids).order_by(preserved_order)