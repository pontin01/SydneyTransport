CREATE TABLE `Stop` (
  `StopID` varchar(50) NOT NULL,
  `StopCode` int DEFAULT NULL,
  `StopName` varchar(255) DEFAULT NULL,
  `StopLat` double DEFAULT NULL,
  `StopLon` double DEFAULT NULL,
  `LocationType` int DEFAULT NULL,
  `ParentStation` varchar(50) DEFAULT NULL,
  `WheelchairBoarding` int DEFAULT NULL,
  `LevelID` varchar(50) DEFAULT NULL,
  `PlatformCode` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`StopID`),
  KEY `LevelID` (`LevelID`),
  KEY `StopName` (`StopName`,`StopID`),
  KEY `ParentStationIndex` (`ParentStation`,`LocationType`),
  CONSTRAINT `Stop_ibfk_1` FOREIGN KEY (`LevelID`) REFERENCES `Level` (`LevelID`),
  CONSTRAINT `Stop_ibfk_2` FOREIGN KEY (`ParentStation`) REFERENCES `Stop` (`StopID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
