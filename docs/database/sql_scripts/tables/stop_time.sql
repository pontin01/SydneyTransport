CREATE TABLE `StopTime` (
  `TripID` varchar(50) NOT NULL,
  `ArrivalTime` time DEFAULT NULL,
  `DepartureTime` time DEFAULT NULL,
  `StopID` varchar(50) DEFAULT NULL,
  `StopSequence` smallint NOT NULL,
  `StopHeadsign` varchar(50) DEFAULT NULL,
  `Pickuptype` tinyint DEFAULT NULL,
  `DropOffType` tinyint DEFAULT NULL,
  `ShapeDistTraveled` double DEFAULT NULL,
  `Timepoint` bit(1) DEFAULT NULL,
  `StopNote` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`TripID`,`StopSequence`),
  KEY `StopID` (`StopID`),
  KEY `StopNote` (`StopNote`),
  CONSTRAINT `StopTime_ibfk_1` FOREIGN KEY (`TripID`) REFERENCES `Trip` (`TripID`),
  CONSTRAINT `StopTime_ibfk_2` FOREIGN KEY (`StopID`) REFERENCES `Stop` (`StopID`),
  CONSTRAINT `StopTime_ibfk_3` FOREIGN KEY (`StopNote`) REFERENCES `Note` (`NoteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
