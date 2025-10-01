**Base url**
http://localhost:8000

**Authentication**
All endpoints require Basic Authentication.
Username: admin
Password: password123

**Endpoints**
1. **GET /transactions**
   **Description**: List all SMS transactions

**Request Example:**
GET /transactions
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=

**Response Example:**
json
[
  {
    "id": 0,
    "address": "M-Money",
    "date": "1715351458724",
    "readable_date": "10 May 2024 4:30:58 PM",
    "body": "You have received 2000 RWF from Jane Smith...",
    "transaction_type": "RECEIVED",
    "amount": 2000.0,
    "sender": "Jane Smith",
    "recipient": null,
    "contact_name": "(Unknown)"
  },
  {
    "id": 1,
    "address": "M-Money",
    "date": "1715351506754",
    "readable_date": "10 May 2024 4:31:46 PM",
    "body": "TxId: 73214484437. Your payment of 1,000 RWF...",
    "transaction_type": "PAYMENT",
    "amount": 1000.0,
    "sender": null,
    "recipient": "Jane Smith",
    "contact_name": "(Unknown)"
  }
]
2. **GET /transactions/{id}**

Description: Get a specific transaction by ID

Request Example:

http
GET /transactions/0
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
Response Example:

json
{
  "id": 0,
  "address": "M-Money",
  "date": "1715351458724",
  "readable_date": "10 May 2024 4:30:58 PM",
  "body": "You have received 2000 RWF from Jane Smith...",
  "transaction_type": "RECEIVED",
  "amount": 2000.0,
  "sender": "Jane Smith",
  "recipient": null,
  "contact_name": "(Unknown)"
}
3. **POST /transactions**
**Description**: Create a new transaction

Request Example:
POST /transactions
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
Content-Type: application/json

{
  "address": "M-Money",
  "date": "1715369560245",
  "readable_date": "10 May 2024 9:32:40 PM",
  "body": "New transaction body here...",
  "transaction_type": "PAYMENT",
  "amount": 500.0,
  "sender": null,
  "recipient": "John Doe",
  "contact_name": "(Unknown)"
}
**Response Example:**
json
{
  "message": "Transaction created successfully",
  "id": 2
}
4. **PUT /transactions/{id}**
Description: Update an existing transaction

Request Example:PUT /transactions/0
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
Content-Type: application/json

{
  "amount": 2500.0,
  "sender": "Updated Sender Name"
}

**Response Example:**
json
{
  "message": "Transaction updated successfully",
  "id": 0
}
5. **DELETE /transactions/{id}**
Description: Delete a transaction

**Request Example:**
DELETE /transactions/0
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=

**Response Example:**
{
  "message": "Transaction deleted successfully",
  "id": 0
}

**Error Codes**

**400 - Bad Request**

Missing required fields in POST request

Invalid JSON format in request body

Empty request body where content is required

**401 - Unauthorized**

Missing Authorization header

Invalid username or password

No authentication credentials provided

Incorrect Basic Auth format

**404 - Not Found**

Transaction ID doesn't exist

Invalid endpoint URL

Resource not found

**500 - Internal Server Error**

Server-side processing error

Database connection issues

Unexpected server errors

## Testing
Correct Credentials
<img width="1601" height="596" alt="image" src="https://github.com/user-attachments/assets/598e35d2-ad61-40a7-948c-2d43a02f2492" />


Get API

<img width="1680" height="467" alt="image" src="https://github.com/user-attachments/assets/c7c1e16d-cfe3-4e45-bad0-d8c27d291b3b" />
Wrong credentials
<img width="1156" height="367" alt="image" src="https://github.com/user-attachments/assets/1d954115-6c1c-4608-9448-defe49f444fd" />



Post API
<img width="1169" height="345" alt="image" src="https://github.com/user-attachments/assets/c12eef15-932d-45eb-9565-482913212839" />

PUT Api
<img width="1180" height="199" alt="image" src="https://github.com/user-attachments/assets/927b385a-1fd2-431a-9e36-06a86d66efda" />

DELETE API
<img width="975" height="106" alt="image" src="https://github.com/user-attachments/assets/33938732-bde8-44ed-ae98-444cfcb7b5f6" />

## Data structures and algolithm 
<img width="842" height="487" alt="image" src="https://github.com/user-attachments/assets/0e4261d9-e2ed-43ea-b312-7d25e3240bc6" />
