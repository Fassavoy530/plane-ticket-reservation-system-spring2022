-- Q1
INSERT INTO `airline` (`airline_name`) VALUES ('China Eastern');

-- Q2

INSERT INTO `airport` (`airport_name`, `city`) VALUES ('JFK', 'NYC');
INSERT INTO `airport` (`airport_name`, `city`) VALUES ('PVG', 'Shanghai');

-- Q3

INSERT INTO `customer` (`customer_email`, `name`, `password_`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES ('yl8060@nyu.edu', 'Ivana Li', 'abcde', '001', 'Century Avenue', 'Shanghai', 'China', '13074306199', '1234456', '2022-03-11', 'China', '2002-05-14');
INSERT INTO `customer` (`customer_email`, `name`, `password_`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES ('abc@nyu.edu', 'Thea Li', 'cdfgh', '002', 'Beautiful Street', 'NYC', 'US', '130425353', '12356767', '2022-03-12', 'US', '1999-08-21');

-- Q4

INSERT INTO `booking_agent` (`booking_agent_email`, `agent_password_`, `booking_agent_id`) VALUES ('hy98@gmail.com', 'fhbvghji876', '0000001');

-- Q5

INSERT INTO `airplane` (`airplane_id`, `airline_name`, `num_of_seat`) VALUES ('1101', 'China Eastern', '55');
INSERT INTO `airplane` (`airplane_id`, `airline_name`, `num_of_seat`) VALUES ('1109', 'China Eastern', '30');

-- Q6
INSERT INTO `airline_staff` (`username`, `airline_name`, `password_`, `first_name`, `last_name`, `date_of_birth`) VALUES ('imstaff', 'China Eastern', 'vghjkmnbvg', 'Ivanaaa', 'Liiii', '2002-05-30');
INSERT INTO `permission_status` (`username`, `status`) VALUES ('imstaff', 'Operator');


-- Q7
INSERT INTO `flight` (`flight_num`, `airline_name`, `departure_time`, `arrival_time`, `price`, `status_`, `airplane_id`, `departure_airport_name`, `arrival_airport_name`) VALUES ('001', 'China Eastern', '2022-3-1 19:00', '2022-3-2 20:00', '456', 'upcoming', '1109', 'JFK', 'PVG');
INSERT INTO `flight` (`flight_num`, `airline_name`, `departure_time`, `arrival_time`, `price`, `status_`, `airplane_id`, `departure_airport_name`, `arrival_airport_name`) VALUES ('002', 'China Eastern', '2022-3-5 19:00', '2022-3-9 20:00', '345', 'in-progress', '1109', 'PVG', 'JFK');
INSERT INTO `flight` (`flight_num`, `airline_name`, `departure_time`, `arrival_time`, `price`, `status_`, `airplane_id`, `departure_airport_name`, `arrival_airport_name`) VALUES ('003', 'China Eastern', '2022-5-1 19:00', '2022-5-2 20:00', '789', 'delayed', '1109', 'PVG', 'JFK');

-- Q8 with agent;

INSERT INTO `ticket` (`ticket_id`, `flight_num`, `airline_name`, `customer_email`, `booking_agent_email`) VALUES ('104', '1', 'China Eastern', 'abc@nyu.edu', 'hy98@gmail.com');

-- without agent;

INSERT INTO `ticket` (`ticket_id`, `flight_num`, `airline_name`, `customer_email`, `booking_agent_email`) VALUES ('105', '3', 'China Eastern', 'yl8060@nyu.edu', NULL);











