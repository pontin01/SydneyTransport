CREATE TABLE `Service` (
  `ServiceID` varchar(50) NOT NULL,
  `Monday` bit(1) NOT NULL,
  `Tuesday` bit(1) NOT NULL,
  `Wednesday` bit(1) NOT NULL,
  `Thursday` bit(1) NOT NULL,
  `Friday` bit(1) NOT NULL,
  `Saturday` bit(1) NOT NULL,
  `Sunday` bit(1) NOT NULL,
  `StartDate` date NOT NULL,
  `EndDate` date NOT NULL,
  PRIMARY KEY (`ServiceID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
