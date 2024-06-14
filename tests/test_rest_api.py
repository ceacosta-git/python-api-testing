import pytest
import requests
import os
import time

"""
These tests are based of a sample set of public RESTful APIs as documented here:
https://gorest.co.in/

This is a basic script for RESTful API testing using the requests and pytest
"""

BASE_URI = "https://gorest.co.in/public/v2"
# VALID_BEARER is an environment variable, the user should generate their own token as documented https://gorest.co.in/
valid_bearer = os.environ.get('VALID_BEARER')

VALID_HEADERS = {"Accept": "application/json",
                 "Content-Type": "application/json",
                 "Authorization": f"Bearer {valid_bearer}"
                 }


test_updated_names = ["update name 1", "update name 2"]


def create_user():
    """
    Creates a user by making a POST request to the /users API.
    This function is meant to be used as a setup method for those test cases that require to have an existing user.
    :returns the response from creating a user
    """
    # The public API used in this exercise does not allow for duplicate emails.
    # I don't own this API so I'm avoiding to delete any records that I did not create.
    unique_number = str(time.time()).replace(".", "")
    email = f"ran{unique_number}@test.com"
    data = {"name": "Some Name",
            "gender": "female",
            "email": email,
            "status": "active"}
    response = requests.post(BASE_URI + "/users", headers=VALID_HEADERS, json=data)
    return response


def delete_user(user_id):
    """
    Deletes a user by making a DELETE request to the /users API
    This function is meant to be used as a cleanup method for those test cases that created a user.
    :param user_id the user id we are trying to delete
    :returns the response from creating a user
    """
    response = requests.delete(BASE_URI + "/users", headers=VALID_HEADERS)
    return response


def test_get_users_ok():
    """
    Sample positive test for a GET request to the /users API.
    """
    response = requests.get(BASE_URI + "/users")
    user_list = response.json()

    assert response.status_code == requests.codes.ok, "GET request is not OK"
    assert len(user_list), "get users did not retrieve users"


def test_get_user_details_user_does_not_exist():
    """
    Sample negative test for a GET request to the /users API.
    """
    non_existing_user_id = 'user_does_not_exist'
    response = requests.get(BASE_URI + f"/users/{non_existing_user_id}")
    response_json = response.json()

    message = response_json.get("message")
    assert response.status_code == requests.codes.not_found, "GET request is not 404"
    assert message == "Resource not found", "Unexpected message when user does not exist."


def test_create_user_success():
    """
    Sample positive test for a POST request to the /users API.
    """
    response = create_user()
    user = response.json()
    id = user.get("id")
    assert response.status_code == requests.codes.created, "create new user response is not 201"
    assert id, "Response did not include id of new user"
    delete_user(id)


def test_create_user_fail_missing_email():
    """
    Sample negative test for a POST request to the /users API.
    """
    data = {"name": "test missing email",
            "gender": "Male",
            "status": "Active"}
    response = requests.post(BASE_URI + "/users", headers=VALID_HEADERS, json=data)
    errors = response.json()

    assert response.status_code == requests.codes.unprocessable_entity,  "create new user with missing email response is not 422"
    assert len(errors) == 1, "Got ore than 1 error"
    field = errors[0].get("field")
    assert field == "email", "Error was not due to email field"
    message = errors[0].get("message")
    assert message == "can't be blank"


def test_delete_user_unauthorized():
    """
    Sample negative test for a DELETE request to the /users API.
    """
    create_response = create_user()
    user = create_response.json()
    user_id = user["data"]["id"]

    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "Authorization": "Bearer INVALID-TOKEN"
               }

    response = requests.delete(BASE_URI + f"/users/{user_id}", headers=headers)
    deleted_user = response.json()
    code = deleted_user["code"]
    assert response.status_code == requests.codes.ok, "POST request is not OK"
    assert code == requests.codes.unauthorized, "delete user with invalid authorization token response is not 401"
    delete_user(user_id)


@pytest.mark.parametrize("new_user_name", test_updated_names)
def test_update_user_success(new_user_name):
    """
     Sample positive data-driven test for a PUT request to the /users API.
    """
    create_response = create_user()
    user = create_response.json()
    user_id = user["data"]["id"]

    data = {"name": new_user_name}
    response = requests.put(BASE_URI + f"/users/{user_id}", headers=VALID_HEADERS, json=data)
    updated_user = response.json()
    code = updated_user["code"]
    assert response.status_code == requests.codes.ok, "PUT request is not OK"
    assert code == requests.codes.ok, "update user response is not 200"
    delete_user(user_id)
