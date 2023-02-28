CREATE TABLE `airline` (
  `airline_name` varchar(50) NOT NULL,
  PRIMARY KEY (`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(30) NOT NULL,
  `airline_name` varchar(30) NOT NULL,
  `password_` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `date_of_birth` varchar(30) NOT NULL,
  PRIMARY KEY (`username`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------

--
-- Table structure for table `permission_status`
--

CREATE TABLE `permission_status` (
  `username` varchar(30) NOT NULL,
  `status` varchar(30) NOT NULL,
  PRIMARY KEY (`username`),
  FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------
--
-- Table structure for table `airport`
--

CREATE TABLE `airport` (
  `airport_name` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  PRIMARY KEY (`airport_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------
--
-- Table structure for table `airplane`
--

CREATE TABLE `airplane` (
  `airplane_id` varchar(30) NOT NULL,
  `airline_name` varchar(30) NOT NULL,
  `num_of_seat` int(10) NOT NULL,
  PRIMARY KEY (`airplane_id`,`airline_name`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

CREATE TABLE `flight` (
  `flight_num` int(10) NOT NULL,
  `airline_name` varchar(30) NOT NULL,
  `departure_time` varchar(20) NOT NULL,
  `arrival_time` varchar(20) NOT NULL,
  `price` int(10) NOT NULL,
  `status_` varchar(10) NOT NULL,
  `airplane_id` varchar(30) NOT NULL,
  `departure_airport_name` varchar(30) NOT NULL,
  `arrival_airport_name` varchar(30) NOT NULL,
  PRIMARY KEY (`flight_num`,`airline_name`),
  FOREIGN KEY (`airplane_id`) REFERENCES `airplane` (`airplane_id`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`),
  FOREIGN KEY (`departure_airport_name`) REFERENCES `airport` (`airport_name`),
  FOREIGN KEY (`arrival_airport_name`) REFERENCES `airport` (`airport_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `customer_email` varchar(30) NOT NULL,
  `name` varchar(20) NOT NULL,
  `password_` varchar(30) NOT NULL,
  `building_number` int(20) NOT NULL,
  `street` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(30) NOT NULL,
  `phone_number` int(50) NOT NULL,
  `passport_number` int(50) NOT NULL,
  `passport_expiration` varchar(30) NOT NULL,
  `passport_country` varchar(30) NOT NULL,
  `date_of_birth` varchar(30) NOT NULL,
  PRIMARY KEY (`customer_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------


--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(20) NOT NULL,
  `flight_num` int(20) NOT NULL,
  `airline_name` varchar(30) NOT NULL,
  `customer_email` varchar(30) ,
  `booking_agent_email` varchar(30),
  PRIMARY KEY (`ticket_id`),
  FOREIGN KEY (`flight_num`) REFERENCES `flight` (`flight_num`),
  FOREIGN KEY (`airline_name`) REFERENCES `flight` (`airline_name`),
  FOREIGN KEY (`customer_email`) REFERENCES `customer` (`customer_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------


--
-- Table structure for table `booking_agent`
--

CREATE TABLE `booking_agent` (
  `booking_agent_email` varchar(30) NOT NULL,
  `agent_password_` varchar(30) NOT NULL,
  `booking_agent_id` int(20) NOT NULL,
  PRIMARY KEY (`booking_agent_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- --------------------------------------------------------



--
-- Table structure for table `works_for`
--

CREATE TABLE `works_for` (
  `airline_name` varchar(30) NOT NULL,
  `booking_agent_email` varchar(30) NOT NULL,
  PRIMARY KEY (`airline_name`,`booking_agent_email`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`),
  FOREIGN KEY (`booking_agent_email`) REFERENCES `booking_agent` (`booking_agent_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

--


