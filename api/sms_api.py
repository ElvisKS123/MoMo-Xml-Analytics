import json
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

transactions = []

class SMSRequestHandler(BaseHTTPRequestHandler):
    
    VALID_CREDENTIALS = {"admin": "password123"}
    
    def authenticate(self):
        auth_header = self.headers.get('Authorization')
        
        if not auth_header:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="SMS Transactions API"')
            self.end_headers()
            return False
        
        try:
            auth_type, credentials = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                raise ValueError()
                
            decoded_credentials = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            if username not in self.VALID_CREDENTIALS or self.VALID_CREDENTIALS[username] != password:
                raise ValueError()
                
            return True
            
        except:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="SMS Transactions API"')
            self.end_headers()
            return False
    
    def do_GET(self):
        if not self.authenticate():
            return
            
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if len(path_parts) == 1 and path_parts[0] == 'transactions':
            self.get_all_transactions()
        elif len(path_parts) == 2 and path_parts[0] == 'transactions' and path_parts[1].isdigit():
            transaction_id = int(path_parts[1])
            self.get_transaction(transaction_id)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if not self.authenticate():
            return
            
        if self.path == '/transactions':
            self.create_transaction()
        else:
            self.send_error(404)
    
    def do_PUT(self):
        if not self.authenticate():
            return
            
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if len(path_parts) == 2 and path_parts[0] == 'transactions' and path_parts[1].isdigit():
            transaction_id = int(path_parts[1])
            self.update_transaction(transaction_id)
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        if not self.authenticate():
            return
            
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if len(path_parts) == 2 and path_parts[0] == 'transactions' and path_parts[1].isdigit():
            transaction_id = int(path_parts[1])
            self.delete_transaction(transaction_id)
        else:
            self.send_error(404)
    
    def get_all_transactions(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        transactions_with_ids = []
        for i, transaction in enumerate(transactions):
            transaction_with_id = transaction.copy()
            transaction_with_id['id'] = i
            transactions_with_ids.append(transaction_with_id)
            
        self.wfile.write(json.dumps(transactions_with_ids).encode())
    
    def get_transaction(self, transaction_id):
        if transaction_id < 0 or transaction_id >= len(transactions):
            self.send_error(404)
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        transaction = transactions[transaction_id].copy()
        transaction['id'] = transaction_id
        self.wfile.write(json.dumps(transaction).encode())
    
    def create_transaction(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400)
            return
        
        try:
            post_data = self.rfile.read(content_length)
            new_transaction = json.loads(post_data.decode('utf-8'))
            
            required_fields = ['address', 'body', 'transaction_type']
            for field in required_fields:
                if field not in new_transaction:
                    self.send_error(400)
                    return
            
            transactions.append(new_transaction)
            transaction_id = len(transactions) - 1
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "message": "Transaction created successfully",
                "id": transaction_id
            }
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            self.send_error(400)
    
    def update_transaction(self, transaction_id):
        if transaction_id < 0 or transaction_id >= len(transactions):
            self.send_error(404)
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400)
            return
        
        try:
            put_data = self.rfile.read(content_length)
            updated_data = json.loads(put_data.decode('utf-8'))
            
            transactions[transaction_id].update(updated_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "message": "Transaction updated successfully",
                "id": transaction_id
            }
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            self.send_error(400)
    
    def delete_transaction(self, transaction_id):
        if transaction_id < 0 or transaction_id >= len(transactions):
            self.send_error(404)
            return
        
        deleted_transaction = transactions.pop(transaction_id)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "Transaction deleted successfully",
            "id": transaction_id
        }
        self.wfile.write(json.dumps(response).encode())

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SMSRequestHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
