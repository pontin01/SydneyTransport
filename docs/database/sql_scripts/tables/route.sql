CREATE TABLE `Route` (
  `RouteID` varchar(50) NOT NULL,
  `AgencyID` varchar(50) DEFAULT NULL,
  `RouteShortName` varchar(50) DEFAULT NULL,
  `RouteLongName` varchar(255) DEFAULT NULL,
  `RouteDesc` varchar(255) DEFAULT NULL,
  `RouteType` int DEFAULT NULL,
  `RouteColour` varchar(50) DEFAULT NULL,
  `RouteTextColour` varchar(50) DEFAULT NULL,
  `ExactTimes` bit(1) DEFAULT NULL,
  PRIMARY KEY (`RouteID`),
  KEY `AgencyID` (`AgencyID`),
  CONSTRAINT `Route_ibfk_1` FOREIGN KEY (`AgencyID`) REFERENCES `Agency` (`AgencyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
