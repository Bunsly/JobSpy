from typing import Optional

from cachebox import LRUCache
from dotenv import load_dotenv
from pymongo import UpdateOne

from jobspy import create_logger
from .User import User
from .monogo_db import mongo_client

load_dotenv()


class UserRepository:
    def __init__(self):
        self._cache = LRUCache(50)
        self._logger = create_logger("UserRepository")
        self._collection = mongo_client.get_collection('user')
        self._collection.create_index('username', unique=True)

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Finds a user document in the collection by its ID.

        Args:
            user_id: The ID of the user to find.

        Returns:
            The user document if found, otherwise None.
        """
        user = None
        cached_user = self._cache[user_id]
        if cached_user:
            return User(**cached_user)

        result = self._collection.find_one({"id": user_id})

        if result:
            user = User(**result)
            self._cache[user_id] = user

        return user

    def find_by_username(self, username: str) -> Optional[User]:
        """
        Finds a user document in the collection by its username.

        Args:
            username: The username of the user to find.

        Returns:
            The user document if found, otherwise None.
        """
        user = None
        cached_user = self._cache.get(username)
        if cached_user:
            return cached_user

        self._logger.info("Find user by username")
        result = self._collection.find_one({"username": username})
        if result:
            user = User(**result)
            self._cache[username] = user

        return user

    def update(self, user: User) -> bool:
        """
        Updates a User in the database.

        Args:
            user: A dictionary representing the User data.

        Returns:
            True if the update was successful, False otherwise.
        """
        result = self._collection.update_one({"id": user.id}, {"$set": user.model_dump()})
        return result.modified_count > 0

    def insert_user(self, user: User):
        """
        Inserts a new user posting into the database collection.

        Args:
            user (User): The User object to be inserted.

        Raises:
            Exception: If an error occurs during insertion.
        """
        self._collection.insert_one(user.model_dump())
        self._logger.info(f"Inserted new user with username {user.username}.")

    def insert_many_if_not_found(self, users: list[User]) -> tuple[list[User], list[User]]:
        """
        Perform bulk upserts for a list of User objects into a MongoDB collection.
        Only insert new users and return the list of newly inserted users.
        """
        operations = []
        new_users = []  # List to store the new users inserted into MongoDB
        old_users = []  # List to store the new users inserted into MongoDB
        for user in users:
            user_dict = user.model_dump()
            operations.append(
                UpdateOne(
                    {"id": user.id},  # Match by `id`
                    # Only set fields if the user is being inserted (not updated)
                    {"$setOnInsert": user_dict},
                    upsert=True  # Insert if not found, but do not update if already exists
                )
            )

        if operations:
            # Execute all operations in bulk
            result = self._collection.bulk_write(operations)
            self._logger.info(f"Matched: {result.matched_count}, Upserts: {
            result.upserted_count}, Modified: {result.modified_count}")

            # Get the newly inserted users (those that were upserted)
            # The `upserted_count` corresponds to how many new documents were inserted
            for i, user in enumerate(users):
                if result.upserted_count > 0 and i < result.upserted_count:
                    new_users.append(user)
                else:
                    old_users.append(user)

        return old_users, new_users


user_repository = UserRepository()
