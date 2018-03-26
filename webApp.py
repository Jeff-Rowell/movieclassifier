import numpy as np
import re
import pyprind
from nltk.corpus import stopwords
stop = stopwords.words('english')
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier

def tokenizer(text):
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text.lower())
    text = re.sub('[\W]+', ' ', text.lower()) + ' '.join(emoticons).replace('-', '')
    tokenized = [w for w in text.split() if w not in stop]
    return tokenized

def stream_docs(path):
    with open(path, 'r', encoding='utf8') as csv:
        next(csv) # skip header
        for line in csv:
            text, label = line[:-3], int(line[-2])
            yield text, label

def get_minibatch(doc_stream, size):
    docs, y = [], []
    try:
        for _ in range(size):
            text, label = next(doc_stream)
            docs.append(text)
            y.append(label)
    except StopIteration:
        return None, None
    return docs, y

vect = HashingVectorizer(decode_error='ignore', n_features=2**21, preprocessor=None,tokenizer=tokenizer)
clf = SGDClassifier(loss='log',random_state=1,max_iter=1)
doc_stream = stream_docs(path='/Users/jeffrowell/Desktop/movie_data.csv')

pbar = pyprind.ProgBar(45)
classes = np.array([0,1])
for _ in range(45):
    X_train, y_train = get_minibatch(doc_stream, size=1000)
    if not X_train:
        break
    X_train = vect.transform(X_train)
    clf.partial_fit(X_train, y_train, classes=classes)
    pbar.update()

X_test, y_test = get_minibatch(doc_stream, size=5000)
X_test = vect.transform(X_test)
clf = clf.partial_fit(X_test, y_test)
print('Accuracy: %.2f%%' %(clf.score(X_test, y_test)*100))

#Serialize the SGDClassifier and the stopword objects
import pickle
import os

dest = os.path.join('movieclassifier', 'pkl_objects')
if not os.path.exists(dest):
    os.makedirs(dest)
pickle.dump(stop, open(os.path.join(dest, 'stopwords.pkl'),'wb'),protocol=4)
pickle.dump(clf, open(os.path.join(dest, 'classifier.pkl'),'wb'),protocol=4)
