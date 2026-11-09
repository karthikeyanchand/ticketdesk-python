def test_customer_sees_only_own_tickets(client, acme_customer):
    tickets = client.get("/tickets", headers=acme_customer).json()
    assert tickets and all(t["org_id"] == tickets[0]["org_id"] for t in tickets)


def test_create_and_comment(client, acme_customer, acme_agent):
    t = client.post("/tickets", headers=acme_customer, json={"subject": "VPN drops", "tags": ["vpn", "Network"]})
    assert t.status_code == 201
    tid = t.json()["id"]
    assert t.json()["tags"] == "network,vpn"
    c = client.post(f"/tickets/{tid}/comments", headers=acme_agent, json={"body": "On it", "internal": False})
    assert c.status_code == 201
    comments = client.get(f"/tickets/{tid}/comments", headers=acme_customer).json()
    assert [x["body"] for x in comments] == ["On it"]


def test_customer_cannot_see_internal_comments(client, acme_customer):
    tid = client.get("/tickets", headers=acme_customer).json()[-1]["id"]
    bodies = [c["body"] for c in client.get(f"/tickets/{tid}/comments", headers=acme_customer).json()]
    assert not any(b.startswith("Internal:") for b in bodies)


def test_customer_cannot_update_ticket(client, acme_customer):
    tid = client.get("/tickets", headers=acme_customer).json()[0]["id"]
    assert client.patch(f"/tickets/{tid}", headers=acme_customer, json={"priority": "urgent"}).status_code == 403


def test_search_is_scoped(client, acme_agent):
    results = client.get("/tickets/search", params={"q": "Invoice"}, headers=acme_agent).json()
    assert results and all("(acme)" in t["subject"] for t in results)


def test_reports(client, acme_agent):
    rows = client.get("/reports/sla", params={"sort": "urgent"}, headers=acme_agent).json()
    assert rows and "open_tickets" in rows[0]
    assert client.get("/reports/volume", params={"days": 7}, headers=acme_agent).status_code == 200


def test_admin_endpoints_need_admin(client, acme_agent, acme_admin):
    assert client.get("/admin/users", headers=acme_agent).status_code == 403
    assert client.get("/admin/users", headers=acme_admin).status_code == 200


def test_export_csv(client, acme_admin):
    resp = client.get("/admin/export/tickets.csv", headers=acme_admin)
    assert resp.status_code == 200
    assert resp.text.splitlines()[0].startswith("id,subject,status")


def test_settings_import_rejects_unknown_keys(client, acme_admin):
    ok = client.post("/admin/import/settings", headers={**acme_admin, "Content-Type": "application/x-yaml"},
                     content="auto_close_days: 7\n")
    assert ok.status_code == 200 and ok.json()["settings"] == {"auto_close_days": 7}
    bad = client.post("/admin/import/settings", headers={**acme_admin, "Content-Type": "application/x-yaml"},
                      content="evil: 1\n")
    assert bad.status_code == 400


def test_portal_page_renders(client):
    client.post("/auth/login", json={"email": "cust@acme.example.com", "password": "correct-horse-battery"})
    resp = client.get("/portal/tickets/1")
    assert resp.status_code == 200
    assert "<h1>#1" in resp.text
