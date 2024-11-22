-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 22, 2024 at 05:39 PM
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
-- Database: `car_showroom`
--

-- --------------------------------------------------------

--
-- Table structure for table `bike`
--

CREATE TABLE `bike` (
  `bike_id` int(11) NOT NULL,
  `vehicle_id` int(11) DEFAULT NULL,
  `image` blob DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `car`
--

CREATE TABLE `car` (
  `car_id` int(11) NOT NULL,
  `vehicle_id` int(11) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `car`
--

INSERT INTO `car` (`car_id`, `vehicle_id`, `image`) VALUES
(13, 13, 'car11.jpg'),
(14, 14, 'car4.jpg'),
(15, 15, 'car7.jpg'),
(16, 16, 'car10.jpg'),
(17, 17, 'car9.jpg'),
(18, 18, 'car8.png'),
(19, 19, 'car12.jpg'),
(20, 20, 'car13.jpg'),
(21, 21, 'car16.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `inquiry`
--

CREATE TABLE `inquiry` (
  `inquiry_id` int(11) NOT NULL,
  `vehicle_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `inquiry_text` text DEFAULT NULL,
  `inquiry_date` date DEFAULT NULL,
  `reply` text DEFAULT NULL,
  `reply_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `inquiry`
--

INSERT INTO `inquiry` (`inquiry_id`, `vehicle_id`, `user_id`, `inquiry_text`, `inquiry_date`, `reply`, `reply_date`) VALUES
(6, 19, 2, 'Kia haal hain', '2024-11-22', 'alhamdulilah ', '2024-11-22');

-- --------------------------------------------------------

--
-- Table structure for table `installment`
--

CREATE TABLE `installment` (
  `installment_id` int(11) NOT NULL,
  `vehicle_id` int(11) DEFAULT NULL,
  `downpayment` decimal(10,2) DEFAULT NULL,
  `monthly_installment` decimal(10,2) DEFAULT NULL,
  `interest_rate` decimal(5,2) DEFAULT NULL,
  `total_price` decimal(10,2) DEFAULT NULL,
  `bank_name` varchar(100) DEFAULT NULL,
  `time_period` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `installment`
--

INSERT INTO `installment` (`installment_id`, `vehicle_id`, `downpayment`, `monthly_installment`, `interest_rate`, `total_price`, `bank_name`, `time_period`) VALUES
(1, 15, 300000.00, 22645.00, 5.00, 1658755.00, 'Global Auto Financing ', 60),
(2, 15, 150000.00, 23873.00, 6.00, 1878090.00, 'Prime Auto Lenders', 72);

-- --------------------------------------------------------

--
-- Table structure for table `testdrive`
--

CREATE TABLE `testdrive` (
  `testdrive_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `vehicle_id` int(11) DEFAULT NULL,
  `test_drive_date` date DEFAULT NULL,
  `test_drive_time` time DEFAULT NULL,
  `status` enum('Pending','Scheduled','Rejected') DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `user_name` varchar(100) NOT NULL,
  `ph_number` varchar(15) DEFAULT NULL,
  `user_type` varchar(50) DEFAULT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`user_id`, `email`, `user_name`, `ph_number`, `user_type`, `password`) VALUES
(1, 'admin123@gmail.com', 'admin', '123456', 'admin', 'scrypt:32768:8:1$FH6PqpTTfPrKTqWr$636f9e4f3c6a22e63a0f3391b11d9108dcf3be2932b0099ec14a8d6a932cfb127847e66b49523a3fcbbb9d1d20e6f47ba97e7c126391ecba5c327cdf08f91e64'),
(2, 'omerkham12345@gmail.com', 'omer', '123456', 'user', 'scrypt:32768:8:1$AQjtcnvxIkiZSDx1$d260ff503db27c52c61bef635101bd8c7c8200654778d61fb1b1f41f37ca115fa0636c5b7c7d72a47b8528211348a6c945cf43a0675f5fdddbbce1fdf3fbddf1'),
(3, 'hamzachacho@gmail.com', 'hamza', '03362144060', 'user', 'scrypt:32768:8:1$w4ZKq6w6CoVnw13B$7407a6d72a564a5861070653cd9b033c8ca0463a0477b78b6c941fe22e89b7235048e0e83ff3551a32452ef83b35779b22553673f47d4f16207c834aa2838785'),
(4, 'salik@gmsil.com', 'salik', '03362144060', 'user', 'scrypt:32768:8:1$g7HBBGvXPHl0LMs2$416ccbe1be8257c393b3ce9896e0b214d82e0f9068b5a22f1ed6ee612c3ab472e7ee98ad85681f276d7c46b51ed737ded080e5feccd52dfefa4e6a4ac4ffe06a'),
(5, 'muhibsiddiqui25@gmail.com', 'Muhib ', '000000', 'user', 'scrypt:32768:8:1$oeAdrYfcfeyXqpHR$dcfc6ae77177bbf103b8dbc15fd0d4b117a7ceb493e412fcf4548c93150d267e20ed253e90604975733626f832b74730a743bf6e776febb7919c0ea6806076ef'),
(7, 'hamza@showroom', 'chacho', '03362144060', 'user', 'scrypt:32768:8:1$253f1zlHfsi3tkDC$c1c38c5df179719dca9d0048cd70de71b095b9f75c1777ae3249582356b898b80c9479f059b1da4fe5f6dae07a22439e8987a547f2e330ee8495eb10bc72f879');

-- --------------------------------------------------------

--
-- Table structure for table `vehicle`
--

CREATE TABLE `vehicle` (
  `vehicle_id` int(11) NOT NULL,
  `make` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `vehicle_type` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `vehicle`
--

INSERT INTO `vehicle` (`vehicle_id`, `make`, `model`, `year`, `price`, `description`, `vehicle_type`) VALUES
(13, 'Honda', 'Civic Type R', 2018, 32000.00, 'The Honda Civic Type R is a high-performance hatchback that boasts a turbocharged 2.0-liter engine, delivering impressive horsepower and precision handling. Celebrated for its aggressive design and track-inspired engineering, it combines everyday practicality with thrilling driving dynamics.', 'Car/Sedan'),
(14, 'Rolls Royce', 'Ghost', 2023, 320000.00, 'The car has a 6.6-litre V12 engine which delivers a maximum power of 603 hp (450 kW) @ 5,250 rpm and a maximum torque of 620 lb⋅ft (841 N⋅m) @ 1,650 – 5,000 rpm. The car can accelerate from 0 to 100 km/h (62 mph) in 4.8 s and has a top speed of 250 km/h (155 mph). Its power-to-weight ratio is 176.3 W/kg.', 'Car/Sedan'),
(15, 'Ferrari', 'Laferrari', 2013, 1500000.00, 'The LaFerrari is a limited-production hybrid hypercar by Ferrari, blending cutting-edge technology with a V12 engine and electric motor to deliver over 950 horsepower. It epitomizes Italian craftsmanship, pushing the boundaries of speed and luxury.', 'Car/Sport'),
(16, 'Rolls Royce', 'Phantom', 2019, 410000.00, 'The Rolls-Royce Phantom is the pinnacle of luxury sedans, featuring a powerful V12 engine and unparalleled craftsmanship. Known for its opulent interior and smooth, whisper-quiet ride, it sets the standard for comfort and prestige in automotive excellence.', 'Car/Sedan'),
(17, 'Porche', '911 Turbo S', 2023, 350000.00, 'The Porsche 911 992 Turbo S is a high-performance sports car that features a twin-turbocharged flat-six engine, delivering 640 horsepower and exceptional acceleration. Renowned for its blend of luxury, precision handling, and everyday usability, it represents the pinnacle of the 911 lineup.', 'Car/Sport'),
(18, 'Mclaren', 'P1', 2013, 1400000.00, 'The McLaren P1 is a pioneering hybrid hypercar that merges a twin-turbo V8 engine with an electric motor, producing a combined output of 903 horsepower. Designed for maximum performance, it embodies McLaren\'s legacy of innovation and track-ready engineering.', 'Car/Sport'),
(19, 'BMW', 'M5 Competition', 2019, 78000.00, 'The 2019 BMW M5 Competition is a high-performance sports sedan that boasts a 617-horsepower twin-turbo V8 engine, offering exhilarating speed and precision handling. With a refined, aggressive design and advanced technology, it delivers an exceptional driving experience.', 'Car/Sedan'),
(20, 'Toyota', 'Land Cruiser', 2023, 92000.00, 'The 2023 Toyota Land Cruiser is known for its rugged off-road capabilities and luxurious interior. It combines powerful performance with advanced safety features, making it ideal for both adventure and comfort.', 'Car/SUV'),
(21, 'Toyota', 'Supra', 2022, 45000.00, ' The 2022 Toyota Supra is a sleek sports car that combines iconic design with a powerful turbocharged engine, delivering up to 382 horsepower. Its sharp handling, advanced tech features, and luxurious interior make it a thrill to drive on road or track.', 'Car/Coupe');

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `fav_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `vehicle_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wishlist`
--

INSERT INTO `wishlist` (`fav_id`, `user_id`, `vehicle_id`) VALUES
(2, 2, 15);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bike`
--
ALTER TABLE `bike`
  ADD PRIMARY KEY (`bike_id`),
  ADD UNIQUE KEY `vehicle_id` (`vehicle_id`);

--
-- Indexes for table `car`
--
ALTER TABLE `car`
  ADD PRIMARY KEY (`car_id`),
  ADD UNIQUE KEY `vehicle_id` (`vehicle_id`);

--
-- Indexes for table `inquiry`
--
ALTER TABLE `inquiry`
  ADD PRIMARY KEY (`inquiry_id`),
  ADD KEY `vehicle_id` (`vehicle_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `installment`
--
ALTER TABLE `installment`
  ADD PRIMARY KEY (`installment_id`),
  ADD KEY `vehicle_id` (`vehicle_id`);

--
-- Indexes for table `testdrive`
--
ALTER TABLE `testdrive`
  ADD PRIMARY KEY (`testdrive_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `vehicle_id` (`vehicle_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `vehicle`
--
ALTER TABLE `vehicle`
  ADD PRIMARY KEY (`vehicle_id`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`fav_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `vehicle_id` (`vehicle_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bike`
--
ALTER TABLE `bike`
  MODIFY `bike_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `car`
--
ALTER TABLE `car`
  MODIFY `car_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `inquiry`
--
ALTER TABLE `inquiry`
  MODIFY `inquiry_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `installment`
--
ALTER TABLE `installment`
  MODIFY `installment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `vehicle`
--
ALTER TABLE `vehicle`
  MODIFY `vehicle_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `fav_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bike`
--
ALTER TABLE `bike`
  ADD CONSTRAINT `bike_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`vehicle_id`);

--
-- Constraints for table `car`
--
ALTER TABLE `car`
  ADD CONSTRAINT `car_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`vehicle_id`) ON DELETE CASCADE;

--
-- Constraints for table `inquiry`
--
ALTER TABLE `inquiry`
  ADD CONSTRAINT `inquiry_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`vehicle_id`),
  ADD CONSTRAINT `inquiry_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `installment`
--
ALTER TABLE `installment`
  ADD CONSTRAINT `installment_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`vehicle_id`);

--
-- Constraints for table `testdrive`
--
ALTER TABLE `testdrive`
  ADD CONSTRAINT `testdrive_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`),
  ADD CONSTRAINT `testdrive_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`vehicle_id`);

--
-- Constraints for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`),
  ADD CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`vehicle_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
