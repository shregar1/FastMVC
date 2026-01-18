import os
from datetime import datetime
from http import HTTPStatus

import bcrypt
from ulid import ULID

from constants.api_status import APIStatus
from dtos.requests.user.registration import UserRegistrationRequestDTO
from dtos.responses.base import BaseResponseDTO
from errors.bad_input_error import BadInputError
from models.user import User
from repositories.user import UserRepository
from services.user.abstraction import IUserService


class UserRegistrationService(IUserService):
    """
    Service to handle user registration and new user creation.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
        user_repository: UserRepository = None,
    ) -> None:
        super().__init__(urn, user_urn, api_name)
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._user_repository = user_repository
        self.logger.debug(
            f"UserRegistrationService initialized for "
            f"user_id={user_id}, urn={urn}, api_name={api_name}"
        )

    @property
    def urn(self):
        return self._urn

    @urn.setter
    def urn(self, value):
        self._urn = value

    @property
    def user_urn(self):
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value):
        self._user_urn = value

    @property
    def api_name(self):
        return self._api_name

    @api_name.setter
    def api_name(self, value):
        self._api_name = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def user_repository(self):
        return self._user_repository

    @user_repository.setter
    def user_repository(self, value):
        self._user_repository = value

    async def run(self, request_dto: UserRegistrationRequestDTO) -> dict:

        self.logger.debug("Checking if user exists")
        user: User = self.user_repository.retrieve_record_by_email(
            email=request_dto.email
        )

        if user:

            self.logger.debug("User already exists")
            raise BadInputError(
                responseMessage="Email already registered.",
                responseKey="error_email_already_registered",
                httpStatusCode=HTTPStatus.BAD_REQUEST,
            )

        self.logger.debug("Preparing user data")
        user: User = User(
            urn=str(ULID()),
            email=request_dto.email,
            password=bcrypt.hashpw(
                request_dto.password.encode("utf-8"),
                os.getenv("BCRYPT_SALT").encode("utf8"),
            ).decode("utf8"),
            is_deleted=False,
            created_by=1,
            created_on=datetime.now(),
        )

        user: User = self.user_repository.create_record(record=user)
        self.logger.debug("Preparing user data")

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Successfully registered the user.",
            responseKey="success_user_register",
            data={
                "user_email": user.email,
                "created_at": str(user.created_on),
            },
        )
