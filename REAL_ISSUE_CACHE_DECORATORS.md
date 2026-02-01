# 🔴 CRITICAL ISSUE FOUND: @st.cache_data Decorators at Module Level

## The Real Problem

The app is crashing because **`@st.cache_data` decorators are being evaluated at module import time**, before Streamlit is fully initialized in Databricks Apps.

### Lines with @st.cache_data:
- Line 448: `@st.cache_data(ttl=300)`
- Line 476: `@st.cache_data(ttl=60)`

### Why This Crashes in Databricks Apps

```python
# At module level (CRASHES in Databricks Apps)
@st.cache_data(ttl=300)  # ❌ st.cache_data() called when module loads!
def load_data_from_delta(...):
    pass
```

**What happens:**
1. Databricks imports the module
2. Python sees `@st.cache_data(ttl=300)` 
3. Python calls `st.cache_data(ttl=300)` immediately
4. Streamlit isn't initialized yet → **CRASH**

### Solution Options

#### Option 1: Remove Decorators (Simplest, works immediately)
```python
# NO decorator - function works without caching
def load_data_from_delta(table_name, limit=10000):
    """Load data from Delta table"""
    # ... implementation ...
```

**Pros:** Guaranteed to work  
**Cons:** No caching (but synthetic data is fast anyway)

#### Option 2: Use st.cache_data inside main() (Complex)
```python
def main():
    st.set_page_config(...)
    
    # Apply caching dynamically
    global load_data_from_delta
    load_data_from_delta = st.cache_data(ttl=300)(load_data_from_delta)
    
    # rest of app...
```

**Pros:** Keeps caching  
**Cons:** Complex, harder to maintain

#### Option 3: Use functools.lru_cache (Python native)
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def load_data_from_delta(table_name, limit=10000):
    # ... implementation ...
```

**Pros:** Works at module level, Python native  
**Cons:** Not Streamlit-aware, no TTL

### Recommended Fix

**Remove the `@st.cache_data` decorators temporarily** to get the app working, then add back caching using a Databricks-safe method.

```python
# Before (CRASHES)
@st.cache_data(ttl=300)
def load_data_from_delta(table_name, limit=10000):
    pass

# After (WORKS)
def load_data_from_delta(table_name, limit=10000):
    pass
```

Since the app falls back to synthetic data anyway, and synthetic data generation is fast, **removing caching won't significantly impact performance**.

---

## Implementation

Remove these two lines from app.py:
- Line 448: `@st.cache_data(ttl=300)`
- Line 476: `@st.cache_data(ttl=60)`

This will allow the app to start successfully in Databricks Apps.

---

**Status:** Critical issue identified  
**Priority:** 🔴 HIGH  
**Action:** Remove Streamlit decorators from module level
