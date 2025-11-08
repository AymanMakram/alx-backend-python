#!/usr/bin/env python3
"""
Run multiple database queries concurrently using asyncio.gather
and aiosqlite for asynchronous database operations.
"""

import asyncio
import aiosqlite


async def async_fetch_users():
    """Fetch all users asynchronously from the database."""
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("All Users:", results)
            return results


async def async_fetch_older_users():
    """Fetch users older than 40 asynchronously."""
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            results = await cursor.fetchall()
            print("Users older than 40:", results)
            return results


async def fetch_concurrently():
    """Run multiple asynchronous queries concurrently."""
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return results


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())