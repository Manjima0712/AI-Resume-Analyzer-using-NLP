import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.lemmatizer.lemmatize('warmup')

    def clean_text(self, text):
        """Cleans and preprocesses the given text. Lowercase, remove symbols, Lemmatize."""
        if not text:
            return ""
            
        text = text.lower()
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        
        words = text.split()
        cleaned_words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        
        return " ".join(cleaned_words)
