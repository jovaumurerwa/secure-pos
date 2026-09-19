import pytest
from sqlalchemy.exc import IntegrityError


def test_issue_receipt_success(client, make_sale):
    sale = make_sale()

    response = client.post(
        f"/receipts/sale/{sale['sale_id']}", json={"copy_type": "Customer Copy"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] == sale["sale_id"]
    assert body["copy_type"] == "Customer Copy"
    assert body["print_status"] == "Printed"
    assert body["receipt_number"] == sale["sale_number"].replace("SALE-", "RCPT-")
    assert "receipt_id" in body


def test_issue_receipt_nonexistent_sale_returns_404(client):
    response = client.post("/receipts/sale/999999", json={"copy_type": "Reprint"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"


def test_issue_duplicate_receipt_for_same_sale_raises_integrity_error(client, make_sale):
    sale = make_sale()
    first = client.post(f"/receipts/sale/{sale['sale_id']}", json={})
    assert first.status_code == 201

    with pytest.raises(IntegrityError):
        client.post(f"/receipts/sale/{sale['sale_id']}", json={})


def test_list_receipts_returns_all_created(client, make_sale):
    sale_a = make_sale()
    sale_b = make_sale()
    client.post(f"/receipts/sale/{sale_a['sale_id']}", json={})
    client.post(f"/receipts/sale/{sale_b['sale_id']}", json={})

    response = client.get("/receipts/")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_receipt_success(client, make_sale):
    sale = make_sale()
    receipt = client.post(f"/receipts/sale/{sale['sale_id']}", json={}).json()

    response = client.get(f"/receipts/{receipt['receipt_id']}")

    assert response.status_code == 200
    assert response.json()["receipt_id"] == receipt["receipt_id"]


def test_get_receipt_not_found_returns_404(client):
    response = client.get("/receipts/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"


def test_update_receipt_success(client, make_sale):
    sale = make_sale()
    receipt = client.post(f"/receipts/sale/{sale['sale_id']}", json={}).json()

    response = client.put(
        f"/receipts/{receipt['receipt_id']}", json={"print_status": "Reprinted"}
    )

    assert response.status_code == 200
    assert response.json()["print_status"] == "Reprinted"


def test_update_receipt_not_found_returns_404(client):
    response = client.put("/receipts/999999", json={"print_status": "Reprinted"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"
