CREATE TABLE `ServiceDate` (
  `ServiceID` varchar(50) NOT NULL,
  `CalendarDate` date NOT NULL,
  `ExceptionType` tinyint NOT NULL,
  PRIMARY KEY (`ServiceID`,`CalendarDate`),
  CONSTRAINT `ServiceDate_ibfk_1` FOREIGN KEY (`ServiceID`) REFERENCES `Service` (`ServiceID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
