# Python Generators, Decorators, Context Managers, and Async Programming

## Project Overview

This project explores advanced Python programming techniques - **generators**, **decorators**, **context managers**, and **asynchronous programming** - focusing on how they improve performance, readability, and maintainability in large-scale applications.

As part of this exercise, we implement a script `seed.py` that:

- Sets up a MySQL database called **`ALX_prodev`**.  
- Creates a table **`user_data`**.  
- Populates the table with data from a CSV file (`user_data.csv`).  
- Demonstrates a **Python generator** that streams rows from the database one by one.

# 0-stream_users.py

## Script Overview

This script defines a **Python generator function** that streams rows from a MySQL database table one at a time.  
It connects to the `ALX_prodev` database, retrieves data from the `user_data` table, and yields each row as a dictionary.

The use of a generator makes this approach **memory-efficient**, as it fetches and returns rows lazily — ideal for large datasets or data pipelines that should not load the entire result set into memory.

---

## Function Definition

```python
def stream_users():
    """
    Connects to the MySQL database ALX_prodev and yields rows
    from the user_data table one at a time.

    Yields:
        dict: A dictionary containing user information with the fields:
              user_id, name, email, and age.
    """





# 1-batch_processing.py Description

This script extends the concept of row-by-row streaming by introducing batch processing.
Instead of fetching one row at a time, it retrieves and processes data in batches — improving performance while maintaining memory efficiency.

# The script defines two main functions:

stream_users_in_batches(batch_size) → Fetches user data in configurable batch sizes using a generator
batch_processing(batch_size) → Processes each batch to filter users over the age of 25

# 2-lazy_paginate.py Description
This script introduces lazy pagination using Python generators.
Instead of loading all user data at once, it fetches and processes data page by page from the MySQL database ALX_prodev.
Each page is retrieved only when required, optimizing both performance and memory usage — a key technique for working with large datasets.

The module defines two core functions:
__________________________________________________________________________________________________________________________________________
|Function	| Description|
|paginate_users(page_size, offset)|	Fetches a single page of users from the database with a specified limit (page_size) and offset.|
|lazy_pagination(page_size)|	A generator function that lazily iterates through the entire dataset, yielding one page of users at a time.|
__________________________________________________________________________________________________________________________________________