import logging
from typing import List, Type

from beanie import Document, init_beanie
from fastapi import FastAPI

from .mongo_client import config_mongodb_client

logging.basicConfig(format="%(message)s", level=logging.INFO, force=True)
_log = logging.getLogger(__name__)


async def startup_db_client(
    app: FastAPI, mongodb_uri: str, database_name: str, document_models: List[Type[Document]]
) -> None:
    """
    Initialize the database client and document models for the application and store the client in the app object for
    later use in the application.

    :param app: Instance of the FastAPI application to store the database client.
    :type app: FastAPI
    :param mongodb_uri: URI of the MongoDB database.
    :type mongodb_uri: str
    :param database_name: Name of the database.
    :type database_name: str
    :param document_models: List of document models to initialize for the application.
    :type document_models: List[Type[Document]]
    :return: None
    :rtype: None
    """
    client = await config_mongodb_client(mongodb_uri=mongodb_uri)
    if app:
        app.mongo_db_client = client

    await init_beanie(database=client[database_name], document_models=document_models, multiprocessing_mode=True)
    _log.info("==> Database init successfully !")


async def shutdown_db_client(app: FastAPI) -> None:
    """
    Close the database client when the application is shutting down.

    :param app: Instance of the FastAPI application to close the database client.
    :type app: FastAPI
    :return: None
    :rtype: None
    """
    app.mongo_db_client.close()
    _log.info("==> Database closed successfully !")
