from abc import ABC, abstractmethod


class GoozaliRequest(ABC):
    @abstractmethod
    def create(self):
        """Abstract method to be implemented in subclasses."""
        pass
