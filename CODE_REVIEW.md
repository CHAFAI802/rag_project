# 🔍 REVUE DE CODE - RAG Project (Senior Review)

---

## 📋 RÉSUMÉ EXÉCUTIF

**État global**: ⚠️ **CRITIQUE - À corriger avant production**

| Critère | Statut | Sévérité |
|---------|--------|----------|
| Architecture | ✅ Solide | - |
| Gestion erreurs | ❌ Faible | 🔴 CRITIQUE |
| Sécurité | ❌ Critique | 🔴 CRITIQUE |
| Performance | ⚠️ Problèmes | 🟠 MAJEUR |
| Type hints | ⚠️ Incomplet | 🟡 MINEUR |

---

## 🚨 PROBLÈMES CRITIQUES

### 1. **Token HuggingFace exposé en clair** 🔴 CRITIQUE

**Fichier**: `.env`
```dotenv
HF_TOKEN=your_token_here  # ❌ NE PAS COMMITER EN CLAIR!
```

**Risques**:
- Token public = accès non autorisé à votre compte HF
- Factures massives
- Accès aux modèles privés
- Révocation automatique par HuggingFace

**Actions immédiates**:
1. ⚠️ **Régénérez ce token immédiatement** sur https://huggingface.co/settings/tokens
2. Supprimez-le de tous les historiques git: `git filter-branch --force --index-filter "git rm -r --cached --ignore-unmatch .env"`
3. Ajoutez `.env` à `.gitignore` ✅ (déjà fait)

---

### 2. **embeddings.py: Fonction `embed_query()` manquante** 🔴 CRITIQUE

**Fichier**: `app/core/embeddings.py`

**Problème**:
```python
# ❌ Appel à embed_query() qui n'existe pas
def embed_query(question: str) -> list[float]:  # ⚠️ MANQUANTE!
```

**Utilisée dans**: `rag_pipeline.py` ligne 19
```python
query_vec = embed_query(question)  # ❌ ERREUR: AttributeError
```

**Solution**:
```python
def embed_query(question: str):
    return client.feature_extraction(
        [question],
        model=MODEL_NAME
    )[0]  # Retourner le premier (unique) embedding
```

---

### 3. **test_hf_api.py: Méthode inexistante** 🔴 CRITIQUE

**Fichier**: `test_hf_api.py`

```python
result = client.sentence_similarity(  # ❌ N'EXISTE PAS!
    "That is a happy person",
    [...]
)
```

**Raison**: `InferenceClient` n'a pas de méthode `sentence_similarity`. Les méthodes valides sont:
- `feature_extraction()` ✅ (utilisée correctement dans embeddings.py)
- `text_generation()`
- `question_answering()`

**Solution**:
```python
result = client.feature_extraction(
    ["That is a happy person"] + ["That is a happy dog", ...],
    model="sentence-transformers/all-MiniLM-L6-v2",
)
# Puis calculer la similarité manually avec scipy/cosine_similarity
```

---

## 🟠 PROBLÈMES MAJEURS

### 4. **Gestion d'erreurs absente** 🟠 MAJEUR

**Fichier**: `app/api/ingest.py`

```python
@router.post("/ingest")
def ingest_document(file: UploadFile = File(...)):
    # ❌ Aucune gestion d'erreur
    file_path = DATA_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)  # Peut échouer
    text = load_document(file_path)             # Peut échouer
    index_document(text, file.filename)         # Peut échouer
    return {...}
```

**Risques**:
- Fichier corrompu → crash silencieux
- Malveillant upload de fichier: pas de validation taille
- Pas de logging pour debug

**Correction requise**:
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        # Validation taille (ex: 50MB max)
        if file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        
        file_path = DATA_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = load_document(file_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Document vide après extraction")
        
        index_document(text, file.filename)
        return {"filename": file.filename, "chars_extracted": len(text), "status": "indexed"}
    
    except ValueError as e:
        logger.error(f"Format non supporté: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur ingestion: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
```

---

### 5. **RAG Pipeline: Problèmes de dimension** 🟠 MAJEUR

**Fichier**: `app/services/rag_pipeline.py`

**Problème 1 - Dimension mismatch**:
```python
def index_document(text: str, source: str):
    embeddings = embed_texts(chunks)     # numpy.ndarray shape (n_chunks, 384)
    dim = embeddings.shape[1]             # 384
    store = VectorStore(dim)              # Crée un index vierge
    # ❌ MAIS: embeddings retourné doit être float32 numpy array, pas list

def query_rag(question: str) -> str:
    query_vec = embed_query(question)    # Retourne ??? (à définir)
    store = VectorStore(len(query_vec))  # ❌ MAUVAIS: utilise len() au lieu de dimensionalité!
```

**Problème 2 - Réinitialisation index**:
```python
# Dans query_rag():
store = VectorStore(dim)  # ❌ Crée un NOUVEL index vide à chaque requête!
                          # Les vecteurs d'indexation sont perdus
```

**Solution**:
```python
def index_document(text: str, source: str):
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)  # numpy array (n, 384)
    
    # Conversion correcte
    if not isinstance(embeddings, np.ndarray):
        embeddings = np.array(embeddings, dtype="float32")
    else:
        embeddings = embeddings.astype("float32")
    
    dim = embeddings.shape[1]
    store = VectorStore(dim)
    metadatas = [{"text": c, "source": source} for c in chunks]
    store.add(embeddings, metadatas)

def query_rag(question: str) -> str:
    query_vec = embed_query(question)  # numpy array (384,)
    
    # ✅ Charger l'index EXISTANT
    store = VectorStore(len(query_vec) if isinstance(query_vec, list) else query_vec.shape[0])
    
    distances, indices = store.search(query_vec)
    # ... reste OK
```

---

### 6. **Vectorstore: Perte de cohérence index/metadata** 🟠 MAJEUR

**Fichier**: `app/core/vectorstore.py`

```python
def add(self, vectors, metadatas):
    self.index.add(vectors)              # Ajoute au FAISS
    self.metadata.extend(metadatas)      # Ajoute à JSON
    self.save()  # ❌ Risque: si save() échoue = désynchronisation
```

**Scénario de corruption**:
1. Ajout 100 vecteurs à FAISS ✅
2. Ajout 100 metadatas à JSON ✅
3. Sauvegarde échoue (disque plein) ❌
4. FAISS sur disque ≠ metadata en mémoire

**Solution**:
```python
def add(self, vectors, metadatas):
    try:
        self.index.add(vectors)
        self.metadata.extend(metadatas)
    except Exception as e:
        logger.error(f"Erreur ajout vecteur: {e}")
        raise
    
    try:
        self.save()
    except Exception as e:
        logger.error(f"Erreur sauvegarde FAISS: {e}")
        # Rollback?
        self.metadata = self.metadata[:-len(metadatas)]
        raise
```

---

### 7. **Chemin hard-codé** 🟠 MAJEUR

**Fichier**: `app/core/vectorstore.py`

```python
INDEX_PATH = Path("data/faiss_index/index.faiss")  # ❌ Chemin relatif
```

**Problèmes**:
- Cwd différent = fichier pas trouvé
- Tests impossible (pollution données)
- Production fragile

**Solution**:
```python
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).parent.parent.parent
INDEX_PATH = PROJECT_ROOT / "data/faiss_index/index.faiss"
```

---

## 🟡 PROBLÈMES MINEURS

### 8. **Type hints incomplets** 🟡 MINEUR

**Fichier**: `app/core/embeddings.py`

```python
def embed_texts(texts: list[str]) -> list[list[float]]:  # ❌ Retourne numpy array, pas list
    return client.feature_extraction(...)
```

**Correction**:
```python
import numpy as np
from numpy.typing import NDArray

def embed_texts(texts: list[str]) -> NDArray:
    """Retourne un numpy array (n_texts, 384)"""
    result = client.feature_extraction(texts, model=MODEL_NAME)
    return np.array(result, dtype="float32")

def embed_query(question: str) -> NDArray:
    """Retourne un numpy array (384,)"""
    result = client.feature_extraction([question], model=MODEL_NAME)
    return np.array(result[0], dtype="float32")
```

---

### 9. **Logging absent** 🟡 MINEUR

Pas de logging dans:
- `rag_pipeline.py`
- `chunker.py`
- `api/ingest.py`

**Impact**: Impossible de déboguer en production.

**Ajout simple**:
```python
import logging

logger = logging.getLogger(__name__)

def index_document(text: str, source: str):
    logger.info(f"Indexation de {source}")
    chunks = chunk_text(text)
    logger.debug(f"Créé {len(chunks)} chunks")
    ...
```

---

### 10. **config.py vide** 🟡 MINEUR

**Fichier**: `app/core/config.py`

Manquent les constantes centralisées. À créer:
```python
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_docs"
FAISS_INDEX_DIR = DATA_DIR / "faiss_index"

# API
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN env variable obligatoire")

# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Search
K_RESULTS = 5

# LLM
LLM_MAX_TOKENS = 300
LLM_TEMPERATURE = 0.0
```

---

### 11. **Pas de validation entrée utilisateur** 🟡 MINEUR

**Fichier**: `app/api/query.py`

```python
class QueryRequest(BaseModel):
    question: str  # ❌ Pas de contraintes
```

**Amélioration**:
```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
```

---

### 12. **Singleton LLM non thread-safe** 🟡 MINEUR

**Fichier**: `app/core/llm.py`

```python
_llm = None  # ❌ Risque race condition en async

def get_llm():
    global _llm
    if _llm is None:
        _llm = pipeline(...)  # ❌ Deux requêtes simultanées = double instantiation
    return _llm
```

**Solution (bonus)**:
```python
from threading import Lock

_llm = None
_llm_lock = Lock()

def get_llm():
    global _llm
    if _llm is None:
        with _llm_lock:
            if _llm is None:  # Double-check pattern
                _llm = pipeline(...)
    return _llm
```

---

## 📊 WORKFLOW ACTUEL

```
┌─────────────────────────────────────────────────────────┐
│                   INGESTION WORKFLOW                    │
├─────────────────────────────────────────────────────────┤

1. POST /api/ingest → upload fichier
   │
   ├─→ Sauvegarde: data/raw_docs/{filename}
   │
   ├─→ load_document() → extraction texte
   │   ├─ PDF: PyPDF2
   │   ├─ DOCX: python-docx
   │   └─ TXT/MD: read_text()
   │
   ├─→ index_document()
   │   ├─ chunk_text() → 500 char chunks, overlap 100
   │   ├─ embed_texts() → HF Inference API (all-MiniLM-L6-v2)
   │   ├─ VectorStore.add() → FAISS + JSON metadata
   │   └─ Sauvegarde: data/faiss_index/{index.faiss, metadata.json}
   │
   └─→ Response: {"filename": "...", "chars_extracted": N, "status": "indexed"}

┌─────────────────────────────────────────────────────────┐
│                    QUERY WORKFLOW                       │
├─────────────────────────────────────────────────────────┤

1. POST /api/query → {"question": "..."}
   │
   ├─→ embed_query() → HF Inference API
   │
   ├─→ VectorStore.search(k=5) → FAISS similarity
   │   ├─ Charge index depuis disque
   │   ├─ Recherche top-5 résultats L2
   │   └─ Récupère metadata associée
   │
   ├─→ Contexte = concatène chunks top-5
   │
   ├─→ generate_answer() → Mistral-7B local
   │   ├─ Création prompt avec contexte
   │   ├─ Inférence (lazy-loaded singleton)
   │   └─ Parse réponse après "ANSWER:"
   │
   └─→ Response: {"answer": "..."}

```

---

## ✅ POINTS POSITIFS

| Point | Description |
|-------|------------|
| ✅ Architecture | Clean separation (API/Core/Services) |
| ✅ Abstractions | VectorStore encapsule bien FAISS |
| ✅ Type hints | Présents (bien que imparfaits) |
| ✅ Modularité | Facile à tester chaque composant |
| ✅ Formatters | Support multi-format (PDF, DOCX, TXT) |

---

## 🔧 PLAN D'ACTION (Ordre priorité)

### Phase 1: CRITIQUE (24h)
- [ ] **Régénérer le token HF** et le retirer du repo
- [ ] **Implémenter `embed_query()`** dans embeddings.py
- [ ] **Corriger test_hf_api.py** ou le supprimer
- [ ] **Ajouter gestion d'erreurs** dans ingest.py

### Phase 2: MAJEUR (3-5 jours)
- [ ] **Fixer RAG pipeline** (dimensions, réinitialisation)
- [ ] **Centraliser config.py**
- [ ] **Ajouter logging** partout
- [ ] **Chemin absolu** pour FAISS

### Phase 3: MINEUR (1-2 semaines)
- [ ] **Type hints complets**
- [ ] **Validation Pydantic** QueryRequest
- [ ] **Thread-safety** pour LLM singleton
- [ ] **Tests unitaires**

---

## 📝 CONCLUSION

**Statut**: 🚨 **NON PRÊT POUR PRODUCTION**

**Raisons**:
1. Sécurité: Token exposé
2. Bugs: Fonction manquante `embed_query()`
3. Robustesse: Zéro gestion d'erreurs
4. Intégrité: Risques désynchronisation FAISS/metadata

**ETA avant production**: 1 semaine si toutes les corrections appliquées
