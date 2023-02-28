-- Q1
SELECT * FROM flight WHERE status_ = 'upcoming';
-- Result1:
-- 1	China Eastern	2022-3-1 19:00	2022-3-2 20:00	456	upcoming    1109	JFK	PVG


-- Q2
SELECT * FROM flight WHERE status_ = 'delayed';
-- R2:
-- 3	China Eastern	2022-5-1 19:00	2022-5-2 20:00	789	delayed	     1109	PVG	JFK	

-- Q3
SELECT c.name FROM customer as c, ticket as t WHERE c.customer_email = t.customer_email and t.booking_agent_email is NOT NULL;
-- R3:
-- Thea Li	

-- Q4
SELECT * FROM airplane WHERE airplane.airline_name = 'China Eastern';
-- R4:
-- 1101	China Eastern	55	
-- 1109	China Eastern	30	
