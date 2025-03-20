from abc import ABC, abstractmethod


class Task(ABC):
    def __init__(self, name) -> None:
        """Base class for all tasks.
        Args:
            name (str): The name of the task.
        """
        super().__init__()
        self.name = name
        self.output_folder = ""
        self.project_name = ""

    @abstractmethod
    def execute(self) -> None:
        """Execute the task."""
