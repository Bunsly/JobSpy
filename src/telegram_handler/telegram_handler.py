from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes


# Define an abstract class
class TelegramHandler(ABC):

    @abstractmethod
    def handle(self, update: Update, context: ContextTypes):
        pass  # This is an abstract method, no implementation here.