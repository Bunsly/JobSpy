from typing import Optional

from dotenv import load_dotenv
from pymongo import UpdateOne

from jobspy import create_logger
from .Position import Position
from .monogo_db import mongo_client

load_dotenv()


class PositionRepository:
    _instance = None

    def __new__(cls):

        if cls._instance is not None:
            return cls._instance

        self = super().__new__(cls)
        cls._instance = self
        self.logger = create_logger("PositionRepository")
        self.collection = mongo_client.db["field"]
        return cls._instance

    def find_all(self) -> list[Position]:
        positions = list(self.collection.find({}))
        return [Position(**position) for position in positions]

    def find_by_id(self, position_id: str) -> Optional[Position]:
        """
        Finds a position document in the collection by its ID.

        Args:
            position_id: The ID of the position to find.

        Returns:
            The position document if found, otherwise None.
        """
        result = self.collection.find_one({"id": position_id})
        return Position(**result)

    def update(self, position: Position) -> bool:
        """
        Updates a Position in the database.

        Args:
            position: A dictionary representing the Position data.

        Returns:
            True if the update was successful, False otherwise.
        """
        result = self.collection.update_one({"id": position.id}, {"$set": position.model_dump()})
        return result.modified_count > 0

    def insert_position(self, position: Position):
        """
        Inserts a new position posting into the database collection.

        Args:
            position (Position): The Position object to be inserted.

        Raises:
            Exception: If an error occurs during insertion.
        """
        self.collection.insert_one(position.model_dump())
        self.logger.info(f"Inserted new position with name {position.name}.")

    def insert_many_if_not_found(self, positions: list[Position]) -> tuple[list[Position], list[Position]]:
        """
        Perform bulk upserts for a list of Position objects into a MongoDB collection.
        Only insert new positions and return the list of newly inserted positions.
        """
        operations = []
        new_positions = []  # List to store the new positions inserted into MongoDB
        old_positions = []  # List to store the new positions inserted into MongoDB
        for position in positions:
            position_dict = position.model_dump()
            operations.append(
                UpdateOne(
                    {"id": position.id},  # Match by `id`
                    # Only set positions if the position is being inserted (not updated)
                    {"$setOnInsert": position_dict},
                    upsert=True  # Insert if not found, but do not update if already exists
                )
            )

        if operations:
            # Execute all operations in bulk
            result = self.collection.bulk_write(operations)
            self.logger.info(f"Matched: {result.matched_count}, Upserts: {
            result.upserted_count}, Modified: {result.modified_count}")

            # Get the newly inserted positions (those that were upserted)
            # The `upserted_count` corresponds to how many new documents were inserted
            for i, position in enumerate(positions):
                if result.upserted_count > 0 and i < result.upserted_count:
                    new_positions.append(position)
                else:
                    old_positions.append(position)

        return old_positions, new_positions


position_repository = PositionRepository()
