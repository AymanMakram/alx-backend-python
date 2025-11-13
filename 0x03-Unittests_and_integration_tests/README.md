# Unit Tests for `utils.py`

This directory contains unit tests for selected functions in the `utils.py` module, part of the **ALX Backend Python** project *0x03 - Unittests and Integration Tests*.

---

## 📘 Overview

The goal of these tests is to ensure that individual functions in `utils.py` behave as expected under both normal and exceptional conditions, **without making any external network or file system calls**.

All tests are written using Python’s built-in `unittest` framework and the `parameterized` library for running multiple test cases efficiently.

---

## 🧪 Tested Functions

### 1️⃣ `access_nested_map`

**Purpose:**  
Retrieves values from a nested dictionary (map) based on a sequence of keys (path).

**Test class:** `TestAccessNestedMap`

| Test Name | Description | Expected Result |
|------------|--------------|-----------------|
| `test_access_nested_map` | Tests valid paths returning expected values | Returns correct nested value |
| `test_access_nested_map_exception` | Tests invalid paths that should raise `KeyError` | Raises `KeyError` with correct message |

**Example Inputs**

| Nested Map | Path | Expected Output |
|-------------|------|-----------------|
| `{"a": 1}` | `("a",)` | `1` |
| `{"a": {"b": 2}}` | `("a",)` | `{"b": 2}` |
| `{"a": {"b": 2}}` | `("a", "b")` | `2` |
| `{}` | `("a",)` | `KeyError('a')` |
| `{"a": 1}` | `("a", "b")` | `KeyError('b')` |

---

### 2️⃣ `get_json`

**Purpose:**  
Fetches JSON data from a URL using `requests.get` and returns the parsed result.

**Test class:** `TestGetJson`

| Test Name | Description | Expected Result |
|------------|--------------|-----------------|
| `test_get_json` | Ensures that `get_json` returns the correct payload and calls `requests.get` exactly once per test | Returns mocked JSON payload |

**Mocked Inputs**

| Test URL | Mocked JSON Payload |
|-----------|---------------------|
| `http://example.com` | `{"payload": True}` |
| `http://holberton.io` | `{"payload": False}` |

**Mocking Behavior:**
- Uses `unittest.mock.patch("utils.requests.get")` to intercept HTTP requests.
- Replaces the `requests.get` call with a mock that simulates `.json()` returning `test_payload`.

---

## ⚙️ How to Run Tests

From the root of your repository, execute:

```bash
python3 -m unittest 0x03-Unittests_and_integration_tests/test_utils.py
