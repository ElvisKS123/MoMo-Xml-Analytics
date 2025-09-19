CREATE DATABASE IF NOT EXISTS momo_analytics;
USE momo_analytics;

-- User
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(60) NOT NULL,
  last_name VARCHAR(60) NOT NULL,
  category ENUM('sender','receiver') NOT NULL,
  phone VARCHAR(20) NOT NULL
);

-- Transaction
CREATE TABLE transactions (
  transaction_id INT AUTO_INCREMENT PRIMARY KEY,
  amount DECIMAL(12,2) NOT NULL CHECK (amount>0),
  category VARCHAR(40) NOT NULL,
  time DATETIME NOT NULL
);

-- Send/Receive (junction)
CREATE TABLE user_transactions (
  transaction_id INT NOT NULL,
  user_id INT NOT NULL,
  role ENUM('sender','receiver') NOT NULL,
  PRIMARY KEY (transaction_id,user_id,role),
  CONSTRAINT foreign_key_user_transactions_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
  CONSTRAINT foreign_key_user_transactions_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- System logs (track)
CREATE TABLE system_logs (
  system_log_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  log VARCHAR(50) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT foreign_key_system_logs_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Indexes
CREATE INDEX index_transactions_time ON transactions(time);
CREATE INDEX index_users_phone ON users(phone);
CREATE INDEX index_user_transactions_user ON user_transactions(user_id);

-- Sample data
INSERT INTO users(first_name,last_name,category,phone) VALUES
 ('Alice','Kay','sender','+250700000001'),
 ('Bob','Lee','receiver','+250700000002'),
 ('Cida','Mo','sender','+250700000003'),
 ('Dan','Poe','receiver','+250700000004'),
 ('Eve','Qi','sender','+250700000005');

INSERT INTO transactions(amount,category,time) VALUES
 (1500.00,'deposit','2025-09-15 10:00'),
 (25.50,'pay','2025-09-16 11:00'),
 (80.00,'bills','2025-09-17 12:00'),
 (5.00,'airtime','2025-09-18 13:00'),
 (100.00,'transfer','2025-09-19 14:00');

INSERT INTO user_transactions(transaction_id,user_id,role) VALUES
 (1,1,'sender'),
 (1,2,'receiver'),
 (2,1,'sender'),
 (2,3,'receiver'),
 (5,4,'sender'),
 (5,5,'receiver');

INSERT INTO system_logs(user_id,log) VALUES (1,'success'),(2,'warning'),(3,'error');

-- Verify
SELECT t.transaction_id,t.amount,t.category,t.time,
 s.first_name AS sender_first,r.first_name AS receiver_first
FROM transactions t
LEFT JOIN user_transactions uts ON uts.transaction_id=t.transaction_id AND uts.role='sender'
LEFT JOIN users s ON s.user_id=uts.user_id
LEFT JOIN user_transactions utr ON utr.transaction_id=t.transaction_id AND utr.role='receiver'
LEFT JOIN users r ON r.user_id=utr.user_id
ORDER BY t.time DESC LIMIT 5;
