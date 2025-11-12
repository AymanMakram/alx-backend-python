# Unit Test for `utils.access_nested_map`

This directory contains a unit test for the `access_nested_map` function from the `utils` module.

---

## 📘 Description

The purpose of this test is to verify that the function `access_nested_map` correctly retrieves values from a nested dictionary (map) using a sequence of keys (`path`).

`access_nested_map` is expected to:
- Return the correct value for valid key paths.
- Raise a `KeyError` if a key in the path does not exist (tested in a later task).

This test file follows the `unittest` framework and uses `parameterized` for multiple test cases.

---

## 🧪 Test File

**File:** `test_utils.py`

### Contains:
- `TestAccessNestedMap` class inheriting from `unittest.TestCase`
- `test_access_nested_map` method decorated with `@parameterized.expand`

### Tested Inputs:
| Nested Map | Path | Expected Result |
|-------------|------|-----------------|
| `{"a": 1}` | `("a",)` | `1` |
| `{"a": {"b": 2}}` | `("a",)` | `{"b": 2}` |
| `{"a": {"b": 2}}` | `("a", "b")` | `2` |

---

## ⚙️ How to Run Tests

From the project root directory:

```bash
python3 -m unittest 0x03-Unittests_and_integration_tests/test_utils.py
