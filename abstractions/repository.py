"""
Repository Abstraction Module.

This module defines the base repository interface implementing the
Repository design pattern. Repositories abstract database operations,
providing a clean interface for data access with built-in caching.

Example:
    >>> class UserRepository(IRepository):
    ...     def __init__(self, session, **kwargs):
    ...         super().__init__(model=UserModel, **kwargs)
    ...         self.session = session
    ...
    ...     def find_by_email(self, email: str) -> UserModel:
    ...         return self.session.query(self.model).filter_by(email=email).first()
"""

from abc import ABC
from datetime import datetime
from operator import attrgetter
from typing import Optional, Dict, Any

from cachetools import cachedmethod, LRUCache
from loguru import logger
from sqlalchemy.ext.declarative import DeclarativeMeta


class IRepository(ABC):
    """
    Abstract base class for database repository pattern implementation.

    The IRepository class provides a standardized interface for data access
    operations in the FastMVC framework. It includes built-in support for:
        - CRUD operations (Create, Read, Update, Delete)
        - Query result caching with LRU cache
        - Execution time logging for performance monitoring
        - Soft delete support via is_deleted flag

    Attributes:
        urn (str): Unique Request Number for tracing.
        user_urn (str): User's unique resource name.
        api_name (str): Name of the API endpoint.
        user_id (str): Database identifier of the user.
        model (DeclarativeMeta): SQLAlchemy model class for this repository.
        cache (LRUCache): Cache instance for query result caching.
        logger: Structured logger bound with request context.

    Note:
        Subclasses must provide a `session` attribute (SQLAlchemy session)
        for database operations to work.

    Example:
        >>> class ProductRepository(IRepository):
        ...     def __init__(self, session, cache_size: int = 100):
        ...         super().__init__(
        ...             model=ProductModel,
        ...             cache=LRUCache(maxsize=cache_size)
        ...         )
        ...         self.session = session
        ...
        ...     def find_by_category(self, category: str):
        ...         return self.session.query(self.model).filter_by(
        ...             category=category
        ...         ).all()
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
        model: DeclarativeMeta = None,
        cache: LRUCache = None,
    ) -> None:
        """
        Initialize the repository with model and optional caching.

        Args:
            urn (str, optional): Unique Request Number for tracing. Defaults to None.
            user_urn (str, optional): User's unique resource name. Defaults to None.
            api_name (str, optional): Name of the API endpoint. Defaults to None.
            user_id (str, optional): Database ID of the user. Defaults to None.
            model (DeclarativeMeta, optional): SQLAlchemy model class. Defaults to None.
            cache (LRUCache, optional): Cache instance for results. Defaults to None.
        """
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
        )
        self._model = model
        self._cache = cache

    @property
    def urn(self) -> str:
        """str: Get the Unique Request Number."""
        return self._urn

    @urn.setter
    def urn(self, value: str) -> None:
        """Set the Unique Request Number."""
        self._urn = value

    @property
    def user_urn(self) -> str:
        """str: Get the user's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str) -> None:
        """Set the user's unique resource name."""
        self._user_urn = value

    @property
    def api_name(self) -> str:
        """str: Get the API endpoint name."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str) -> None:
        """Set the API endpoint name."""
        self._api_name = value

    @property
    def logger(self):
        """loguru.Logger: Get the structured logger instance."""
        return self._logger

    @logger.setter
    def logger(self, value) -> None:
        """Set the structured logger instance."""
        self._logger = value

    @property
    def user_id(self) -> str:
        """str: Get the user's database identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        """Set the user's database identifier."""
        self._user_id = value

    @property
    def model(self) -> DeclarativeMeta:
        """DeclarativeMeta: Get the SQLAlchemy model class."""
        return self._model

    @model.setter
    def model(self, value: DeclarativeMeta) -> None:
        """Set the SQLAlchemy model class."""
        self._model = value

    @property
    def cache(self) -> LRUCache:
        """LRUCache: Get the cache instance."""
        return self._cache

    @cache.setter
    def cache(self, value: LRUCache) -> None:
        """Set the cache instance."""
        self._cache = value

    def create_record(
        self,
        record: DeclarativeMeta,
    ) -> DeclarativeMeta:
        """
        Create a new record in the database.

        Adds the record to the session and commits the transaction.
        Logs the execution time for performance monitoring.

        Args:
            record (DeclarativeMeta): The model instance to persist.

        Returns:
            DeclarativeMeta: The persisted record with generated ID.

        Raises:
            SQLAlchemyError: If database operation fails.

        Example:
            >>> user = UserModel(email="user@example.com", name="John")
            >>> created_user = repository.create_record(user)
            >>> print(created_user.id)  # Auto-generated ID
        """
        start_time = datetime.now()
        self.session.add(record)
        self.session.commit()

        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record

    @cachedmethod(attrgetter('_cache'))
    def retrieve_record_by_id(
        self,
        id: str,
        is_deleted: bool = False
    ) -> Optional[DeclarativeMeta]:
        """
        Retrieve a record by its primary key ID.

        Results are cached using LRU cache for improved performance
        on repeated queries.

        Args:
            id (str): The primary key ID of the record.
            is_deleted (bool, optional): Filter by soft-delete status.
                Defaults to False (only active records).

        Returns:
            Optional[DeclarativeMeta]: The found record or None if not found.

        Example:
            >>> user = repository.retrieve_record_by_id("user-123")
            >>> if user:
            ...     print(user.email)
        """
        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(self.model.id == id, self.model.is_deleted == is_deleted)
            .first()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    @cachedmethod(attrgetter('_cache'))
    def retrieve_record_by_urn(
        self,
        urn: str,
        is_deleted: bool = False,
    ) -> Optional[DeclarativeMeta]:
        """
        Retrieve a record by its Unique Resource Name (URN).

        Results are cached using LRU cache for improved performance
        on repeated queries.

        Args:
            urn (str): The unique resource name of the record.
            is_deleted (bool, optional): Filter by soft-delete status.
                Defaults to False (only active records).

        Returns:
            Optional[DeclarativeMeta]: The found record or None if not found.

        Example:
            >>> user = repository.retrieve_record_by_urn("urn:user:abc123")
            >>> if user:
            ...     print(user.name)
        """
        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(self.model.urn == urn, self.model.is_deleted == is_deleted)
            .first()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    def update_record(
        self,
        id: str,
        new_data: Dict[str, Any],
    ) -> DeclarativeMeta:
        """
        Update an existing record with new data.

        Finds the record by ID and updates the specified attributes.
        Commits the transaction and logs execution time.

        Args:
            id (str): The primary key ID of the record to update.
            new_data (dict): Dictionary of attribute names to new values.

        Returns:
            DeclarativeMeta: The updated record.

        Raises:
            ValueError: If no record with the given ID exists.
            SQLAlchemyError: If database operation fails.

        Example:
            >>> updated_user = repository.update_record(
            ...     id="user-123",
            ...     new_data={"name": "Jane Doe", "email": "jane@example.com"}
            ... )
        """
        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(self.model.id == id)
            .first()
        )

        if not record:
            raise ValueError(f"{self.model.__name__} with id {id} not found")

        for attr, value in new_data.items():
            setattr(record, attr, value)

        self.session.commit()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record
