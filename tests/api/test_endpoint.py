import pytest
from fastapi import status
from slugify import slugify
from src.common.helpers.error_codes import AppErrorCode


@pytest.mark.asyncio
async def test_create_log_cases(http_client_api, trailhub_data, fake_data):
    # CASE 1: Create a new log with valid data and return 201
    response = await http_client_api.post("/logs", json=trailhub_data)

    response_json = response.json()
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response_json["user_id"] == trailhub_data["user_id"]
    assert response_json["source"] == trailhub_data["source"].lower().replace(" ", "")

    # CASE 2: Create a new log with invalid data and return 422
    trailhub_data.update({"user_id": fake_data.random_int()})
    response = await http_client_api.post("/logs", json=trailhub_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
    assert response.json()["error_code"] == AppErrorCode.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_retrieve_log_cases(http_client_api, create_trailhub):
    # CASE 1: Retrieve log with valid ID and return 200
    trailhub_id = create_trailhub.id
    case_one = await http_client_api.get(f"/logs/{trailhub_id}")
    response_json = case_one.json()
    assert case_one.status_code == status.HTTP_200_OK, case_one.text
    assert response_json["_id"] == str(trailhub_id)
    assert response_json["user_id"] == create_trailhub.user_id
    assert response_json["source"] == create_trailhub.source

    # CASE 2: Retrieve log with invalid ID and return 422
    case_two = await http_client_api.get("/logs/invalid_id")
    assert case_two.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, case_two.text
    assert case_two.json()["error_code"] == AppErrorCode.UNPROCESSABLE_ENTITY

    # CASE 3: Retrieve log with non-existent ID and return 404
    case_three = await http_client_api.get("/logs/6756f47af9096fa27c21d567")
    assert case_three.status_code == status.HTTP_404_NOT_FOUND, case_three.text
    assert case_three.json()["error_code"] == AppErrorCode.DOCUMENT_NOT_FOUND
    assert case_three.json()["error_message"] == "Document with '6756f47af9096fa27c21d567' not found."


@pytest.mark.asyncio
@pytest.mark.parametrize("sort", ["asc", "desc"])
async def test_get_logs_cases(http_client_api, create_trailhub, sort):
    # CASE 1: Retrieve all logs and return 200
    case_one = await http_client_api.get("/logs")
    assert case_one.status_code == status.HTTP_200_OK, case_one.text
    assert case_one.json()["total"] >= 1

    # CASE 2: Retrieve logs with filter and return 200
    case_two = await http_client_api.get(
        "/logs", params={
            "source": create_trailhub.source,
            "user_id": create_trailhub.user_id,
        }
    )
    assert case_two.status_code == status.HTTP_200_OK, case_two.text
    assert case_two.json()["total"] >= 1
    assert case_two.json()["items"][0]["source"] == create_trailhub.source
    assert case_two.json()["items"][0]["user_id"] == create_trailhub.user_id

    # CASE 3: Retrieve logs with not existing filter and return 200
    case_three = await http_client_api.get("/logs", params={"source": "invalid_source"})
    assert case_three.status_code == status.HTTP_200_OK, case_three.text
    assert case_three.json()["total"] == 0

    # CASE 4: Retrieve logs with sort and return 200
    case_four = await http_client_api.get("/logs", params={"sort": sort})
    assert case_four.status_code == status.HTTP_200_OK, case_four.text
    assert case_four.json()["total"] >= 1

    # CASE 5: Retrieve logs with created filter and return 200
    case_five = await http_client_api.get(
        "/logs",
        params={
            "user_id": create_trailhub.user_id,
            "created": create_trailhub.created,
            "anonymous": create_trailhub.anonymous
        }
    )
    assert case_five.status_code == status.HTTP_200_OK, case_five.text
    assert case_five.json()["total"] >= 0
