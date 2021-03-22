import pytest
import requests
import random

"""
These tests are based of a sample set of public RESTful APIs as documented here:
https://gorest.co.in/

This is a basic script for RESTful API testing using the requests and pytest
"""

BASE_URI = "https://gorest.co.in/public-api"
# ToDo: VALID_BEARER is a placeholder, the user should generate their own token as documented https://gorest.co.in/
VALID_HEADERS = {"Accept": "application/json",
                 "Content-Type": "application/json",
                 "Authorization": "Bearer VALID_BEARER"
                 }

test_updated_names = ["update name 1", "update name 2"]


def create_user():
    """
    Creates a user by making a POST request to the /users API.
    This function is meant to be used as a setup method for those test cases that require to have an existing user.
    :returns the response from creating a user
    """
    # ToDo: find a better strategy for generating unique emails.
    # The public API used in this exercise does not allow for duplicate emails.
    # I don't own this API so I'm avoiding to delete any records that I did not create.
    random_number = random.randint(1, 9999)
    email = f"ran{random_number}@test.com"
    data = {"name": "test update user",
            "email": email,
            "gender": "Male",
            "status": "Active"}
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
    user = response.json()
    code = user["code"]
    user_list = user["data"]
    assert response.status_code == 200, "GET request is not OK"
    assert code == requests.codes.ok, "get user response is not OK"


def test_get_user_details_user_does_not_exist():
    """
    Sample negative test for a GET request to the /users API.
    """
    response = requests.get(BASE_URI + "/users/10000000")
    user = response.json()
    code = user["code"]
    message = user["data"]["message"]
    assert response.status_code == requests.codes.ok, "GET request is not OK"
    assert code == requests.codes.not_found, "get a non existent user response is not 404"
    assert message == "Resource not found", "Unexpected message when user does not exist."


def test_create_user_success():
    """
    Sample positive test for a POST request to the /users API.
    """
    response = create_user()
    user = response.json()
    code = user["code"]
    id = user["data"]["id"]
    assert code == requests.codes.created, "create new user response is not 201"
    delete_user(id)


def test_create_user_fail_missing_email():
    """
    Sample negative test for a POST request to the /users API.
    """
    data = {"name": "test missing email",
            "gender": "Male",
            "status": "Active"}
    response = requests.post(BASE_URI + "/users", headers=VALID_HEADERS, json=data)
    user = response.json()
    code = user["code"]
    assert response.status_code == requests.codes.ok, "POST request is not OK"
    assert code == requests.codes.unprocessable_entity, "create new user with missing email response is not 422"


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
