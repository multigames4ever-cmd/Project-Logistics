-- Create locations table for delivery routes in the Philippines
CREATE TABLE IF NOT EXISTS `locations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `delivery_id` INT DEFAULT NULL,
  `origin` VARCHAR(100) NOT NULL,
  `destination` VARCHAR(100) NOT NULL,
  `current_location` VARCHAR(100) DEFAULT NULL,
  `distance_km` DECIMAL(10,2) DEFAULT NULL,
  `estimated_hours` DECIMAL(5,2) DEFAULT NULL,
  `departure_time` DATETIME DEFAULT NULL,
  `estimated_arrival` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `delivery_id` (`delivery_id`),
  CONSTRAINT `locations_ibfk_1` FOREIGN KEY (`delivery_id`) REFERENCES `deliveries` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Philippine locations data with multiple routes from Nasugbu and other cities
INSERT INTO `locations` (`origin`, `destination`, `distance_km`, `estimated_hours`) VALUES
-- From Nasugbu to various cities
('Nasugbu, Batangas', 'Manila, Metro Manila', 110.5, 2.5),
('Nasugbu, Batangas', 'Quezon City, Metro Manila', 125.0, 3.0),
('Nasugbu, Batangas', 'Makati City, Metro Manila', 115.0, 2.8),
('Nasugbu, Batangas', 'Taguig City, Metro Manila', 120.0, 2.9),
('Nasugbu, Batangas', 'Pasig City, Metro Manila', 130.0, 3.2),
('Nasugbu, Batangas', 'Tagaytay City, Cavite', 45.0, 1.0),
('Nasugbu, Batangas', 'Batangas City, Batangas', 55.0, 1.2),
('Nasugbu, Batangas', 'Calamba, Laguna', 85.0, 2.0),

-- Manila to various cities
('Manila, Metro Manila', 'Quezon City, Metro Manila', 15.2, 0.5),
('Manila, Metro Manila', 'Makati City, Metro Manila', 12.0, 0.4),
('Manila, Metro Manila', 'Cebu City, Cebu', 570.0, 1.5),
('Manila, Metro Manila', 'Davao City, Davao del Sur', 980.0, 2.0),
('Manila, Metro Manila', 'Baguio City, Benguet', 250.0, 5.0),
('Manila, Metro Manila', 'Angeles City, Pampanga', 83.0, 1.5),
('Manila, Metro Manila', 'Tagaytay City, Cavite', 59.0, 1.5),
('Manila, Metro Manila', 'Batangas City, Batangas', 110.0, 2.3),

-- Other major routes
('Makati City, Metro Manila', 'Taguig City, Metro Manila', 8.5, 0.3),
('Makati City, Metro Manila', 'Quezon City, Metro Manila', 18.0, 0.6),
('Quezon City, Metro Manila', 'Pasig City, Metro Manila', 12.5, 0.4),
('Bacolod City, Negros Occidental', 'Iloilo City, Iloilo', 110.0, 2.0),
('Caloocan City, Metro Manila', 'Valenzuela City, Metro Manila', 12.0, 0.5),
('Calamba, Laguna', 'Manila, Metro Manila', 54.0, 1.3),
('Batangas City, Batangas', 'Lipa City, Batangas', 24.0, 0.5);
