from uuid import uuid4


def create_server(client, auth_headers, payload):
    return client.post("/api/v1/servers", json=payload, headers=auth_headers)


def test_empty_server_list(client):
    response = client.get("/api/v1/servers")
    assert response.status_code == 200
    assert response.json() == []


def test_server_creation_and_retrieval(client, auth_headers, server_payload):
    created = create_server(client, auth_headers, server_payload)
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "offline"
    assert body["players"] == 0
    assert client.get(f"/api/v1/servers/{body['id']}").json() == body


def test_duplicate_server_name_rejected(client, auth_headers, server_payload):
    assert create_server(client, auth_headers, server_payload).status_code == 201
    response = create_server(client, auth_headers, server_payload)
    assert response.status_code == 409


def test_invalid_max_players(client, auth_headers, server_payload):
    server_payload["max_players"] = 0
    assert create_server(client, auth_headers, server_payload).status_code == 422


def test_invalid_negative_players(client, auth_headers, server_payload):
    server_id = create_server(client, auth_headers, server_payload).json()["id"]
    response = client.patch(
        f"/api/v1/servers/{server_id}", json={"players": -1}, headers=auth_headers
    )
    assert response.status_code == 422


def test_players_over_capacity_rejected(client, auth_headers, server_payload):
    server_id = create_server(client, auth_headers, server_payload).json()["id"]
    response = client.patch(
        f"/api/v1/servers/{server_id}", json={"players": 129}, headers=auth_headers
    )
    assert response.status_code == 422


def test_status_update(client, auth_headers, server_payload):
    server_id = create_server(client, auth_headers, server_payload).json()["id"]
    response = client.patch(
        f"/api/v1/servers/{server_id}",
        json={"status": "online", "players": 37},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["players"] == 37


def test_write_operations_require_authentication(client, auth_headers, server_payload):
    assert client.post("/api/v1/servers", json=server_payload).status_code == 401
    server_id = create_server(client, auth_headers, server_payload).json()["id"]
    assert client.patch(f"/api/v1/servers/{server_id}", json={"players": 1}).status_code == 401
    assert client.delete(f"/api/v1/servers/{server_id}").status_code == 401


def test_server_deletion(client, auth_headers, server_payload):
    server_id = create_server(client, auth_headers, server_payload).json()["id"]
    response = client.delete(f"/api/v1/servers/{server_id}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/api/v1/servers/{server_id}").status_code == 404


def test_nonexistent_server_returns_404(client, auth_headers):
    server_id = uuid4()
    assert client.get(f"/api/v1/servers/{server_id}").status_code == 404
    assert (
        client.patch(
            f"/api/v1/servers/{server_id}", json={"status": "online"}, headers=auth_headers
        ).status_code
        == 404
    )
    assert client.delete(f"/api/v1/servers/{server_id}", headers=auth_headers).status_code == 404


def test_invalid_status_and_empty_patch(client, auth_headers, server_payload):
    server_id = create_server(client, auth_headers, server_payload).json()["id"]
    assert (
        client.patch(
            f"/api/v1/servers/{server_id}", json={"status": "broken"}, headers=auth_headers
        ).status_code
        == 422
    )
    assert (
        client.patch(f"/api/v1/servers/{server_id}", json={}, headers=auth_headers).status_code
        == 422
    )
