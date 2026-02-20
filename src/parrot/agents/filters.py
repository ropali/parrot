from abc import ABC, abstractmethod


class TextFilter(ABC):
    """
    Abstract base class for text filters.
    """

    @abstractmethod
    def apply(self, text: str) -> str:
        """
        Apply the filter to the given text.

        Args:
            text (str): The input text to filter.

        Returns:
            str: The filtered text.
        """
        pass
