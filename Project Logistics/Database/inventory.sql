-- Minimal baseline schema for `inventory` database
CREATE DATABASE IF NOT EXISTS `inventories` DEFAULT CHARACTER SET = 'utf8mb4';
USE `inventories`;

DROP TABLE IF EXISTS `inventory`;
CREATE TABLE `inventory` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(255) NOT NULL,
  `Category` VARCHAR(255) NOT NULL,
  `Quantity` INT NOT NULL DEFAULT 0,
  `Quantity_Delivered` INT NOT NULL DEFAULT 0,
  `Delivery_Amount` INT NOT NULL DEFAULT 0,
  `Brand` VARCHAR(255) NOT NULL DEFAULT '',
  `Delivered` TINYINT(1) NOT NULL DEFAULT 0,
  `Being_Delivered` TINYINT(1) NOT NULL DEFAULT 0,
  `Deleted` TINYINT(1) NOT NULL DEFAULT 0,
  `Delivered_at` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- deliveries table for persistent delivery records
DROP TABLE IF EXISTS `deliveries`;
CREATE TABLE `deliveries` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `inventory_id` INT,
  `Name` VARCHAR(255),
  `Category` VARCHAR(255),
  `Delivery_Amount` INT,
  `Status` VARCHAR(32),
  `Delivered_at` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 13, 2025 at 04:17 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `inventories`
--

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Category` varchar(255) NOT NULL,
  `Quantity` int(11) NOT NULL,
  `Quantity_Delivered` int(11) NOT NULL DEFAULT 0,
  `Delivery_Amount` int(11) NOT NULL DEFAULT 0,
  `Brand` varchar(255) NOT NULL,
  `Delivered` tinyint(1) NOT NULL DEFAULT 0,
  `Being_Delivered` tinyint(1) NOT NULL DEFAULT 0,
  `Deleted` tinyint(1) NOT NULL DEFAULT 0,
  `Delivered_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Triggers `inventory`
--
DELIMITER $$
CREATE TRIGGER `trg_set_delivered_at` BEFORE UPDATE ON `inventory` FOR EACH ROW BEGIN
    IF NEW.Being_Delivered = 1 AND OLD.Being_Delivered = 0 THEN
        SET NEW.Quantity = OLD.Quantity - NEW.Delivery_Amount;
    END IF;
    IF NEW.Delivered = 1 AND OLD.Delivered = 0 THEN
        SET NEW.Delivered_at = NOW();
        SET NEW.Quantity_Delivered = OLD.Quantity_Delivered + OLD.Delivery_Amount;
        SET NEW.Being_Delivered = 0;
        SET NEW.Delivery_Amount = 0;
    END IF;
END
$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `trg_check_delivery_insert` BEFORE INSERT ON `inventory` FOR EACH ROW
BEGIN
  IF NEW.Quantity < 0 OR NEW.Delivery_Amount < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity and Delivery_Amount must be non-negative';
  END IF;
  IF NEW.Delivery_Amount > NEW.Quantity THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Delivery amount cannot exceed quantity on insert';
  END IF;
END
$$

CREATE TRIGGER `trg_check_delivery_update` BEFORE UPDATE ON `inventory` FOR EACH ROW
BEGIN
  IF NEW.Quantity < 0 OR NEW.Delivery_Amount < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity and Delivery_Amount must be non-negative';
  END IF;
  IF NEW.Delivery_Amount > OLD.Quantity THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Delivery amount cannot exceed current quantity';
  END IF;
END
$$
DELIMITER ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `inventory`
  ADD INDEX (`Category`),
  ADD INDEX (`Being_Delivered`),
  ADD INDEX (`Deleted`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
