from abc import ABC, abstractmethod



class StorageClient(ABC):
    """Abstract base class for a storage client."""

    @abstractmethod
    def get_container(self, name: str):
        """Get a container by name.

        Args:
            name (str): The name of the container.

        Returns:
            The container object.
        """
        pass

    @abstractmethod
    def get_file(self, container_name: str, file_name: str):
        """Get a file from a container.

        Args:
            container_name (str): The name of the container.
            file_name (str): The name of the file.

        Returns:
            The file object.
        """
        pass

    @abstractmethod
    def get_file_from_url(self, container_name: str, full_url: str):
        """Get a file from a URL.

        Args:
            container_name (str): The name of the container.
            full_url (str): The full URL of the file.

        Returns:
            The file object.
        """
        pass

    @abstractmethod
    def get_sas_url(self, container_name: str, file_path: str, expiry_hours: int) -> str:
        """Get a shared access signature (SAS) URL for a file.

        Args:
            container_name (str): The name of the container.
            file_path (str): The path of the file.
            expiry_hours (int): The number of hours until the SAS URL expires.

        Returns:
            The SAS URL as a string.
        """
        pass
    @abstractmethod
    def clone_file(self, file_url:str, destination_container_name:str, destination_file_path:str):
        pass